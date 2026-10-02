"""Deterministic issue-theme classifier (regex taxonomy built from the supplied tickets). No LLM / API calls.

Two stages: (1) rules run on the customer's message; (2) if nothing matches, the same rules run on the agent's
closing note. Customer text goes first because notes describe the *resolution* (refund, replacement, 'reverse pkp')
and would otherwise steal fault tickets. First matching rule wins, so order matters. Text with no letters -> 'unclear'.
"""
import re
import pandas as pd

RULES = [
    ("product_enquiry", r"compatib|spec sheet|pre-?sales|before i buy|will (this|it) (survive|work|run|talk)|water ?resist|waterproof|shower|enquiry|inquiry|query answered"),
    ("wrong_or_damaged_item", r"damaged|transit damage|crushed|cracked|wrong (item|product|colou?r|variant)|different colou?r|incorrect product|dead on arrival"),
    ("payment_issue", r"card charged|double charg|duplicate (txn|charge|payment)|charged two times|payment (debited|failed|deducted|went)|money debited|amount deducted|debited|failed (ord|after)|no order|without order|pg dashboard|\butr\b|coupon|promo|price adj|discount|bank says|nothing shows in my account"),
    ("address_change", r"address (change|update|chagne|chnge)|addrses|wrong pincode|pincode|pin code|flat number|moved house|old flat|delivery address|edit(ing)? (the )?address"),
    ("order_cancellation", r"cancel|change of mind|stop the shipment|ordered (this )?by mistake|without asking|please reverse"),
    ("warranty_status_followup", r"warranty (claim|cl\w*m|status)|rma status|\brma ?\d|service cent|\brepair|claim pending|claim number"),
    ("return_refund_pickup", r"pick ?up|pikup|\bpkp\b|reverse p|refund (pending|status|delay|was promised)|still waiting for (my )?refund|promised (a )?refund|money (has|hasn)|rfnd status|\barn\b|return"),
    ("delivery_not_received", r"not delivered|not rcvd|not received|tracking|\bawb\b|courier|\brto\b|lost in transit|shipment|delivery delayed|undelivered|nothing in hand|waiting for something to show up|package|has not been delivered"),
    ("display_touch_defect", r"touch ?screen|display (is|not|dead|flick)|screen (lights|is|not)|unresponsive|\bdial\b|strap"),
    ("charging_battery_fault", r"not charg|no charg|stopp\w* charg|taking charge|take charge|won'?t charge|wont charge|battery|drain|charging case|plugging in|charge it twice|\d+ ?percent|in the case|pin cleaning|charging pin|stays flat|paperweight|\bdoa\b|charged for \d|case led"),
    ("connectivity_pairing", r"pair|bluetooth|\bbt\b|discoverable|dropout|disconnect|reconnect|stutter|pocket|silent for a|every few minutes|see it in the list|doesn'?t see it"),
    ("audio_quality", r"no sound|sound|audio|\bmic\b|microphone|hear me|crackl|static|volume|bass|distort|noise|\banc\b|silent|decoration|one side|one of them"),
    ("invoice_issue", r"invoice|\bgst\b"),
    ("app_firmware", r"firmware|\bfw\b|\bapp\b|update|login|log in|otp|password|account|went dark"),
]
_COMPILED = [(n, re.compile(p)) for n, p in RULES]
THEMES = [n for n, _ in RULES] + ["unclear"]


def _match(text):
    for name, rx in _COMPILED:
        if rx.search(text):
            return name
    return None


def classify_text(customer_message, agent_notes):
    msg, note = str(customer_message or "").lower(), str(agent_notes or "").lower()
    if not re.search(r"[a-z]{3}", msg + " " + note):
        return "unclear"
    return _match(msg) or _match(note) or "unclear"


def classify_df(df):
    return pd.Series([classify_text(m, n) for m, n in zip(df["customer_message"].fillna(""), df["agent_notes"].fillna(""))],
                     index=df.index, name="theme")
