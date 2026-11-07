"""Scores against labels_dev, VALIDATION split only (PRODUCT.md §7.2). The only product module that reads labels.

1. Task B, family PREMATURE_UNJUSTIFIED: the FullLoad rule (`premature.py`) vs the kit's rules baseline (B2,
   `b2_rules_anomaly.detect_collections`) vs the kit's ML baseline (B4, `b4_ml_models.task_b`, trained on TRAIN-period
   labels exactly as the kit's `run_all.py` does). All three are scored by the kit's own `evaluate.score_b` on the
   validation split, so they are scored on the same label rows with the same metric definitions. Precision, recall,
   F1 and explained cases flagged (EARLY_JUSTIFIED traps) are the kit's numbers.
2. Task B2: the FullLoad scorecard (`scorecard.py`) vs `labels_dev/operator_scorecard` with the kit's
   `evaluate.score_b2`, validation months only; kit B5 on the same rows for reference.

Leakage guards:
  * the split must exist in the package manifest (the kit scorer silently scores everything otherwise);
  * the FullLoad rule runs on the kit's leak-free `as_of` view at the END of the validation period, so it sees no
    test-period rows; the kit baselines run as the kit runs them (full public package), which is what BENCHMARK.md
    reports;
  * nothing here reads the organisers' private folder or the held-out final period; only SPLIT is scored.

One command reproduces the numbers:  fullload build  (or: python -m fullload.validate [competition|quickstart]).
"""
from __future__ import annotations

import functools
import json
import math
import sys
from pathlib import Path

import pandas as pd

from . import premature, scorecard
from .config import data_root
from .kit import baseline, open_dataset

SPLIT = "validation"
FAMILY = premature.FAMILY
MODELS = ("fullload_rule", "kit_b2_rules", "kit_b4_ml")


def _evaluate():
    return baseline("europress_data.evaluate")          # the kit's scorer, imported through the kit adapter


def _labels_dir(root: Path) -> Path:
    return root / "labels_dev"


def _period(root: Path) -> tuple[str, str] | None:
    """The validation period [start, end) from the package manifest, or None if the package has none."""
    periods = json.loads((root / "metadata" / "dataset_manifest.json").read_text(encoding="utf-8"))["label_periods"]
    if SPLIT not in periods:
        return None
    a, b = periods[SPLIT]
    return a, b


@functools.cache
def _kit_features(root: Path) -> pd.DataFrame:
    b1, _ = baseline("b1_economic_calculator").compute(root)
    return baseline("b2_rules_anomaly").collection_features(root, b1)


def _kit_b2(root: Path) -> pd.DataFrame:
    return baseline("b2_rules_anomaly").detect_collections(_kit_features(root))


def _kit_b4(root: Path) -> pd.DataFrame:
    """B4 trained on train-period labels and train-period lifts, as in the kit's run_all.py (validation column)."""
    ev, ml, f = _evaluate(), baseline("b4_ml_models"), _kit_features(root)
    dev = _labels_dir(root)
    lab = pd.read_parquet(dev / "anomaly_labels.parquet")
    lab_tr = ev._period_filter(lab, dev, "train", "eval_at")
    train_end = json.loads((root / "metadata" / "dataset_manifest.json").read_text(encoding="utf-8"))["label_periods"]["train"][1]
    t = f.collection_id.map(ev._entity_times(dev).set_index("entity_id").eval_at)
    t = t.dt.tz_convert("Europe/Helsinki").dt.tz_localize(None)
    return ml.task_b(f[t < pd.Timestamp(train_end)], lab_tr, f)


def _score(pred: pd.DataFrame, root: Path) -> dict:
    pred = pred[pred.label_family == FAMILY]
    r = _evaluate().score_b(pred, _labels_dir(root), SPLIT)[FAMILY]
    return {"positives": r["positives"], "predicted": r["predicted"], "tp": r["tp"], "precision": r["precision"],
            "recall": r["recall"], "f1": r["f1"], "explained_flagged": r["explained_flagged_as_anomaly"],
            "value_weighted_recall": r["value_weighted_recall"]}


def premature_validation(root: Path, end: str) -> tuple[list[dict], dict]:
    con = open_dataset(root, as_of=end)          # leak-free view: nothing at or after the validation end
    try:
        ours = premature.predictions(con)
        variant = premature.predictions(con, include_requests=True)
    finally:
        con.close()
    try:
        b4 = _score(_kit_b4(root), root)
    except ImportError as e:      # kit B4 needs scikit-learn (the kit's [dev] extra); never break the build over it
        b4 = {k: None for k in ("positives", "predicted", "tp", "precision", "recall", "f1", "explained_flagged",
                                "value_weighted_recall")} | {"unavailable": f"{e.name or e} not installed"}
    rows = [{"model": "fullload_rule", **_score(ours, root)},
            {"model": "kit_b2_rules", **_score(_kit_b2(root), root)},
            {"model": "kit_b4_ml", **b4}]
    return rows, {"model": "fullload_rule_with_pre_closure_requests", **_score(variant, root)}


def _clean(v):
    return None if v is None or (isinstance(v, float) and math.isnan(v)) else v


def _b2_result(pred: pd.DataFrame, root: Path, metrics: dict[str, str]) -> dict:
    r = {k: _clean(v) for k, v in _evaluate().score_b2(pred, _labels_dir(root), SPLIT).items()}
    per = {ours: r.get(f"{kit}:score") for ours, kit in metrics.items()}
    covered = [v for v in per.values() if v is not None]
    return {"rows": r["n_rows"], "overall": r["scorecard_score_0_100"], "per_metric": per,
            "overall_covered_metrics": round(100 * sum(covered) / len(covered), 2) if covered else None,
            "rank_corr": {ours: r.get(f"{kit}:mean_rank_corr") for ours, kit in metrics.items()}}


def scorecard_validation(root: Path) -> dict:
    con = open_dataset(root)
    try:
        sc = scorecard.scorecard(con, root)
    finally:
        con.close()
    ours = _b2_result(sc.rename(columns=scorecard.KIT_METRIC), root, scorecard.KIT_METRIC)
    b1, b1l = baseline("b1_economic_calculator").compute(root)
    b5 = baseline("b5_operator_scorecard").scorecard(root, b1, b1l)
    ours["kit_b5_same_metrics"] = _b2_result(b5[["operator_id", "region_code", "month", *scorecard.KIT_METRIC.values()]],
                                             root, scorecard.KIT_METRIC)
    ours["note"] = ("overall = the kit's 0-100 score over all 9 Task B2 metrics; metrics we do not produce "
                    "(over/undercharge %, weight bias, order-to-lift) score 0 there. overall_covered_metrics = "
                    "mean over the 5 metrics we produce.")
    return ours


def validation_facts(root: Path) -> dict:
    period = _period(root)
    if period is None:
        return {"split": SPLIT, "available": False, "premature": [], "scorecard_b2": None}
    rows, variant = premature_validation(root, period[1])
    return {"split": SPLIT, "available": True, "period": list(period), "family": FAMILY,
            "premature": rows, "premature_variant": variant, "scorecard_b2": scorecard_validation(root),
            "method": ("Kit scorer europress_data.evaluate (score_b, score_b2), validation split. FullLoad rule on the "
                       "as-of view at the validation end; kit B2 rules and B4 gradient boosting as run by the kit "
                       "(B4 trained on train-period labels).")}


if __name__ == "__main__":
    print(json.dumps(validation_facts(data_root(sys.argv[1] if len(sys.argv) > 1 else None)), indent=2))
