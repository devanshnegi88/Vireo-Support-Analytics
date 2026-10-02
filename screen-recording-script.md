# Screen recording script (target 2:55, no slides, one screen share)

Prep: `streamlit run app.py` open on tab 1; terminal ready in the repo; `validation/results.json` and README open in editor.

**0:00-0:20 | Problem.** "Priya asked for CSAT and handle time per agent and the bottom ten, to spend a Rs 4 lakh training budget. Two things in the email thread made me doubt that: Neha said the hardware triage rota gets the hard queue, and Arjun said replacements doubled since December."

**0:20-0:50 | Dashboard (tab 1).** Show tickets 11,750, CSAT 3.33, median handle 29 min, 44 agents. Read the banner: Pulse 2 lots made Oct-Dec 2025 have 42% replacements per order vs 6.5%; about 709 avoidable replacements x Rs 1,820 = Rs 12.9 lakh; Q1 2026 about Rs 9.4 lakh. Show the monthly CSAT line (3.50 to 2.95). Open Trends tab: replacements-per-order bar by lot.

**0:50-1:30 | Agents (tabs 2-3).** Sort the agent table; point out handle time is only comparable within a team. Go to Bottom 10: six Tier 2 plus the four-person chat rota. Then the Coaching Priority table: adjusted for issue type, channel, product, defective lot and team, shrunk for small samples. Five remain "Review recommended": the four chat rota agents and Jaspreet Desai. "Review recommended is a signal, not a verdict." Mention the two Kavya Pandeys.

**1:30-2:00 | Issue themes (tab 5).** Deterministic keyword taxonomy on customer message then agent note, no LLM, so a run costs Rs 0. Show CSAT and handle time by theme; charging and battery faults are the worst CSAT. State the 87% holdout accuracy honestly.

**2:00-2:25 | Validation.** Terminal: `python -m validation.run_validation` and `pytest`. Say: 140 hand-labelled tickets (labelled by Claude, not a human reviewer), 80 dev set 93.8% (tuned on it), 60 fresh holdout 86.7%. Per-agent CSAT and handle time recomputed independently: 44 of 44 agents match. Show 9 tests passing.

**2:25-2:45 | What changed / discarded.** Prompts: the brief pasted into Claude (Claude Sonnet 5.5 via claude.ai chat), then iterative prompts to fix the classifier. v1 classifier was 67.5% on the first sample; it matched "anc" inside "advance" and let refund words in the customer message override faults. Rewrote as two-stage rules. Discarded: LLM per-ticket classification (Finance said no per-ticket calls), controlling for transfers and replacement flags (agents influence them), and a tone score (no difference found).

**2:45-3:00 | Run and outcome.** Show README setup block: `python -m venv .venv`, `pip install -r requirements.txt`, `streamlit run app.py`. Close on the outcome: cut lot-linked excess replacements from about 515 a quarter to about zero, about Rs 9.4 lakh a quarter.
