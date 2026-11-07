"""Benchmark slice: premature-lift rule, operator scorecard, validation section. Quickstart pack for speed."""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

import pandas as pd
import pytest

from fullload import premature, scorecard, validate
from fullload.config import data_root
from fullload.export import build_bundle, dumps
from fullload.figures import TAGS
from fullload.kit import open_dataset

PKG = Path(__file__).resolve().parents[1] / "fullload"


@pytest.fixture(scope="module")
def root() -> Path:
    return data_root("quickstart")


@pytest.fixture(scope="module")
def bundle() -> dict:
    return build_bundle("quickstart")


def test_sections_present_and_deterministic(bundle):
    for k in ("premature", "scorecard", "validation"):
        assert k in bundle
    again = build_bundle("quickstart")
    for k in ("premature", "scorecard", "validation"):
        assert dumps(bundle[k]) == dumps(again[k])
    json.loads(dumps(bundle))                       # valid JSON: no NaN / numpy types leak into the bundle
    assert "NaN" not in dumps(bundle)


def test_premature_figures(bundle):
    p = bundle["premature"]
    assert p["rule"]
    for k in ("flagged_lifts", "flagged_share_pct"):
        f = p[k]
        assert f["tag"] in TAGS and f["sources"] and f["formula"]
    assert 0 <= p["flagged_share_pct"]["value"] <= 100
    assert sum(r["flagged_lifts"] for r in p["by_policy"]) == p["flagged_lifts"]["value"]


def test_rule_never_flags_explained_triggers(root):
    f = premature.flag_lifts(open_dataset(root), include_requests=True)
    assert not f[f.original_trigger_type.isin(premature.EXPLAINED_TRIGGERS)].flagged.any()
    assert not f[f.at_min_frequency & (f.arm == "SCHEDULED_LOW_LOAD")].flagged.any()
    default = premature.flag_lifts(open_dataset(root))
    assert not (default.flagged & (default.arm == "PRE_CLOSURE_REQUEST")).any()


def test_thresholds_are_fixed_constants():
    assert premature.LOW_LOAD_SHARE == 0.40 and premature.LOW_FILL_PCT == 40
    assert premature.INCLUDE_PRE_CLOSURE_REQUESTS is False


def test_validation_scores_validation_split_only(bundle, root):
    v = bundle["validation"]
    assert v["split"] == "validation" and v["available"]
    man = json.loads((root / "metadata" / "dataset_manifest.json").read_text())["label_periods"]
    assert v["period"] == man["validation"]
    assert [r["model"] for r in v["premature"]] == list(validate.MODELS)
    for r in v["premature"]:
        if r["model"] == "kit_b4_ml" and r.get("unavailable"):
            continue                                # scikit-learn not installed: reported, not scored
        assert {"precision", "recall", "f1", "explained_flagged"} <= r.keys()
        assert 0 <= r["precision"] <= 1 and 0 <= r["recall"] <= 1 and r["explained_flagged"] >= 0
    src = (PKG / "validate.py").read_text()
    assert not re.search(r"labels_test|private_evaluation|\"test\"", src)


def test_rule_sees_no_rows_after_validation_end(root):
    end = validate._period(root)[1]
    con = open_dataset(root, as_of=end)
    f = premature.lift_features(con)
    cut = pd.Timestamp(end, tz="Europe/Helsinki")
    assert len(f) and (f.actual_at < cut).all()
    ids = set(premature.predictions(con).entity_id)
    assert ids <= set(f.collection_id)


def test_scorecard_rows_are_shares(bundle):
    sc = bundle["scorecard"]
    assert sc["rows"] and set(sc["definitions"]) >= set(scorecard.METRICS)
    keys = [(r["operator_id"], r["region_code"], r["month"]) for r in sc["rows"]]
    assert keys == sorted(keys) and len(keys) == len(set(keys))
    for r in sc["rows"]:
        for m in ("on_time_share", "missed_visit_share", "ticket_share", "discrepant_line_share"):
            assert r[m] is None or 0 <= r[m] <= 1
        assert r["tonnes_per_lift"] is None or r["tonnes_per_lift"] > 0
        assert r["ticket_lag_days_median"] is None or not math.isnan(r["ticket_lag_days_median"])


def test_product_modules_read_public_tables_only():
    for name in ("premature.py", "scorecard.py"):
        src = (PKG / name).read_text()
        assert not re.search(r"labels_|anomaly_labels|operator_scorecard|private_evaluation|truth", src), name
