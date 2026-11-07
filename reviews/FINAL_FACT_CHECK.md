# Final fact-check (7 Nov 2026, late evening)

Every number a judge can see, checked against its source: `web/public/data/bundle.json` (queried by key),
`part1/installed_cost.json`, `part1/generated/h7_hydraulic.json`, the output of `part1/calc/h7_2_*.py`, and
`pipeline/fullload/pricing.py` (re-run for values the bundle does not hold). Arithmetic was recomputed where
possible. Status: **OK** = matches; **fixed** = text corrected in this pass; **report** = left as is, needs a
decision (code, data or unverifiable).

After the fixes: `fullload build`, `pytest` (all pass), `tsc -b`, `oxlint` (clean) and `npm run parity`
(4 market + 8 pricing cases) all pass. The rebuilt bundle is byte-identical to the committed one.

## Job 1 (the €1,000 H7 base), propagated to

PRODUCT.md (§1 who pays, figure decisions, §4 screen 3 row, §9 risks and open questions), LIMITATIONS.md (§2, §2c,
§8, §9), BUSINESS_CASE.md (summary, §2, §5 table and text, §7, §8 risks, §9 roadmap), MASTER.md (§A 5, 8, 9, 10;
§B 6, 9, 10; §C3, §C4; §D; §E; §F1, F3, F5), reviews/OPENWEIGHT_PDF_FIXES.md item 1, part1/RED_TEAM.md R27,
part1/WEIGHING_CONCEPT.md §0 item 3. The §5 scenario table in BUSINESS_CASE.md now uses the bundle's base-centred
sensitivity rows (the old "Mid H7, adoption 40 % / no packages / no extra sales" rows no longer exist in the
bundle). "To confirm with Europress" for the COMBI/DUO split is now "unknown (no data); the model assumes all new
units are weighed".

## Table

