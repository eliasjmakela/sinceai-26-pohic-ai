# Part 1 quality-gate self-check (weighing v2)

Branch `weighing-v2` (from `part1-weighing`), checked 7 Nov 2026. Line numbers refer to `part1/WEIGHING_CONCEPT.md`
(D1) unless another file is named. Self-check: the supervisor should re-verify every row.

## v1 gates (briefs/PART1_WEIGHING.md §5)

| Gate | Result | Evidence |
|---|---|---|
| **QG1 Brief coverage** | PASS | Coverage table D1:503–519 maps 13 items to non-empty sections: principle §3.1 (D1:93) and §6 (D1:204), placement §5.1/§5.2 (D1:159, 169), cost §7 (D1:262) + Appendix A (D1:608), installation/retrofit §12 (D1:443), calibration §13 (D1:458), error sources §8.2 (D1:322), accuracy §1/§8 (D1:49, 297), validation §14 (D1:468), limitations §15 (D1:480), comparison §10 (D1:386) |
| **QG2 Sourced costs** | PASS | Every euro figure carries [n] or "team estimate" in its sentence or table row; checked with a grep over every `€` line (remaining hits are sentences wrapped over two lines and reference-list entries). Cost tables have a source column (D1:264–274, Appendix A). Spot-checked URLs that opened during the work: [22] KERN CT 500 (€220), [26] Zemic BM8H ($262.50), [27] WEDI container scale (€4,800/5,620) |
| **QG3 No over-claiming** | PASS | grep for "proven", "validated", "guaranteed", "certified accuracy": no hits. "Europress specification" appears only as "not a Europress specification" (D1:363). Every σ is tagged *estimate*/*simulation target*/*literature* (D1:5–9; tiers table D1:391–398, evidence column; H1 tagged `estimate` in `sigma_tiers.json`) |
| **QG4 Machine-type correctness** | PASS | COMBI D1:159–167 (whole unit lifted and transported; H1 plate travels but carries only plate + charge; tipping at emptying) and DUO D1:169–175 (compactor stationary; only the container exchanged; H1 never weighs the container, sum resets at docking); H5 separately for COMBI (8–9.5 t, machine re-tare) and DUO (container only, coupling bypass) D1:209–213. Mechanical assumptions in the human-review list D1:699–718 and `ENGINEER_QUESTIONS.md` |
| **QG5 Reproducible data claims** | PASS | `part1/scripts/reproduce.sh` regenerates every calc, number and figure; two consecutive runs → `diff -r` of `generated/`, `figures/`, `sigma_tiers.json`, `installed_cost.json`: identical. Seeds fixed (charge_sum 1–3, self_calibration 11–13, accuracy 1). Data only via `check_public_root` (`scripts/common.py:30`); no `private_evaluation`/`labels_dev` reads in `scripts/` or `calc/` |
| **QG6 Interface valid** | PASS (shape) / **DEVIATION** (chosen tier) | `scripts/check_interface.py` → "OK": same keys and types as §4, `schema_version` 1, D1 tables verbatim. Deviations, for the lead developer: six tiers instead of three (ids T0, T1, T2, H1, H5, PS; the v2 brief asked for the hopper tier to be added), and `chosen_tier` is **H1, not T1**, because the v2 brief (§2 H4) asks for a recommendation and PRODUCT.md §7.5 allows the change. `schema_version` not bumped |
| **QG7 Consistent with PRODUCT.md** | PASS with one item to update | Hardware free to customers (D1:293), Europress never transports (D1:526), name OpenWeight, no "SMART" in product names, billing stays on the weighbridge (D1:36, 500). The T1-chosen clause of the v1 brief is superseded as in QG6. **PRODUCT.md §1 quotes v1's T1 figures (+10 % flagged on ~85 %, 3 % after ~2 loads); with v2 H1 mid these are 77 % and ~6 loads** (`generated/accuracy_summary.md`) |
| **QG8 Licences** | PASS | `THIRD_PARTY_part1.md`: all packages in `part1/.venv` (unchanged `requirements-lock.txt`), tools, datasets, transcripts and every web source [4]–[38]; all figures self-made (hand-written SVG or matplotlib) |
| **QG9 Scope respected** | PASS | `git diff --stat part1-weighing...weighing-v2` touches only `part1/`. No web UI, no pressure ML model (T0 in `fusion.py` is a per-device ratio), hardware maths limited to order-of-magnitude statics. Timebox ≈ 4 h |
| **QG10 Limitations stated** | PASS | D1:480–501: biowaste (H1 liquids; T0 back-pressure), humidity/moisture, temperature drift, off-centre loads, press cycle, overloads, tickets, retrofit, not legal for trade, FTO, and "Untested" first |
| **QG11 Human-review list** | PASS | D1 ends with 10 concrete items (D1:699–718) |

