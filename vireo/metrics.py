"""Agent metrics, case-mix adjustment, coaching priority and the business case. All numbers computed here."""
import numpy as np
import pandas as pd
from . import config as C

Z90 = 1.645


def agent_table(t):
    """Raw per-agent view (CSAT excludes blank = non-response, §8)."""
    g = t.groupby(["agent_id", "label", "agent_team", "tier"])
    out = g.agg(tickets=("ticket_id", "size"), csat_responses=("csat_score", "count"), csat=("csat_score", "mean"),
                median_handle_min=("handle_min", "median"), mean_handle_min=("handle_min", "mean"),
                bad_lot_share=("bad_lot", "mean"), hard_fault_share=("category", lambda s: s.isin(C.HARD_FAULT_CATEGORIES).mean()),
                breach_rate=("breach", "mean")).reset_index()
    team_h = out.groupby("agent_team").median_handle_min.transform("median")
    out["handle_vs_team_median"] = out.median_handle_min / team_h
    out["team_avg_csat"] = t.groupby("agent_team").csat_score.mean().reindex(out.agent_team).values
    out["csat_vs_team"] = out.csat - out.team_avg_csat
    out["csat_vs_company"] = out.csat - t.csat_score.mean()
    return out


def raw_bottom(at, n=10, min_responses=1):
    return at[at.csat_responses >= min_responses].sort_values("csat").head(n).assign(raw_rank=lambda d: range(1, len(d) + 1))


def adjust(t, controls=("category", "priority", "channel", "family", "bad_lot", "agent_team")):
    """OLS of CSAT on ticket context the agent does NOT control. Transfers and replacement flags are excluded
    on purpose (agent-influenced). Returns per-agent residual, SE, empirical-Bayes shrunk residual."""
    d = t[t.csat_score.notna()].copy()
    d["bad_lot"] = d.bad_lot.astype(int)
    X = pd.get_dummies(d[list(controls)], drop_first=True).astype(float)
    X.insert(0, "const", 1.0)
    beta, *_ = np.linalg.lstsq(X.values, d.csat_score.values, rcond=None)
    d["expected"] = X.values @ beta
    d["resid"] = d.csat_score - d.expected
    s = d.groupby("agent_id").agg(adj_resid=("resid", "mean"), resid_sd=("resid", "std"), n=("resid", "size"),
                                  expected_csat=("expected", "mean")).reset_index()
    s["se"] = s.resid_sd / np.sqrt(s.n)
    # method-of-moments between-agent variance (tau^2) -> shrinkage weight
    tau2 = max(s.adj_resid.var(ddof=1) - (s.se ** 2).mean(), 1e-6)
    s["shrunk_resid"] = s.adj_resid * tau2 / (tau2 + s.se ** 2)
    s["ci90_hi"] = s.adj_resid + Z90 * s.se
    s["ci90_lo"] = s.adj_resid - Z90 * s.se
    s.attrs["tau2"] = tau2
    return s


def coaching_priority(t, controls=("category", "priority", "channel", "family", "bad_lot", "agent_team")):
    at = agent_table(t)
    adj = adjust(t, controls)
    m = at.merge(adj[["agent_id", "adj_resid", "se", "shrunk_resid", "ci90_lo", "ci90_hi", "expected_csat"]], on="agent_id")
    def flag(r):
        if r.csat_responses < C.MIN_CSAT_RESPONSES:
            return "Too few survey responses"
        if r.ci90_hi < 0 and r.adj_resid <= -0.15:
            return "Review recommended"
        if r.adj_resid <= -0.10:
            return "Watch"
        return "No signal"
    m["signal"] = m.apply(flag, axis=1)
    m["coaching_rank"] = m.shrunk_resid.rank(method="first").astype(int)
    return m.sort_values("shrunk_resid"), adj.attrs["tau2"]


def monthly(t):
    return t.groupby("month").agg(tickets=("ticket_id", "size"), csat=("csat_score", "mean"), csat_n=("csat_score", "count"),
                                  median_handle_min=("handle_min", "median"), replacements=("replacement", "sum")).reset_index()


def lot_analysis(t, orders, sku=C.BAD_LOT_SKU):
    """Replacement tickets per order, by manufacturing-lot month, for one SKU."""
    o = orders[orders.sku == sku].assign(lot_month=lambda d: d.lot_code.str.split("-").str[1])
    tk = t[(t.product_sku == sku) & t.lot.notna()].assign(lot_month=lambda d: d.lot.str.split("-").str[1])
    r = tk.groupby("lot_month").agg(tickets=("ticket_id", "size"), replacements=("replacement", "sum"), csat=("csat_score", "mean"))
    r = r.join(o.groupby("lot_month").size().rename("orders"))
    r["replacements_per_order"] = r.replacements / r.orders
    return r.reset_index()


def business_case(t, orders, products):
    """Excess replacement cost from the defective Pulse 2 lots. Cost per replacement = unit cost + Rs 340 (policy §5)."""
    unit = products.set_index("sku").unit_cost_inr[C.BAD_LOT_SKU]
    cost = unit + C.REPLACEMENT_LOGISTICS_INR
    o = orders[orders.sku == C.BAD_LOT_SKU].copy()
    o["bad"] = o.lot_code.str.match(C.BAD_LOT_REGEX)
    base_orders = int((~o.bad).sum()); bad_orders = int(o.bad.sum())
    tk = t[(t.product_sku == C.BAD_LOT_SKU) & t.lot.notna() & t.replacement]
    base_rep = int((~tk.bad_lot).sum()); bad_rep = int(tk.bad_lot.sum())
    base_rate = base_rep / base_orders
    expected_bad = base_rate * bad_orders
    excess = bad_rep - expected_bad
    q1 = tk[tk.bad_lot & (tk.created_at >= "2026-01-01") & (tk.created_at < "2026-04-01")]
    q1_share = len(q1) / bad_rep
    q1_excess = excess * q1_share
    all_repl_q1 = int(t[(t.created_at >= "2026-01-01") & (t.created_at < "2026-04-01")].replacement.sum())
    return dict(unit_cost=int(unit), cost_per_replacement=int(cost), bad_lot_orders=bad_orders, base_orders=base_orders,
                bad_lot_replacements=bad_rep, base_replacement_rate=base_rate, expected_if_normal=expected_bad,
                excess_replacements=excess, excess_cost_inr=excess * cost, bad_lot_replacements_q1_2026=len(q1),
                q1_2026_excess_replacements=q1_excess, q1_2026_excess_cost_inr=q1_excess * cost,
                q1_2026_all_replacements=all_repl_q1, q1_share_of_bad_lot=q1_share)