| Where | Claim | Source value | Status | Note |
|---|---|---|---|---|
| Pitch 1 (Today.tsx) | 3.4× price per tonne half empty | `fleet.visit_cost_by_fill` 166.8 / 49.0 = 3.40 | OK | |
| Pitch 1 | €143 / €150 / €160 per visit; €167 / €70 / €49 per t | 143 / 150 / 160; 166.8 / 69.6 / 49.0 | OK | |
| Pitch 1 | 56.5 % of charges per visit | `fleet.trip_share_pct` 56.5 (3.577 / 6.332 M = 56.49 %) | OK | |
| Pitch 1 | 0 of 19 customers contestable, region FI-01 | `market.headline.contestable_before` 0; 19 inputs | OK | |
| Pitch 1 | "about a third of emptyings below 50 % full (Paananen, LUT 2024)" | R1 | OK (existence) | content not re-read: lutpub blocks automated fetches |
| Pitch 2 (Weight.tsx) | ±4.4 % 1σ after 10 tickets, range 2.6–9.7, ±3.2 % two-end, ~±10.7 % without | `weighing.h7` = h7_hydraulic.json case B / C / A | OK | |
| Pitch 2 | 10 mm stroke; ≤ 113 bar of ~200; 80 mm bore | `weighing.h7` | OK | |
| Pitch 2 | worked example 27 → 57 bar → 2.5 t, 85 kg/bar | 30 bar × 85 = 2.55 t; 80 mm bore → 51.2 kgf/bar ÷ 0.6 = 85.3 | OK | |
| Pitch 2 | installed H7 €1,034–3,008, H1 €548–2,363, PS €7,860–22,160; retrofit €1,994–6,168 | installed_cost.json | OK | |
| Pitch 2 | 1,200 units a year | `pricing.params.new_units_per_year` | OK | |
| Pitch 3 (Value.tsx) | €/t €113 → €100, about 12 % less | market 113.1 → 99.55 (−11.98 %) | OK | screen rounds €99.55 to €100; docs say €99.6 |
| Pitch 3 | visits 3,845 → 3,102 (−19 %); 19 / 19 contestable | `market.headline` | OK | 743 / 3,845 = 19.3 % |
| Pitch 3 | 6.1–18.1 % fewer visits | `validation.trips_check` (165 / 2,716; 493 / 2,716) | OK | |
| Pitch 3 | 68.3 % on time, €1,111 above contract | `hero.service_check` | OK | |
| Pitch 3 | ±10 % vs ±37 % | `sigma_inc` 0.1004, `sigma_ent` 0.3726 | OK | |
| Pitch 3 | NPV €180,188, pays back year 9, self-lift €1,000, €30 break-even | `pricing.headline` | OK | |
| Business screen | default NPV +€0.18 M, year 9, deepest −€3.83 M, cumulative +€2.79 M | parity case fee 30 | OK | parity-tested |
| Business screen | break-even €30 (€48 at Part 1 mid); max H7 €1,020 at €30 | scenarios, `max_h7_capex_eur` | OK | |
| Business screen | "with the H7 cost from Part 1" | H7 capex is the team's €1,000; upkeep from Part 1 | fixed | display string only, no logic changed |
| Business screen | value per device €686–1,469 / €1,278 / €301 / €2,712; team 1,570 / 1,245 / 100 / 1,930 / 400 | `value_per_device.rows` | OK | |
| Business screen / SMART_INTEGRATION | lift order 1,850 kg, σ 63 kg | illustrative | report | 63 / 1,850 = 3.4 %, not the claimed 4.4 % (≈ 81 kg); label says illustrative |
| Customer screen | 163 visits, 49.7 % under 60 %, €137.6/t → €95.2/t | `hero.figures` (81 / 163 = 49.7 %; 28,218 / 205.1 t = 137.6) | OK | |
| Customer report | €8,699 (30.8 %) less; 132–116 visits; 47 fewer (28.8 %) | 28,218 − 19,518 = 8,700 (cent rounding); 47 / 163 = 28.8 % | OK | |
| Customer screen | 24 / 712 invoice lines; 93.9 % tickets; 1 missed | `hero.service_check` | OK | service_check counts 164 lifts vs 163 in figures (different definitions); harmless |
| Operator screen | medians 13.2 % vs 64.6 %; OP-E wins at €19,518 vs €28,218 | `hero.operator_view` | OK | |
| Market screen | defaults €3.9/t fee, 9 of 19 switch | `market.params` 390 c/t; `accounts_switched` 9 | OK | |
| Fleet screen | 447 devices; 56.5 %; 33.4 %; 37,429 t | `fleet` | OK | |
| PRODUCT.md §1 | €30 ≈ €3.9/t at 92.6 t per device-year | 37,428.7 t / 404 = 92.6; 360 / 92.6 = 3.89 | OK | |
| PRODUCT.md figure decisions | showcase customer −31.9 % | `hero.figures.saving_pct` 30.8 | fixed | also LIMITATIONS §5, MASTER §C3 |
| PRODUCT.md figure decisions | €0.7–1.5k, ~€1.3k, €2.7k; ±4.4 %; €1,034–3,008 | bundle | OK | |
| PRODUCT.md §4 row 3 | "pays back if H7 ≤ ~€1,000" | screen shows +€0.18 M, y9 at €1,000 | fixed | |
| PRICING.md | base row −2.46 / +0.18 (y9) / €30 / 59 %; other scenario rows | `pricing.scenarios` | OK | all eight rows match |
| PRICING.md | max capex €690 / €850 / €1,020 | `max_h7_capex_eur` | OK | |
| PRICING.md | "at €800 €30 gives +€3.1 M, year 7" | that is €800 **and €39 upkeep**; €800 at €73 upkeep gives +€1.79 M (pricing.py) | fixed | upkeep named |
| PRICING.md | "parts alone €550–1,100" (as Part 1) | Part 1 hardware €550–1,300; €550–1,100 is the team document | fixed | |
| PRICING.md | operator: 41 visits, €150 / 437 / 862, 55 / 82 %, 18 / 26 %, 29–87 / 44–130 %, €276–818 | `pricing.operator`; recomputed (e.g. 41.1 × 18.1 % × €116 = €863; 360 / 437 = 82 %) | OK | |
| PRICING.md | €30 at 40 % = €20 at 60 % | 12 = 12; both NPV −€2.46 M | OK | |
| PRICING.md | team model +€2.49 M, deepest −€2.94 M, cumulative +€6.41 M, y7 | parity case (825, 50) | OK | |
| BUSINESS_CASE.md §1 | 56.5 %, 33.4 %, €143/150/160, €167/70/49, ±10 vs ±37, 0 of 19 | bundle | OK | |
| BUSINESS_CASE.md §3 | €113.1 → €99.6 (−12 %), 3,845 → 3,102, 9 switch, 68.3 %, 93.9 %, 24 / 712 | bundle | OK | |
| BUSINESS_CASE.md §5 | old table (mid H7 as headline, mid-H7 sensitivity rows −8.93 / −12.51 / −8.71) | not in bundle any more | fixed | rebuilt from `pricing.scenarios` with the base on top |
| BUSINESS_CASE.md §5 | €1,130 max capex at €50 upkeep | pricing.py `max_h7_capex` with upkeep 50: 1,130 | OK | |
| BUSINESS_CASE.md §8 | "at 40 % no fee in range pays back with mid H7 cost" | base at 40 %: −€2.46 M at €30; break-even €44 | fixed | |
| BUSINESS_CASE.md [R2] | Weiergraeber, S. & Wolf, C. (2023), IJIO 87, 102902 | published authors: **Carnehl, C. & Weiergraeber, S.** | fixed | also OPENWEIGHT_PDF_FIXES refs |
| BUSINESS_CASE.md [R2] | "removing the information gap raised the chance … by 48 pp (median)" | Dec 2022 accepted version: counterfactual, removing the strategic response to the common-value asymmetry, **+43 pp average**; Bocconi IRIS abstract says 48 pp median | fixed | now "more than 40 percentage points" in a counterfactual |
| BUSINESS_CASE.md [R3] | public cost information reduced the spread of bids, most where cost uncertainty was largest | De Silva et al. 2008, EER 52(1) 150–181 | OK | |
| BUSINESS_CASE.md [R4] | price structure matters; one side often subsidised | Rochet & Tirole 2003, JEEA 1(4) 990–1029 | OK | |
| BUSINESS_CASE.md [R5] | service investment raises costs without matching returns | Gebauer, Fleisch & Friedli 2005, EMJ 23(1) 14–26 | OK | |
| BUSINESS_CASE.md [R1] | HSY: a third below 50 % fill; sensors pay only with changed cost structure | thesis exists (LUT 2024, HSY mixed-waste **underground** containers) | report | findings not re-read (bot block) |
| MASTER.md §A8, §D | customer €/t −13 % | −11.98 % with the €30 fee | fixed | §C3 and F3 marked resolved |
| MASTER.md §C4 | base row, 59 %, team y10 +€2.38 M/yr | parity cash flow y10 2,377,500 | OK | |
| MASTER.md §C1–C3 | trigger medians 82 / 52 / 44 / 39 %; 97.6 % of 1,586; F1 0.81, recall 71 %, ML 0.93 with 13 | bundle | OK | |
| MASTER.md §C2 | virtual scale 8.3 / 7.6 / 5.5 / 16.2 | `virtual_scale.headline` | OK | |
| LIMITATIONS.md | 404 / 447; 380 devices, 2,716 lifts, 66 of 78; 97.6 %, +0.34 %, CV 0.09; scorecard 0.32 | bundle | OK | |
| LIMITATIONS.md §4 | HHI ~5,350 → ~6,170; switching 8–19 | not in the bundle | report | from an earlier sensitivity run; not reproducible from the bundle |
| OPENWEIGHT_PDF_FIXES item 4 | "€113 → €98, −13 % (−12 to −15 %)" | €113.1 → €99.6, −12 % | fixed | |
| WEIGHING_CONCEPT §0 | €1,034–3,008, capex €800–2,370, upkeep €39–106, retrofit €1,994–6,168 | installed_cost.json; h7_2_cost.py (maintenance 234–638 / 6 y) | OK | mid 1,585, upkeep mid 72.5 → 73 |
| WEIGHING_CONCEPT §0 | 31–57 kN point load | h7_hydraulic.json full_max 56.7 kN; §19.2 table 31–57 | OK | |
| WEIGHING_CONCEPT §19.7 | hardware €550–1,300 | installed_cost.json H7 hardware | OK | |
| WEIGHING_CONCEPT §19.8 | fused 4.1 % | h7_hydraulic.json | OK | |
| WEIGHING_CONCEPT §20.3 | case C 1.7 / 3.2 / 8.4 % (2.5 t), 0.9 / 1.9 / 4.8 % (5 t) | h7_hydraulic.json; h7_2_statics.py | OK | |
| WEIGHING_CONCEPT §20.6 | H7-2 €1,801–5,026, capex €1,427–3,965, 7.1–19.8 % of €20k, hardware €1,030–2,360 | h7_2_cost.py output | OK | |
| WEIGHING_CONCEPT §20.6–20.7 | extra hardware €480–1,060; extra capex €627–1,595 | 1,030 − 550, 2,360 − 1,300; 1,427 − 800, 3,965 − 2,370 | OK | |
| WEIGHING_CONCEPT §20.6 | H7-2 retrofit €3,354–9,676 | not printed by h7_2_cost.py, not in installed_cost.json | report | could not reproduce |
| SMART_INTEGRATION.md | €30 / device / month; ±10 % vs ±37 %; "81 of 163 lifts" | bundle | OK | |
| README.md | no headline numbers beyond €30 | – | OK | does not list BUSINESS_CASE.md or SMART_INTEGRATION.md in the document table (not a number issue) |

