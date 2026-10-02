"""Vireo Audio support analytics dashboard. Run: streamlit run app.py"""
import os
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from vireo import config as C, data, metrics

st.set_page_config(page_title="Vireo support analytics", layout="wide")
DATA_DIR = Path(os.environ.get("VIREO_DATA_DIR", "data"))


@st.cache_data(show_spinner="Loading and cleaning exports...")
def load():
    t, ag, q = data.build(DATA_DIR)
    orders = pd.read_csv(DATA_DIR / "orders.csv"); products = pd.read_csv(DATA_DIR / "products.csv")
    return t, q, orders, products


t, q, orders, products = load()
cp, tau2 = metrics.coaching_priority(t)
raw = metrics.raw_bottom(metrics.agent_table(t))
bc = metrics.business_case(t, orders, products)
inr = lambda x: f"Rs {x:,.0f}"

st.title("Vireo Audio - support performance and coaching priority")
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Executive summary", "Agent performance", "Bottom 10 vs coaching priority",
                                              "Trends", "Issue themes", "Data quality & method"])

with tab1:
    c = st.columns(5)
    c[0].metric("Tickets", f"{len(t):,}"); c[1].metric("Overall CSAT (responders only)", f"{t.csat_score.mean():.2f}")
    c[2].metric("Median handle time", f"{t.handle_min.median():.0f} min"); c[3].metric("Agents", t.agent_id.nunique())
    c[4].metric("Review-recommended agents", int((cp.signal == "Review recommended").sum()))
    st.info(f"**Biggest finding.** Pulse 2 earbuds made in Oct-Dec 2025 (lot codes PL2-2510/2511/2512) generate "
            f"{bc['bad_lot_replacements'] / bc['bad_lot_orders']:.0%} replacements per order versus {bc['base_replacement_rate']:.1%} for every other Pulse 2 lot. "
            f"That is about {bc['excess_replacements']:.0f} avoidable replacements x {inr(bc['cost_per_replacement'])} (unit cost {inr(bc['unit_cost'])} + Rs 340, policy section 5) = "
            f"{inr(bc['excess_cost_inr'])}. In Q1 2026 alone: about {bc['q1_2026_excess_replacements']:.0f} excess replacements = {inr(bc['q1_2026_excess_cost_inr'])}. "
            "Estimates are lower bounds: 8% of tickets cannot be tied to a lot.")
    m = metrics.monthly(t)
    c1, c2 = st.columns(2)
    c1.plotly_chart(px.line(m, x="month", y="csat", markers=True, title="Monthly CSAT"), width="stretch")
    c2.plotly_chart(px.line(m, x="month", y="median_handle_min", markers=True, title="Monthly median handle time (min)"), width="stretch")

with tab2:
    teams = st.multiselect("Team", sorted(cp.agent_team.unique()), default=sorted(cp.agent_team.unique()))
    sort = st.selectbox("Sort by", ["csat", "adj_resid", "tickets", "median_handle_min", "handle_vs_team_median"])
    v = cp[cp.agent_team.isin(teams)].sort_values(sort)
    cols = ["label", "agent_team", "tickets", "csat_responses", "csat", "csat_vs_team", "median_handle_min", "handle_vs_team_median",
            "bad_lot_share", "adj_resid", "se", "signal"]
    st.dataframe(v[cols].round(2), width="stretch", hide_index=True)
    st.caption("CSAT excludes blank (non-response) scores. Handle time = first response to resolution, legacy timestamps shifted UTC->IST. "
               "Handle time is dominated by team: Tier 2, Logistics and Returns work multi-day cases, so compare within team only (policy section 6).")
    pick = st.selectbox("Agent monthly trend", v.label.tolist())
    aid = v.loc[v.label == pick, "agent_id"].iloc[0]
    am = t[t.agent_id == aid].groupby("month").agg(csat=("csat_score", "mean"), n=("csat_score", "count")).reset_index()
    st.plotly_chart(px.line(am, x="month", y="csat", markers=True, hover_data=["n"], title=f"{pick}: monthly CSAT (n responses in hover; thin months are noisy)"), width="stretch")

