"""Scores against labels_dev, VALIDATION split only (PRODUCT.md §7.2). The only product module that reads labels.

1. Task B, family PREMATURE_UNJUSTIFIED: the FullLoad rule (`premature.py`) vs the kit's rules baseline (B2,
   `b2_rules_anomaly.detect_collections`) vs the kit's ML baseline (B4, `b4_ml_models.task_b`, trained on TRAIN-period
   labels exactly as the kit's `run_all.py` does). All three are scored by the kit's own `evaluate.score_b` on the
   validation split, so they are scored on the same label rows with the same metric definitions. Precision, recall,
   F1 and explained cases flagged (EARLY_JUSTIFIED traps) are the kit's numbers.
2. Task B2: the FullLoad scorecard (`scorecard.py`) vs `labels_dev/operator_scorecard` with the kit's
   `evaluate.score_b2`, validation months only; kit B5 on the same rows for reference.
3. Economics check: "today's price" in the market model is the invoiced amount. Per collection (joined by
   operator_job_ref), invoiced totals vs the contract-expected amount in `labels_dev/reference_economics`, plus how
   constant the contract collection cost per lift is (the market model scales trip costs with the number of lifts).
4. Trips check: lifts the trips model removes vs lifts labelled PREMATURE_UNJUSTIFIED, per device, validation period.

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


def economics_check(root: Path, period: tuple[str, str]) -> dict:
    from .fleet import TONNE_LINES, TRIP_LINES, _in
    a, b = period
    con = open_dataset(root)
    ref = f"read_parquet('{_labels_dir(root) / 'reference_economics.parquet'}')"
    n, inv_total, exp_total, exact, inv_tendered, ref_tendered = con.execute(f"""
        WITH r AS (SELECT * FROM {ref} WHERE service_date >= DATE '{a}' AND service_date < DATE '{b}'),
             l AS (SELECT operator_job_ref, sum(amount_eur) AS total,
                          sum(amount_eur) FILTER (WHERE line_type IN {_in(TRIP_LINES + TONNE_LINES)}) AS tendered
                   FROM invoice_lines GROUP BY 1)
        SELECT count(*), sum(l.total), sum(r.expected_invoice_amount_eur),
               avg(CASE WHEN abs(l.total - r.expected_invoice_amount_eur) <= 0.01 THEN 1.0 ELSE 0.0 END),
               sum(l.tendered), sum(r.collection_cost_eur + r.processing_cost_eur)
        FROM r JOIN collection_events c USING (collection_id) JOIN l USING (operator_job_ref)""").fetchone()
    cv = con.execute(f"""
        SELECT median(cv), quantile_cont(cv, 0.9) FROM (
          SELECT device_id, stddev_samp(collection_cost_eur) / nullif(avg(collection_cost_eur), 0) AS cv
          FROM {ref} WHERE status = 'COMPLETED' AND service_date >= DATE '{a}' AND service_date < DATE '{b}'
          GROUP BY 1 HAVING count(*) >= 3)""").fetchone()
    con.close()
    return {"collections": int(n), "invoiced_eur": round(inv_total, 2), "contract_expected_eur": round(exp_total, 2),
            "invoiced_vs_expected_pct": round(100 * (inv_total / exp_total - 1), 2),
            "collections_exact_to_cent_pct": round(100 * exact, 1),
            "tendered_invoiced_eur": round(inv_tendered, 2), "collection_plus_processing_expected_eur": round(ref_tendered, 2),
            "per_lift_collection_cost_cv_median": round(cv[0], 3), "per_lift_collection_cost_cv_p90": round(cv[1], 3),
            "reading": ("Today's price = invoiced amount, which matches the contract-expected amount to the cent for most "
                        "collections; the rest are billing discrepancies. Collection cost per lift is close to constant per "
                        "device (median CV), so scaling trip costs with the number of lifts is a fair approximation.")}


def trips_check(root: Path, period: tuple[str, str]) -> dict:
    from .trips import device_trips
    a, b = period
    con = open_dataset(root)
    tr = device_trips(con)
    tr = tr[tr.weight_trips.notna()].copy()
    tr["removed_share"] = (1 - tr.weight_trips.astype(float) / tr.actual_lifts).clip(lower=0)
    lab = con.execute(f"""SELECT device_id, count(*) AS labelled FROM read_parquet('{_labels_dir(root) / 'anomaly_labels.parquet'}')
                          WHERE label_family = '{FAMILY}' AND event_at >= TIMESTAMPTZ '{a}' AND event_at < TIMESTAMPTZ '{b}'
                          GROUP BY 1""").df()
    lifts = con.execute(f"""SELECT device_id, count(*) AS lifts FROM collection_events WHERE status = 'COMPLETED'
                            AND actual_at >= TIMESTAMPTZ '{a}' AND actual_at < TIMESTAMPTZ '{b}' GROUP BY 1""").df()
    con.close()
    x = tr.merge(lifts, on="device_id").merge(lab, on="device_id", how="left").fillna({"labelled": 0})
    x["removed"] = x.removed_share * x.lifts
    by = (x.groupby("collection_policy")[["lifts", "removed", "labelled"]].sum().reset_index()
          .sort_values("collection_policy"))
    total = float(x.lifts.sum())
    return {"devices": int(len(x)), "lifts": int(total),
            "model_removed_lifts": round(float(x.removed.sum())), "labelled_premature_lifts": int(x.labelled.sum()),
            "model_removed_pct": round(100 * float(x.removed.sum()) / total, 1),
            "labelled_premature_pct": round(100 * float(x.labelled.sum()) / total, 1),
            "per_device_pearson": round(float(x.removed.corr(x.labelled)), 3),
            "per_device_spearman": round(float(x.removed.corr(x.labelled, method="spearman")), 3),
            "labelled_devices": int((x.labelled > 0).sum()),
            "labelled_devices_also_reduced": int(((x.labelled > 0) & (x.removed > 0.5)).sum()),
            "by_policy": [{"policy": r.collection_policy, "lifts": int(r.lifts), "model_removed": round(float(r.removed)),
                           "labelled_premature": int(r.labelled)} for r in by.itertuples()],
            "reading": ("The labels count only lifts the dataset calls unjustified today. The trips model also merges lifts "
                        "that are justified under today's fill-based rules but unnecessary with a weight trigger. Read the "
                        "labelled share as a lower bound and the model's share as an upper estimate.")}


def validation_facts(root: Path) -> dict:
    period = _period(root)
    if period is None:
        return {"split": SPLIT, "available": False, "premature": [], "scorecard_b2": None}
    rows, variant = premature_validation(root, period[1])
    return {"split": SPLIT, "available": True, "period": list(period), "family": FAMILY,
            "premature": rows, "premature_variant": variant, "scorecard_b2": scorecard_validation(root),
            "economics_check": economics_check(root, period), "trips_check": trips_check(root, period),
            "method": ("Kit scorer europress_data.evaluate (score_b, score_b2), validation split. FullLoad rule on the "
                       "as-of view at the validation end; kit B2 rules and B4 gradient boosting as run by the kit "
                       "(B4 trained on train-period labels).")}


if __name__ == "__main__":
    print(json.dumps(validation_facts(data_root(sys.argv[1] if len(sys.argv) > 1 else None)), indent=2))