## v2 gates (briefs/WEIGHING_V2.md §5)

| Gate | Result | Evidence |
|---|---|---|
| **WG1 Claims ledger** | PASS | `CLAIMS_LEDGER.md` C1–C61 with source, confidence, check; its last paragraph samples ten D1 numbers and maps each to a ledger row |
| **WG2 Shown working** | PASS | Engineering numbers come from `calc/loads.py`, `calc/temperature.py`, `calc/error_accumulation.py`, `calc/installed_cost.py` (outputs `generated/calc_*.md`, pasted into D1 §5.3, §6, §7, Appendix A) or a cited datasheet ([19][20][22]) |
| **WG3 Edge is measured** | PASS | `scripts/self_calibration.py` (rerun deterministic; assumptions in its docstring and D1:149–151): H1 error 9.5 % → 4.6 % before the first ticket, 3.4 % after 10 (mid) |
| **WG4 Red team done** | PASS | `RED_TEAM.md`: 18 failure modes (frost, wet cardboard, grit, biowaste, overloads, COMBI transport, vandalism, bridging, T1 support, DUO bypass, pull force, set-down, no tickets, drift, timing, FTO, retrofit cost, model risk); 11 revised, 7 accepted explicitly |
| **WG5 Prior art** | PASS | D1 §11 (D1:421–441): 9 rows, 13 items with links ([12][13][27]–[35][38]) and how ours differs. Opened during the work: [28] US 6,427,585, [29] US 2023/0219317, [31] US 12,379,240 |
| **WG6 Honest novelty** | PASS | D1:437–441: per-charge running totals [28] and floating floors with stops [29] are not new; **no novelty claim**; hopper idea credited to Europress/Tommi (D1:21, 153); weighing rails credited to the team (D1:204) |
| **WG7 Platform scale** | PASS | PS is a candidate in every table (D1:274, 391–398, 402–411, Appendix A); why H1/H5 differ: D1:256–260 and D1:410–413 |
| **WG8 Installed cost** | PASS | Every candidate (T0, T1, H1, H5, T2, PS) has a table with all eight lines (sensors, electronics, mechanical, site work, labour, calibration, 6-year maintenance, development amortised), retrofit and factory-fit ranges, and a source or "team estimate" per line: D1 Appendix A (D1:608–697), summary D1:264–274, data in `installed_cost.json` |

## H7 addendum (branch `weighing-h7`, 7 Nov 2026 evening)

H7 = hydraulic self-lift (team idea, team document [39]). Line numbers below refer to D1 after the H7 edit (the
v2 rows above keep their original line numbers). Self-check; the supervisor should re-verify.

