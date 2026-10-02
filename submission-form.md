# Submission form: Vireo Audio support tickets

Note: no submission-form.md was in the supplied files, so this answers the questions listed in the brief.

**1. What did you build, and what business outcome does it move?**
A Streamlit dashboard (CSAT and handle time per agent, raw bottom ten, an adjusted "coaching priority" view, trends, issue themes) plus an analysis showing Pulse 2 earbuds from lots PL2-2510/2511/2512 drive a large part of the CSAT slide. Outcome metric: lot-linked excess replacements. Replacement tickets on those lots run at 42.3% of orders (838 of 1,979) against 6.5% on other Pulse 2 lots (166 of 2,542 orders). About 709 were avoidable at Rs 1,820 each (unit cost 1,480 + 340, policy section 5) = Rs 12.9 lakh total; Q1 2026 about 515 = Rs 9.4 lakh. Goal: from about 515 excess replacements a quarter to roughly zero, about Rs 9.4 lakh per quarter. Training will not move this number; the supplier/QC fix will. Support can move how early a bad lot is flagged.

**2. What does one run cost, and what would a month cost?**
Rs 0 per run: no API calls. Monthly volume: 650 tickets/week x 4.33 weeks = 2,814.5, about 2,815 tickets/month, classified locally by regex. Monthly cost Rs 0. For comparison, Finance's feared Rs 5 per ticket would be 2,815 x 5 = Rs 14,075 a month; we avoid it.

**3. How do you know it works?**
- Themes: 140 tickets hand-labelled against a 15-theme taxonomy (the labelling was done by Claude, not by a human reviewer at Vireo, so it is one labeller's judgement). Dev set 80 tickets: 93.8% (rules were tuned on it; first untuned pass was 67.5%). Fresh holdout 60 tickets, never used for tuning: 86.7% (52 of 60), about 13% error. Per-category results are in `validation/results.json`; the holdout has only 1 to 14 examples per category, so per-category figures are rough.
- Metrics: per-agent ticket count, CSAT, response count and median handle time recomputed with a separate pure-python csv implementation for all 44 agents: 0 mismatches. Caveat: I wrote both, so a shared misunderstanding (for example the UTC fix) would not be caught.
- 9 pytest tests plus edge cases: blank CSAT not zero, agent with no CSAT, 5,000-minute handle-time outlier, empty text, unknown agent handling, "advance" containing "anc".
- Known failure cases: firmware tickets mentioning "kept it in the case" classified as charging; "will the watch app run" read as app issue; typos like "debted"; wrong-colour cancel requests read as wrong item.

**4. Did you change, narrow, or push back on the client's ask?**
Yes. I delivered the raw bottom ten as asked, but added a coaching-priority view and recommend against using the raw list. Reason: 6 of the raw ten are Tier 2 warranty agents (policy says not to compare Tier 2 with Tier 1 on volume metrics) and 4 are the chat triage rota, which Neha flagged. After adjusting, only 5 agents are flagged (4 rota agents plus Jaspreet Desai), overlap with the raw ten is 5. I also did not run causes "later": the replacement finding comes first, because it changes where the budget should go. Handle time is shown, but compared within team only.

**5. What is wrong with what you are handing us?**
- The four chat rota agents are flagged even though Neha says they get the angriest customers. I could only test a crude anger-wording proxy (no difference found); unrecorded difficulty can still explain some or all of a 0.25 to 0.33 gap.
- Excess-replacement cost is a lower bound: 8% of tickets cannot be tied to a lot (933 customers have more than one order for the same SKU). 255 tickets are dated before their order date; I left them as they are. The Oct-Dec lot window was found from the data and a defect cause is not proven. The Q1 2026 share splits the all-time excess by ticket share, an approximation.
- The adjustment model is a plain OLS on survey responders only (44% respond); non-response bias is untested. Adjustment drops the Tier 2 team gap almost entirely because team is in the model, which means a whole weak team would be invisible there (team means are visible in the raw view).
- Theme classifier is 86.7% on 60 holdout tickets; the error bar is wide (about +/- 9 points). The "unclear" bucket is 387 tickets (3.3%).
- Duplicates: I found none (0 dropped), although policy section 9 warns of legacy re-imports; my duplicate keys may be too strict. Legacy refund amounts were not unit-converted because refund-to-price ratios look identical across systems (median 0.9).
- Festive window (Oct-Jan) is an assumption. No shift/site analysis was done. The dashboard has no authentication and loads CSVs from disk.
- "Hours" and the links below are placeholders I cannot fill.

**6. What did you deliberately leave out, and why?**
LLM classification (rules were enough and Finance said no per-ticket calls); 30-day repeat-contact costing; SLA breach credit costing (breach rate is 9.1%, shown per agent, credits not costed); refund reason-code audit (6 tickets have both refund and replacement, which policy section 5 forbids; not escalated); shift, site and tenure effects; forecasting. Priority was correct analysis, then the dashboard, then validation.

**7. Anything you built or found that nobody asked for?**
(a) The Pulse 2 lot finding and the Rs 1,820 vs Rs 2,500 replacement cost conflict: the average across all replacement tickets using unit cost + 340 is about Rs 1,802. (b) Legacy `resolved_at` is UTC: without the +5:30 shift, 2,309 legacy tickets have negative handle time. (c) The raw top five and adjusted top five share only two names, so the Diwali bonus should not use raw CSAT. (d) Six tickets carry both refund and replacement.

**8. What did you use AI for?**
Tool: Claude chat (claude.ai, Claude Sonnet 5.5) with a code sandbox. Purpose: data audit, finding the lot pattern, writing the code, tests, validation labels and docs. Helped: spotting the UTC bug, the lot analysis, and fast iteration on the classifier. Wasted time: the first classifier (67.5%) and a tone-proxy test that showed nothing. Discarded: per-ticket LLM classification; controlling for transfers and replacement flags; using Tier 1 agents as the benchmark for Tier 2. API cost: Rs 0 for the product. The chat subscription cost is not itemised here.

**9. Public Google Drive link**
[PLACEHOLDER: I could not create a Drive link. Upload the repo and memo, set to "anyone with the link", and paste it here.]

**10. Three things a developer needs to know**
1. Run: `pip install -r requirements.txt`, `streamlit run app.py`; validate with `python -m validation.run_validation` and `python -m pytest -q tests`. No env vars needed.
2. Logic lives in `vireo/data.py` (cleaning, lot join), `vireo/metrics.py` (adjustment, business case), `vireo/themes.py` (rules); constants such as the bad-lot regex and 40-response gate are in `vireo/config.py`. The bad-lot regex is hard-coded to the lots found in this data.
3. Join agents on `agent_id` only; legacy timestamps are UTC; blank CSAT is non-response. Manual labels are in `validation/manual_labels.csv`; if you change the rules, re-score on the holdout only once.

**11. Honest hours spent**
1-2 hours: data audit, lot finding, classifier rules, validation labels, business case, memo. 2-3 hours: dashboard and tests. 1 hour: final validation and docs. Total: 4-5 hours.

**12. GitHub repo link**
https://github.com/devanshnegi88/Vireo-Support-Analytics