with tab3:
    st.subheader("A. What was asked: bottom 10 by raw CSAT")
    st.dataframe(raw[["raw_rank", "label", "agent_team", "csat_responses", "csat", "bad_lot_share", "hard_fault_share"]].round(2), hide_index=True, width="stretch")
    st.warning(f"{int((raw.agent_team == 'Escalations & Warranty').sum())} of these 10 are the Tier 2 Escalations & Warranty team and "
               f"{int((raw.agent_team == 'Chat Frontline').sum())} are the four-person hardware triage rota in Chat Frontline. "
               "These queues get the defective Pulse 2 lots and warranty cases; raw CSAT mostly measures the queue.")
    st.subheader("B. Coaching priority (adjusted for ticket context, compared with team peers, shrunk for small samples)")
    show = cp.sort_values("shrunk_resid").head(12)
    st.dataframe(show[["coaching_rank", "label", "agent_team", "csat_responses", "csat", "expected_csat", "adj_resid", "ci90_lo", "ci90_hi", "shrunk_resid", "signal"]].round(2), hide_index=True, width="stretch")
    ov = set(raw.agent_id) & set(cp.head(10).agent_id)
    st.caption(f"Overlap between list A and the top 10 of list B: {len(ov)} agents. 'Review recommended' = adjusted gap of at least 0.15 CSAT points, "
               f"the 90% interval entirely below zero, and at least {C.MIN_CSAT_RESPONSES} survey responses. This is a performance signal, not a verdict: "
               "unobserved queue difficulty can still explain part of any gap.")
    fig = px.scatter(cp, x="csat", y="adj_resid", color="agent_team", hover_name="label", size="csat_responses",
                     title="Raw CSAT vs adjusted gap (each dot = one agent)")
    st.plotly_chart(fig, width="stretch")

with tab4:
    m = metrics.monthly(t)
    st.plotly_chart(px.bar(m, x="month", y="tickets", title="Ticket volume"), width="stretch")
    st.plotly_chart(px.bar(m, x="month", y="replacements", title="Replacements issued per month"), width="stretch")
    lot = metrics.lot_analysis(t, orders)
    st.plotly_chart(px.bar(lot, x="lot_month", y="replacements_per_order", title="Pulse 2: replacement tickets per order, by lot (YYMM)"), width="stretch")
    t["period"] = pd.cut(t.created_at, [pd.Timestamp("2000-01-01"), pd.Timestamp(C.FESTIVE_START), pd.Timestamp(C.FESTIVE_END) + pd.Timedelta(days=1), pd.Timestamp("2100-01-01")],
                         labels=["pre-festive", "festive (Oct-Jan)", "post-festive (Feb-Jun)"])
    p = t.groupby("period", observed=True).agg(tickets=("ticket_id", "size"), csat=("csat_score", "mean"), median_handle=("handle_min", "median"),
                                              replacement_rate=("replacement", "mean")).round(3)
    ex = t[~t.bad_lot].groupby("period", observed=True).csat_score.mean().round(3).rename("csat_excluding_bad_lot_tickets")
    st.dataframe(p.join(ex)); st.caption("Festive window is an assumption (Oct 2025 - Jan 2026), editable in vireo/config.py.")

with tab5:
    th = t.groupby("theme").agg(tickets=("ticket_id", "size"), csat=("csat_score", "mean"), median_handle_min=("handle_min", "median"),
                                replacement_rate=("replacement", "mean"), refund_inr=("refund_amount_inr", "sum")).reset_index()
    th["est_replacement_cost_inr"] = [ (t[(t.theme == x) & t.replacement].unit_cost_inr + C.REPLACEMENT_LOGISTICS_INR).sum() for x in th.theme]
    st.dataframe(th.sort_values("tickets", ascending=False).round(2), hide_index=True, width="stretch")
    st.plotly_chart(px.bar(th.sort_values("csat"), x="theme", y="csat", title="CSAT by theme"), width="stretch")
    st.caption("Themes come from a deterministic keyword taxonomy (vireo/themes.py), not an LLM. Accuracy on a hand-labelled holdout is in validation/results.json.")

with tab6:
    st.json({k: (float(v) if hasattr(v, "item") else v) for k, v in q.items()})
    st.markdown(f"**Method.** Adjusted gap = mean of (actual CSAT - expected CSAT) per agent, where expected comes from an OLS on category, priority, channel, product family, "
                f"defective-lot flag and team. Transfers and replacement flags are deliberately NOT controlled for (agents influence them). Shrinkage: empirical Bayes, tau^2 = {tau2:.4f}.")
