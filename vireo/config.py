"""Constants. Policy figures come from support-policy.pdf v3.2 (sections cited)."""
LEGACY_UTC_OFFSET_MIN = 330          # §9: legacy resolved_at stored in UTC; helpdesk shows IST (UTC+5:30)
FRT_TARGET_MIN = {"chat": 15, "voice": 120, "social": 240, "email": 480}   # §3
SLA_CREDIT_INR = 350                 # §3
REPLACEMENT_LOGISTICS_INR = 340      # §5: unit cost (products.csv) + 340
MIN_CSAT_RESPONSES = 40              # below this an agent is never flagged "review recommended"
HARD_FAULT_CATEGORIES = ["Charging & Battery", "Warranty & Repair", "Audio Quality", "Connectivity"]
BAD_LOT_SKU = "VA-EB-PL2"
BAD_LOT_REGEX = r"^PL2-25(10|11|12)-"   # lots made Oct-Dec 2025; found by lot_analysis() in metrics.py
FESTIVE_START, FESTIVE_END = "2025-10-01", "2026-01-31"   # assumption: Diwali run-up through Jan
