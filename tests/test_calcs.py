import sys
from pathlib import Path
import numpy as np, pandas as pd, pytest
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from vireo import data, metrics
from vireo.themes import classify_text

DATA = Path(__file__).resolve().parent.parent / "data"


@pytest.fixture(scope="module")
def built():
    return data.build(DATA)


def test_blank_csat_excluded_not_zero():
    t = pd.DataFrame({"ticket_id": list("abc"), "agent_id": "A", "label": "A", "agent_team": "T", "tier": 1,
                      "csat_score": [5, np.nan, 3], "handle_min": [1, 2, 3], "bad_lot": False, "category": "x", "breach": False})
    at = metrics.agent_table(t)
    assert at.csat.iloc[0] == 4.0 and at.csat_responses.iloc[0] == 2


def test_legacy_timestamps_fixed_no_negative_handle_time(built):
    t, _, q = built
    assert (t.handle_min.dropna() >= 0).all()
    assert q["legacy_resolved_at_shifted"] > 3000


def test_join_on_agent_id_not_name(built):
    t, ag, _ = built
    assert ag.name.duplicated().sum() == 1            # two 'Kavya Pandey'
    assert t.agent_id.nunique() == 44 and t.label.nunique() == 44


def test_ticket_count_preserved(built):
    t, _, q = built
    assert len(t) == q["rows_raw"] - q["duplicate_tickets_dropped"]


def test_small_samples_never_flagged(built):
    t, _ = metrics.coaching_priority(built[0])
    low = t[t.csat_responses < 40]
    assert (low.signal == "Too few survey responses").all()


def test_shrinkage_pulls_toward_zero(built):
    t, _ = metrics.coaching_priority(built[0])
    assert (t.shrunk_resid.abs() <= t.adj_resid.abs() + 1e-12).all()


def test_empty_text_unclear():
    assert classify_text("", "") == "unclear" and classify_text("-", "...") == "unclear"


def test_advance_not_mistaken_for_anc():
    assert classify_text("will it work with my tv, thanks in advance", "") == "product_enquiry"


def test_business_case_uses_policy_cost(built):
    t, *_ = built
    o = pd.read_csv(DATA / "orders.csv"); p = pd.read_csv(DATA / "products.csv")
    bc = metrics.business_case(t, o, p)
    assert bc["cost_per_replacement"] == 1480 + 340
    assert bc["excess_replacements"] > 0
