# Requirements summary and decisions

**Ask:** CSAT and handle time per agent, bottom ten flagged, Rs 4 lakh Q3 training budget; top five get Diwali bonus (email 7 Sep).
**Data:** 11,750 tickets, 1 Jan 2025 to 30 Jun 2026, 44 agents (all ids resolve; two share a name), 9,500 customers, 15,500 orders, 14 SKUs. CSAT present on 5,196 tickets (44.2%).
**Traps found:** legacy resolved_at is UTC (2,309 negative handle times unfixed); Tier 2 not comparable with Tier 1 (policy section 6); hardware triage rota (Neha); replacement spike (Arjun/Priya) traced to Pulse 2 lots made Oct-Dec 2025 via orders.csv lot codes, the file the client said to ignore; Rs 2,500 replacement cost conflicts with policy (unit cost + 340); a handful of junk IVR transcripts (27 flagged).
**Decisions:** blank CSAT excluded; handle time = first response to resolution (policy section 10); compare within team; adjust CSAT for context the agent does not control; shrink small samples; minimum 40 responses before any flag; no LLM; business case uses policy cost (Rs 1,820 for Pulse 2).
**Ambiguities:** festive window (Oct-Jan assumed); which orders belong to a ticket with no order_id (customer+SKU only if unique); duplicates (none found by exact keys).
