# Agent brief: benchmark slice (Task B premature lifts, Task B2 operator scorecard)

> Self-contained brief for an agent working on its own. A supervisor agent and the lead developer check the result
> against the **quality gates in §5**. Everything outside those gates is the agent's own judgement.

## 1. Mission
Deliver the two pieces of the starter kit's benchmark that feed the FullLoad demo. Do **not** chase leaderboard
scores beyond that (PRODUCT.md §6 "Explicitly OUT").

1. **Rules vs ML on premature lifts (Task B, family `PREMATURE_UNJUSTIFIED`).** The challenge brief §04 asks to
   "compare AI-driven insights with transparent rule-based logic". Build one transparent FullLoad rule for unjustified
   premature lifts (using device weight / fill / calendar, e.g. reusing the payload idea in `pipeline/fullload/trips.py`),
   and compare it with the kit's rules baseline (B2) and ML baseline (B4) on the **validation period**: precision,
   recall, F1, and **explained cases flagged** (`EARLY_JUSTIFIED` traps must not be flagged).
2. **Operator scorecard metrics (Task B2).** Per operator × region × month from **public tables only**: tonnes per lift,
   on-time share, missed visits, weighbridge-ticket sharing share and lag, discrepant invoice line share. These feed the
   market simulation (PRODUCT.md §3, beat 4). Score them against `labels_dev/operator_scorecard` on the validation
   period with the kit scorer (`--task B2`) to show they are sound.

Read first: `PRODUCT.md` (all, especially §3, §5, §7.2, §8), `CLAUDE.md`, and in the kit
(`/home/eliasjmakela/Documents/sinceai26-haaste/resources/Europress_SMART_Material_Value_Engine_v1.0.1/`):
`docs/BENCHMARK.md`, `docs/QUICKSTART_FOR_BUILDERS.md`, `docs/SCHEMA.md`, `docs/DATA_DICTIONARY.md`,
`docs/SCENARIO_CATALOG.md`, `baselines/b2_rules_anomaly.py`, `baselines/b4_ml_models.py`,
`baselines/b5_operator_scorecard.py`, `src/europress_data/evaluate.py`.

## 2. Working rules
- Work on git branch **`benchmark-slice`** in your own worktree. Commit in sensible steps; end every commit message with
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not merge, push or touch other branches.
- `resources/` is not in git. Use the main checkout by absolute path (above). Set
  `FULLLOAD_KIT=<that path>` so `pipeline/fullload/config.py` finds it. Never modify anything under `resources/`.
- Use the main checkout's venv: `/home/eliasjmakela/Documents/sinceai26-haaste/.venv` (it has the kit and pipeline
  installed editable; install your worktree's pipeline with `pip install -e <worktree>/pipeline` into a **new**
  `pipeline/.venv` if you need isolation — do not modify the main `.venv`). Add no new dependency without a licence row.
- Follow the pipeline conventions: kit access only through `fullload/kit.py`; every displayed number is a `Figure`;
  deterministic output; money in integer cents.
- **Labels**: `labels_dev` may be read **only** in `pipeline/fullload/validate.py` (the existing test enforces this).
  **Validation split only.** Never read or score the test period; never open `private_evaluation/`.
- Timebox about 3 hours. If a gate cannot be met, stop and report.

## 3. Deliverables (only these files may change)
| Path | Content |
|---|---|
| `pipeline/fullload/premature.py` | The FullLoad premature-lift rule (public tables only), documented in its docstring |
| `pipeline/fullload/scorecard.py` | Operator × region × month efficiency metrics (public tables only) |
| `pipeline/fullload/validate.py` | Scores: our rule vs kit B2 rules vs kit B4 ML on validation; our scorecard vs `labels_dev` with the kit scorer |
| `pipeline/fullload/export.py` | At most a few lines: add `"premature"`, `"scorecard"` and `"validation"` sections to the bundle |
| `pipeline/tests/test_benchmark_slice.py` | Tests on the quickstart pack (determinism, Figures valid, no test-period rows used) |
| `briefs/BENCHMARK_SLICE_REPORT.md` | Results table, method notes, gate self-check (§5) with evidence |

## 4. Bundle contract (additions)
```
"premature":  {"rule": str, "flagged_lifts": Figure, "flagged_share_pct": Figure, "by_policy": [...]}
"scorecard":  {"rows": [{"operator_id", "region_code", "month", "tonnes_per_lift", "on_time_share",
                "missed_visit_share", "ticket_share", "ticket_lag_days_median", "discrepant_line_share", "jobs"}],
               "definitions": {...}}
"validation": {"premature": [{"model": "fullload_rule|kit_b2_rules|kit_b4_ml", "precision", "recall", "f1",
                "explained_flagged"}], "scorecard_b2": {"overall": number, "per_metric": {...}}, "split": "validation"}
```

## 5. Quality gates (each must PASS; the supervisor checks every one)
| Gate | Rule | How to check |
|---|---|---|
| **BG1 Scope** | Only the files in §3 changed | `git diff --name-only main...benchmark-slice` |
| **BG2 Label hygiene** | `labels_dev` read only in `validate.py`; validation split only; no `private_evaluation`; product modules (`premature.py`, `scorecard.py`) use public tables only | existing test `test_labels_only_read_by_allowed_modules`; grep for `test`/`private_evaluation`; read `validate.py` split filter |
| **BG3 Honest comparison** | All three models scored on the same validation rows with the kit's own scorer/metric definitions; numbers reproduced by one command; explained-cases-flagged reported for each | rerun the command; compare to `BENCHMARK.md` baseline numbers for B2/B4 (should match within rounding) |
| **BG4 No leaderboard chasing** | No hyper-parameter search, no model beyond kit B4, no tuning on validation labels of the rule's thresholds beyond one documented choice | read `premature.py`; thresholds are constants with a one-line rationale |
| **BG5 Conventions** | kit access via `kit.py` only; Figures with tag/sources; deterministic bundle; all pipeline tests pass | `pytest`; build twice and diff |
| **BG6 Neutral wording** | Scorecard definitions and report use neutral language (difference, share, lag), list non-operator causes where relevant | read definitions + report |
| **BG7 Report** | `BENCHMARK_SLICE_REPORT.md` has results table, method, limitations, gate table with evidence | read |

## 6. Final report
Reply with: branch name, files changed, the results table, the gate table, and anything the lead developer must decide.

## 7. Supervisor checklist
1. BG1 diff; 2. run `pytest` and `fullload build` twice, diff; 3. read `validate.py` split handling; 4. compare kit
baseline numbers with `BENCHMARK.md`; 5. read `premature.py` thresholds; 6. merge only after the lead developer reviews.