## Not resolved

1. **[R1] Paananen 2024:** the thesis exists (HSY mixed-waste underground containers), but lutpub blocks automated
   reads, so "a third below 50 % fill" and "pays only with a changed cost structure" were not re-checked here.
2. **[R2] effect size:** the accepted version says +43 pp (average) and the Bocconi abstract says 48 pp (median).
   The published text could not be opened, so the docs now say "more than 40 percentage points".
3. **Lift-order example σ 63 kg on 1,850 kg (3.4 %)** in Business.tsx and SMART_INTEGRATION.md is tighter than the
   ±4.4 % claim. It is code or payload data, so it was not changed. Suggest σ ≈ 81 kg.
4. **pricing.py receipt text** still reads "highest H7 capex … (design-to-cost target)" (`max_h7_capex_eur.formula`,
   visible in receipts). This is code, so it was not changed. Suggest "break-even H7 capex".
5. **HHI 5,350 → 6,170 and "8 to 19 customers switching"** (LIMITATIONS §4, MASTER §C3, BUSINESS_CASE §8) are not in
   the bundle and were not computed with the €30 fee (LIMITATIONS already says the sensitivity was not recomputed).
6. **H7-2 retrofit €3,354–9,676** (§20.6) is not reproduced by any script output.
7. Left stale, not judge-facing: PRODUCT.md §9 "the €30 fee (pending)" open question, TODO.md C6
   ("design-to-cost"), MASTER.md §G (a historical snapshot).
