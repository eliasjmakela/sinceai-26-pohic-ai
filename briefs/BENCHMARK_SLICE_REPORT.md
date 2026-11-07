# Benchmark slice report (Task B premature lifts, Task B2 operator scorecard)

Branch `benchmark-slice`. Competition pack, **validation split only** (2026-06-01 to 2026-08-01 for Task B; month
2026-06 for Task B2). Every number below comes from the kit's own scorer (`europress_data.evaluate`).

Reproduce: `FULLLOAD_KIT=<kit> fullload build` (bundle section `validation`), or
`python -m fullload.validate competition` (prints the same section). Runtime about 10 s.

## 1. Results

### Task B, family PREMATURE_UNJUSTIFIED (404 positives in validation)

| model | predicted | TP | precision | recall | F1 | explained cases flagged | value-weighted recall |
|---|---|---|---|---|---|---|---|
| **FullLoad rule** (`premature.py`, default) | 304 | 287 | **0.944** | 0.710 | 0.811 | **0** | 0.714 |
| kit B2 rules | 266 | 240 | 0.902 | 0.594 | 0.716 | 0 | 0.578 |
| kit B4 gradient boosting | 411 | 377 | 0.917 | **0.933** | **0.925** | 13 | 0.947 |
| *FullLoad rule + pre-closure customer requests (variant, off)* | 396 | 357 | 0.902 | 0.884 | 0.893 | 6 | 0.883 |

What this says, plainly:
- The transparent weight-based rule beats the kit's rules baseline on every metric (+0.09 F1, +12 pts recall,
  +4 pts precision) and, like B2, flags **no** explained early lifts.
- The kit's ML baseline has the best F1, but it flags 13 lifts that the labels mark as explained early lifts
  (EARLY_JUSTIFIED traps), and it cannot say why it flagged a lift. The rule can, for every lift.
- The rule's recall gap is mostly precautionary customer orders before a weekend (scenario S39). They have the same
  low weight as justified customer requests, so the default rule leaves all customer requests alone. The variant
  that adds them closes most of the gap but flags 6 explained lifts.

### Task B2, operator scorecard (14 validation rows with >= 10 jobs)

| metric (ours → kit name) | FullLoad score | kit B5, same rows | within-region rank corr. |
|---|---|---|---|
| on_time_share → on_time_rate | 0.9998 | 0.9998 | 1.0 |
| missed_visit_share → missed_visit_rate | 0.9990 | 0.9990 | 1.0 |
| ticket_share → weighbridge_shared_7d_rate | 0.9998 | 0.9998 | 1.0 |
| ticket_lag_days_median → median_share_lag_days | 0.9794 | 0.9794 | 1.0 |
| discrepant_line_share → discrepant_line_rate | 0.6738 | 0.3159 | 0.83 |
| **mean over the 5 metrics we produce (0–100)** | **93.04** | 85.88 | |
| kit overall over all 9 metrics (missing ones score 0) | 51.69 | 47.71 | |

*Updated 7 Nov night: our invoice-line share now matches mistyped job references by contract and service date (the
kit's SCHEMA.md rule), which lifts it from 0.32 (equal to B5) to 0.67.*

`tonnes_per_lift` is also produced (for the market simulation) but has no Task B2 label. The four service metrics
are essentially exact, as expected: they are the customer's own records. The invoice-line share is moderate (0.67, 0.32 before the job-reference matching): the
truth counts missing lines and differences against the true contract amount, and our expected amounts come from the
kit's B1 calculator, which inherits invoice tonnages. Use the service metrics in the simulation; treat the
invoice-line share as indicative only.

## 2. Method

**Premature-lift rule** (`pipeline/fullload/premature.py`, docstring has the full definition). Public tables only.
- Load share = `device_estimated_collected_kg` / device's typical full payload. The payload is the trips model's
  (`trips.device_trips`): median of kg × 100 / fill % over the device's own lifts with fill >= 40 %.
- Low load = load share < 0.40; fill < 40 % only where no load share exists (no device weight or no payload).
- Arms (by `original_trigger_type`): SCHEDULED lifts with low load on devices **not** already at the slowest
  schedule the material's maximum interval allows (same test as kit B2); ON_CALL_ORDER lifts whose **weight** is low
  although the fill sensor triggered them (fill read high, mass did not: scenario S40, which B2 cannot see).
- Never flagged: MAX_INTERVAL_RULE, CUSTOMER_REQUEST_PRE_CLOSURE, DECOMMISSION, AD_HOC_CUSTOMER, and all customer
  requests in the default rule.
- **Thresholds**: one choice, 0.40, the kit B2 rule's 40 % fill cut applied to weight instead of fill. Not
  searched. The only other decision, arm 3 (customer requests on on-call devices the day before a weekend/closure)
  on or off, was taken on the **train** period: on train, arm 3 lifts F1 from 0.825 to 0.905 but flags 13 explained
  lifts (vs 0). The brief says explained early lifts must not be flagged, so it is **off**
  (`INCLUDE_PRE_CLOSURE_REQUESTS = False`). The variant is still scored and reported so the lead can choose.

**Kit baselines** are run exactly as `baselines/run_all.py` runs them: B2 = `detect_collections` on
`collection_features` (with B1); B4 = `b4_ml_models.task_b` trained on train-period lifts and train-period labels,
predicting all lifts. Only the PREMATURE_UNJUSTIFIED family is scored.

**Same rows, same metric**: all three go through `evaluate.score_b(pred, labels_dev, "validation")`, which filters
both labels and predictions to validation-period entities. Check against `BENCHMARK.md`: B2 PREMATURE_UNJUSTIFIED
reproduces exactly (404 positives, P 0.9023, R 0.5941, F1 0.7164, 0 explained). BENCHMARK.md publishes no
per-family B4 row; the B4 run here reproduces its published macro-F1 over all families, 0.3518, exactly.

**Scorecard** (`pipeline/fullload/scorecard.py`): SQL over `collection_events`, `weighbridge_tickets`, `sites`,
`invoice_lines`, `invoices`, `contracts`; expected invoice amounts from the kit's B1 calculator (via `fullload.kit`),
compared in integer cents. The definitions match the kit's Task B2 definitions (2 h on-time window, 7-day sharing
window), so the four service figures land on the same values as kit B5, and the invoice share beats it (0.67 vs 0.32). That is the point: they are sound
enough to feed the simulation. Scored with `evaluate.score_b2(..., "validation")`.

