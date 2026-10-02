"""Loading, cleaning and joining the Vireo exports. Every cleaning decision is counted in `quality`."""
from pathlib import Path
import numpy as np
import pandas as pd
from . import config as C
from .themes import classify_df


def load_raw(data_dir):
    d = Path(data_dir)
    t = pd.read_csv(d / "tickets.csv", parse_dates=["created_at", "first_response_at", "resolved_at"])
    return (t, pd.read_csv(d / "agents.csv"), pd.read_csv(d / "orders.csv", parse_dates=["order_date"]),
            pd.read_csv(d / "customers.csv"), pd.read_csv(d / "products.csv"))


def build(data_dir):
    t, agents, orders, customers, products = load_raw(data_dir)
    q = {"rows_raw": len(t)}
    # 1. duplicates (policy §9 warns of legacy re-imports): exact ticket_id or identical customer+created_at+message
    dup = t.duplicated("ticket_id", keep="first") | t.duplicated(["customer_id", "created_at", "customer_message"], keep="first")
    q["duplicate_tickets_dropped"] = int(dup.sum()); t = t[~dup].copy()
    # 2. legacy resolved_at is UTC -> shift to IST
    leg = t.source_system == "legacy_fd"
    t.loc[leg, "resolved_at"] += pd.Timedelta(minutes=C.LEGACY_UTC_OFFSET_MIN)
    q["legacy_resolved_at_shifted"] = int((leg & t.resolved_at.notna()).sum())
    # 3. handle time = first response -> resolution (§10), only resolved/closed tickets with a valid timestamp
    t["handle_min"] = (t.resolved_at - t.first_response_at).dt.total_seconds() / 60
    bad = t.handle_min < 0
    q["negative_handle_time_after_fix"] = int(bad.sum()); t.loc[bad, "handle_min"] = np.nan
    t.loc[~t.status.isin(["resolved", "closed"]), "handle_min"] = np.nan
    t["first_response_min"] = (t.first_response_at - t.created_at).dt.total_seconds() / 60
    t["breach"] = t.first_response_min > t.channel.map(C.FRT_TARGET_MIN)
    # 4. agents: join on agent_id only (two agents are both called Kavya Pandey)
    ag = agents.sort_values("from_date").drop_duplicates("agent_id", keep="last")
    ag["label"] = ag.name + " (" + ag.agent_id + ")"
    q["unknown_agent_ids"] = int((~t.agent_id.isin(ag.agent_id)).sum())
    t = t.merge(ag[["agent_id", "name", "label", "team", "tier", "shift", "site"]].rename(columns={"team": "agent_team"}),
                on="agent_id", how="left")
    # 5. order / lot join: direct on order_id, else customer+sku fallback only if exactly one such order
    t = t.merge(orders[["order_id", "order_date", "lot_code"]], on="order_id", how="left")
    fb = orders.groupby(["customer_id", "sku"]).agg(n=("order_id", "size"), lot_fb=("lot_code", "first"),
                                                     od_fb=("order_date", "first")).reset_index()
    t = t.merge(fb, left_on=["customer_id", "product_sku"], right_on=["customer_id", "sku"], how="left").drop(columns="sku")
    use_fb = t.lot_code.isna() & (t.n == 1)
    t["lot"] = t.lot_code.where(~use_fb, t.lot_fb); t["order_date"] = t.order_date.where(~use_fb, t.od_fb)
    t["lot_source"] = np.where(t.lot_code.notna(), "order_id", np.where(use_fb, "customer+sku", "unresolved"))
    q["lot_resolved_pct"] = round(100 * t.lot.notna().mean(), 1)
    q["lot_ambiguous_fallback"] = int((t.lot_code.isna() & (t.n > 1)).sum())
    t = t.drop(columns=["n", "lot_fb", "od_fb"])
    q["ticket_before_order_date"] = int((t.created_at < t.order_date).sum())
    # 6. other enrichment
    t = t.merge(products[["sku", "family", "unit_cost_inr", "product_name"]], left_on="product_sku", right_on="sku", how="left").drop(columns="sku")
    t = t.merge(customers[["customer_id", "care_plus"]], on="customer_id", how="left")
    t["bad_lot"] = t.lot.fillna("").str.match(C.BAD_LOT_REGEX)
    t["replacement"] = t.replacement_issued.eq("Y")
    t["month"] = t.created_at.dt.to_period("M").dt.to_timestamp()
    t["theme"] = classify_df(t)
    t["junk_text"] = t.customer_message.str.contains(r"\[inaudible\]|\[crosstalk\]|\[line dropped\]", regex=True) | ~t.customer_message.str.contains(r"[A-Za-z]{3}", regex=True)
    q.update(rows=len(t), missing_csat=int(t.csat_score.isna().sum()), missing_handle=int(t.handle_min.isna().sum()),
             missing_customer=int(t.care_plus.isna().sum()), junk_text=int(t.junk_text.sum()))
    return t, ag, q