| Gate | Result | Evidence |
|---|---|---|
| **QG1 Brief coverage** | PASS | Coverage row for H7 (D1:564) → §19: principle 19.1 (D1:831), statics 19.2 (D1:847), placement COMBI/DUO/retrofit 19.3 (D1:894), procedure 19.4 (D1:917), error sources + target 19.5 (D1:944), safety/ground 19.6 (D1:1012), cost 19.7 (D1:1048), virtual scale/H2 19.8 (D1:1057), validation 19.11 (D1:1095); Appendix A H7 table (D1:726) |
| **QG2 Sourced costs** | PASS | Every new € figure has [39], [36], [24] or "team estimate" in its sentence or table row (grep of § 0 and § 19 € lines; one table row fixed during the check, D1:1085). Every H7 cost line carries a source column (D1:726–738). No supplier quote could be fetched (web search hit its limit), so every H7 line is labelled team estimate, anchored on [39] |
| **QG3 No over-claiming** | PASS | grep "proven / validated / guaranteed / certified accuracy" in D1: no hits ("unvalidated" from the PDF reworded). H7 σ tagged *estimate* (tiers table D1:420, `sigma_tiers.json` `evidence_tag`); accuracy given as an **untested target** (D1:1007); §19 opens with "a new idea to explore, not a design" (D1:826) |
| **QG4 Machine-type correctness** | PASS | COMBI placement, DUO (speculative variant, not costed, coupling bypass) and retrofit treated separately (D1:894–916); `suits` = ["COMBI"] only; mechanical assumptions as ENGINEER_QUESTIONS 11–14 (D1:1089) |
| **QG5 Reproducible** | PASS | `calc/h7_hydraulic.py` added to `reproduce.sh` step 1 (standard library, no data, no randomness). Two consecutive runs of `part1/scripts/reproduce.sh` → `diff -r` of `generated/`, `figures/`, `cmp` of `sigma_tiers.json` and `installed_cost.json`: **identical**. No `private_evaluation` / `labels_dev` reads |
| **QG6 Interface valid** | PASS (shape) / DEVIATION (tier count) | `check_interface.py` → "OK". Same keys and types, `schema_version` 1, `chosen_tier` **H1 (unchanged)**. Seven tiers instead of six (H7 added between H1 and H5); the checker's id list was updated accordingly. D1 now also must contain `generated/h7_budget.md` verbatim (checked) |
| **QG7 Consistent with PRODUCT.md** | PASS | Lead story = virtual scale on every device + reference subset with a real scale + fleet self-calibration from tickets (D1:19–48, PRODUCT.md §1 "Weighing architecture"); billing stays on the weighbridge (D1:49); Europress does not transport; H1 credited to Europress (D1:28), H7 to the team (D1:35); product name OpenWeight throughout `part1/` (grep "FullLoad" in part1 text: 0; the internal env var `FULLLOAD_DATA` and the SVG hash salt are code identifiers and stay) |
| **QG8 Licences** | PASS | `THIRD_PARTY_part1.md` "H7 additions": [39]–[48], pdftotext, pipeline bundle; no new Python packages |
| **QG9 Scope** | PASS | Only files under `part1/` changed (`git status`); no UI, no ML; maths limited to statics, RSS budget and arithmetic. Timebox ≈ 2.5 h |
| **QG10 Limitations** | PASS | H7 bullet in §15 (D1:543) and the error / ground / safety lists in §19.5–19.6 |
| **QG11 Human-review list** | PASS with a note | §18 keeps its 10 items; H7 items are ENGINEER_QUESTIONS 11–14 (total 14). D1 no longer *ends* with §18, because the task placed H7 as §19 after it |
| **WG1 Claims ledger** | PASS | C62–C90 cover every new H7 number; a ten-number sampling check is at the end of `CLAIMS_LEDGER.md` |
| **WG2 Shown working** | PASS | Statics, pressures, flow, stroke, ground, friction and the error budget come from `calc/h7_hydraulic.py` (`generated/calc_h7_hydraulic.md`) and are pasted into §19; statics table D1:869, worked example D1:878–885 |
| **WG3 Edge is measured** | PASS (no change) | H2 unchanged; H7's calibration benefit (case A → B) is a stated-assumption budget, not a data result, and is labelled so |
| **WG4 Red team** | PASS | R19–R28 (10 H7 failure modes: centre of mass, friction, ground, frame, safety, pivot shift, snow, rod in transport, no revenue, prior art), each revised and/or accepted |
| **WG5 Prior art** | PASS | Four new rows in §11 (D1:464–468) with nine documents [40]–[47]; opened during the work: [42] US 2020/0096383 A1, [44] DE 4405000 A1; the rest from search listings, marked |
| **WG6 Honest novelty** | PASS | D1:476–483: pressure weighing, up/down averaging, jack weighing and hooklift centre-of-mass estimation are **not new**; the narrow combination is presented as worth exploring, with no novelty claim; FTO read of [42] flagged |
| **WG7 Platform scale** | PASS (no change) | PS still in every table |
| **WG8 Installed cost** | PASS | H7 has all eight H6 lines, retrofit and factory-fit, each sourced or labelled team estimate (D1 Appendix A, D1:726; `installed_cost.json` → `candidates.H7`): **€1,994–6,168 retrofit, €1,034–3,008 factory-fit** |
