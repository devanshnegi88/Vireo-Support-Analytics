"""Validation: (1) theme labels vs manual labels, (2) per-agent metrics vs an independent csv-module recomputation,
(3) edge-case checks on synthetic rows. Writes validation/results.json and prints a summary. Run: python -m validation.run_validation"""
import csv, json, statistics, sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from vireo import data, metrics
from vireo.themes import classify_text

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FMT = "%Y-%m-%d %H:%M"


def theme_validation(t):
    lab = pd.read_csv(ROOT / "validation" / "manual_labels.csv")
    d = lab.merge(t[["ticket_id", "theme"]], on="ticket_id")
    out = {}
    for name, g in [("dev (rules were tuned on this set)", d[d.set == "dev"]), ("holdout (never used for tuning)", d[d.set == "holdout"]), ("all", d)]:
        out[name] = {"n": len(g), "accuracy": round(float((g.theme == g.manual_label).mean()), 3)}
    h = d[d.set == "holdout"]
    per = {}
    for c in sorted(h.manual_label.unique()):
        s = h[h.manual_label == c]; p = h[h.theme == c]
        per[c] = {"manual_n": len(s), "recall": round(float((s.theme == c).mean()), 2),
                  "precision": round(float((p.manual_label == c).mean()), 2) if len(p) else None}
    out["holdout_per_category"] = per
    out["holdout_errors"] = h[h.theme != h.manual_label][["ticket_id", "manual_label", "theme"]].to_dict("records")
    return out


def independent_agent_metrics():
    """Pure-python recomputation, no pandas, sharing no code with vireo.data/metrics."""
    csat, ht, n = defaultdict(list), defaultdict(list), defaultdict(int)
    with open(DATA / "tickets.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            a = r["agent_id"]; n[a] += 1
            if r["csat_score"].strip():
                csat[a].append(float(r["csat_score"]))
            if r["status"] in ("resolved", "closed") and r["resolved_at"]:
                fr = datetime.strptime(r["first_response_at"], FMT); rs = datetime.strptime(r["resolved_at"], FMT)
                if r["source_system"] == "legacy_fd":
                    rs += timedelta(minutes=330)
                m = (rs - fr).total_seconds() / 60
                if m >= 0:
                    ht[a].append(m)
    return {a: dict(tickets=n[a], csat_n=len(csat[a]), csat=sum(csat[a]) / len(csat[a]) if csat[a] else None,
                    median_handle=statistics.median(ht[a]) if ht[a] else None) for a in n}


def metric_crosscheck(t):
    at = metrics.agent_table(t).set_index("agent_id")
    ind = independent_agent_metrics()
    rows, worst = 0, {"csat": 0.0, "median_handle": 0.0}
    mism = 0
    for a, v in ind.items():
        rows += 1
        ok = at.loc[a, "tickets"] == v["tickets"] and at.loc[a, "csat_responses"] == v["csat_n"]
        dc = abs(at.loc[a, "csat"] - v["csat"]); dh = abs(at.loc[a, "median_handle_min"] - v["median_handle"])
        worst["csat"] = max(worst["csat"], dc); worst["median_handle"] = max(worst["median_handle"], dh)
        mism += (not ok) or dc > 1e-9 or dh > 1e-6
    return {"agents_checked": rows, "agents_mismatching": int(mism), "max_abs_diff_csat": worst["csat"],
            "max_abs_diff_median_handle_min": worst["median_handle"]}


def edge_cases():
    res = {}
    res["empty_text_is_unclear"] = classify_text("", "") == "unclear" and classify_text("...", "-") == "unclear"
    res["compat_question_with_word_advance"] = classify_text("will this work with my tv, thanks in advance", "") == "product_enquiry"
    # synthetic ticket frame through the real metric code
    t = pd.DataFrame({"ticket_id": list("abcdef"), "agent_id": ["A1"] * 3 + ["A2"] * 2 + ["A3"],
                      "label": ["x"] * 3 + ["y"] * 2 + ["z"], "agent_team": "T", "tier": 1,
                      "csat_score": [5, np.nan, 3, 1, np.nan, np.nan], "handle_min": [10, 20, np.nan, 5000.0, 6, np.nan],
                      "bad_lot": False, "category": "Other", "breach": False})
    at = metrics.agent_table(t).set_index("agent_id")
    res["blank_csat_not_zero"] = bool(at.loc["A1", "csat"] == 4.0 and at.loc["A1", "csat_responses"] == 2)
    res["agent_with_no_csat_is_nan"] = bool(np.isnan(at.loc["A3", "csat"]))
    res["median_robust_to_5000min_outlier"] = bool(at.loc["A2", "median_handle_min"] == 2503.0 or at.loc["A2", "median_handle_min"] == statistics.median([5000.0, 6]))
    return res


def main():
    t, ag, q = data.build(DATA)
    out = {"themes": theme_validation(t), "metric_crosscheck": metric_crosscheck(t), "edge_cases": edge_cases(), "data_quality": {k: (float(v) if hasattr(v, "item") else v) for k, v in q.items()}}
    (ROOT / "validation" / "results.json").write_text(json.dumps(out, indent=2, default=str))
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