**Leakage guards** (`validate.py`): the split must exist in the package manifest (the kit's `_period_filter`
silently scores everything if it does not); the FullLoad rule runs on the kit's leak-free `open_dataset(as_of=<end of
validation>)` view, so it sees no test-period rows (a test checks this); labels are read only in `validate.py`; the
organisers' private folder is never touched; no test split is scored.

## 3. Limitations

- The payload uses all of the device's visible lifts, including the scored lift itself (a production version would
  use a trailing window). For a device that is almost always lifted early, the payload is under-estimated and its
  early lifts are missed (conservative).
- Device weight carries sensor drift and calibration errors; the rule inherits them.
- The default rule cannot see precautionary customer orders (the main recall gap); the variant can, at the cost of
  flagging some justified requests.
- Kit B4 is run as the kit ships it (fixed 0.5 threshold, no calibration). We did not try to improve it, by design.
- The scorecard's invoice-line share inherits B1's blind spots (invoice tonnage taken at face value, missing lines not
  counted). Ticket lag is a lower bound (tickets shared after extraction are invisible).
- Only one validation month for Task B2 (14 rows). Synthetic data throughout.
- A flag or a scorecard difference is a prompt for a human, not a finding of fault. Late lifts, missed visits,
  unshared tickets and invoice differences all have non-operator causes (blocked access, closures, customer
  reschedules, data-sharing agreements, tariff versions, calculator gaps).

## 4. Gate self-check

| Gate | Result | Evidence |
|---|---|---|
| BG1 Scope | PASS | `git diff --name-only main...benchmark-slice` lists only `pipeline/fullload/{premature,scorecard,validate,export}.py`, `pipeline/tests/test_benchmark_slice.py`, `briefs/BENCHMARK_SLICE_REPORT.md`. The committed `web/public/data/bundle.json` was **not** regenerated (outside §3); the lead regenerates it. |
| BG2 Label hygiene | PASS | `test_labels_only_read_by_allowed_modules` passes; `test_product_modules_read_public_tables_only` greps `premature.py`/`scorecard.py` for label tables; `test_validation_scores_validation_split_only` checks the split and that `validate.py` has no test-split / private-folder reference; `test_rule_sees_no_rows_after_validation_end` checks the as-of cut. |
| BG3 Honest comparison | PASS | All three via `evaluate.score_b(..., "validation")` on the same label rows; one command (`fullload build` / `python -m fullload.validate competition`); explained-flagged reported for each; B2 matches BENCHMARK.md exactly, B4 macro-F1 0.3518 matches exactly. The ML baseline beats our rule on F1, and the report says so. |
| BG4 No leaderboard chasing | PASS | One threshold (0.40 = kit B2's cut) as a constant with a rationale line; arm 3 decided on train, off; no search, no model beyond kit B4; `test_thresholds_are_fixed_constants`. |
| BG5 Conventions | PASS | Kit access via `fullload.kit` only (`baseline(...)`, incl. `baseline("europress_data.evaluate")` for the scorer); Figures with tag/sources/formula; money compared in integer cents; `pytest`: 15 passed; competition bundle built twice: byte-identical (`cmp`). |
| BG6 Neutral wording | PASS | `scorecard.DEFINITIONS` use share / difference / lag and name non-operator causes for each metric; rule assumptions say a flag is a prompt for review, not a finding against anyone. |
| BG7 Report | PASS | This file: results tables, method, limitations, gate table. |
