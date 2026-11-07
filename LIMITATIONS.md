# Limitations, assumptions and what remains untested

Required by the challenge brief §07 ("include assumptions and what remains untested"). Numbers below come from
`web/public/data/bundle.json` (built by `fullload build`) unless a file is named. Keep this file in step with the
pipeline: when a number changes, change it here.

## 1. The data
- **Everything is synthetic.** About 450 invented compactors over one year, invented customers, contracts and
  invoices (Europress starter kit v1.0.1). No figure here is a real price, saving or market share.
- **Prices are hypothetical** customer–operator tariffs. Europress is not a party to transport or treatment today.
- **Weight at the source is a future scenario** in the dataset: 404 of 447 devices carry a simulated device weight.
  It does not show that any weighing design works.
- **12 months only.** Seasonality ("which store at which time of year") cannot be learned or tested.
- **The size of the information gap depends on the generator.** Forecasting a device's tonnage from its own history
  is off by ~10 % (median), from similar devices by ~37 % (held-out 3 months, 385 devices). The direction is robust,
  and a teammate's independent analysis found the same direction (9 % vs 21 %, per visit); the size reflects how
  different the simulator makes individual devices.
- Operators are fictional ("Hauler Alpha–Epsilon"). Differences between them have causes other than the operator
  (device sensors, combined loads, data gaps).

## 2. Weighing concept (Part 1, `part1/`, branch `weighing-v2`)
- **Untested.** No hardware was built or measured; every accuracy figure is an estimate, a simulation target or a
  vendor claim. The team has no mechanical-engineering expertise; `part1/CLAIMS_LEDGER.md` lists every technical
  claim with its source and confidence, and `part1/ENGINEER_QUESTIONS.md` the questions for a Europress engineer.
- **Costs are ranges, mostly team estimates** (installed cost per device, 6-year lease, `part1/installed_cost.json`).
  Load-cell prices are single-unit list prices; volume prices could be much lower.
- **Self-calibration (3.4 % after ~10 shared weighbridge tickets) is measured on synthetic data** with an assumed
  error model; the unknown share of each charge that sticks in the hopper sets the floor.
- **Prior art exists** for hopper-stage weighing and for weighing rails (patents listed in `part1/WEIGHING_CONCEPT.md`
  §11). We claim no mechanical novelty; no freedom-to-operate check was done.
- **Not legal for trade.** Billing stays on the operator's certified weighbridge (EU Directive 2014/31/EU). The device
  weight is planning data and a cross-check.

## 2b. Virtual scale (`pipeline/fullload/virtual_scale.py`)
- Simulated on synthetic data: a log-linear model (fill × volume, material, machine type, compaction cycles, days since
  the last lift) trained on 10 % reference devices estimates other devices' lift weights with ~8 % median error,
  ~7–8 % after 5 shared weighbridge tickets per device, ~5–6 % on monthly totals; fill alone ~16 %.
- **Likely optimistic**: the generator derives mass from similar quantities. Real pressure data was not available.
- A single ticket makes calibration worse (one noisy ratio); calibration needs ~5 tickets.
- The figures are **median** errors; as a 1σ the calibrated per-lift error is about 11 %.

## 2c. Hydraulic self-lift (H7, `part1/WEIGHING_CONCEPT.md` §19)
- Team idea, untested: the compactor lifts itself ~10 mm with its own hydraulics and weighs from cylinder pressure.
  Installed cost €1,034–3,008 factory-fit (team estimates; no supplier prices found), COMBI only, retrofit not
  recommended. Accuracy target 1σ ≤ 5 % after 10 shared tickets (≤ 3 % lifting both ends, which needs a front
  cylinder not in the cost).
- Two failure modes found in the review of the team's paper (`reviews/SELF_WEIGHING_PAPER_REVIEW.md`), not yet in
  the error budget: **sideways tipping** (the support triangle is ~±0.21 m wide, so an off-centre load can leave one
  rear runner down) and **runner contact near the pivot** (only ~1.8 mm of lift at 1 m; ice, debris or frozen runners
  can carry load). Mitigations in §19.6 are untested.
- Hydraulic weighing exists on refuse trucks, forklifts and hook-lifts (closest: Hiab/Cargotec, truck-side, with a
  centre-of-mass estimate); we found no compactor that lifts itself to weigh. No freedom-to-operate check was done.

- The demo's H7 animation is the worked example of §19.2 (mid values), not a simulation of a real unit; the lift is
  drawn exaggerated. Its numbers come from `part1/generated/h7_hydraulic.json` via `pipeline/fullload/weighing.py`.

## 3. Weight-triggered trips (`pipeline/fullload/trips.py`)
- An approximation, not a day-by-day replay: each device's full payload is extrapolated from its own lifts, a lift
  is triggered at 90 % of it, and the material's maximum interval is respected. Closures, peaks, overflow risk and
  side waste are not modelled.
- **Validation against labels** (validation period, 380 devices, 2,716 lifts): the model removes ~18 % of lifts;
  the dataset labels ~6 % as unjustified premature lifts. Per device the two agree in pattern (Pearson 0.85), and 66
  of the 78 devices with labelled premature lifts are also reduced by the model. Read **6 % as a lower bound** (what
  the dataset calls waste today) and **~17–18 % as an upper estimate** (also merging lifts that are justified under
  today's fill-based rules but unnecessary with a weight trigger). Present the saving as a range.

## 4. Market simulation (`pipeline/fullload/market.py`, beat 4)
- **Biowaste excluded** from the market, value and virtual-scale figures (decision 7 Nov).
- **Stylised**: one region (FI-01, 19 customers, 3 operators + new entrants), one tender round, closed-form bids. No
  routing, capacity limits, learning or repeated games.
- **Assumptions are placeholders** (`pipeline/fullload/params.yaml`: cost share, margin, risk aversion, entrant
  advantage, route fit, route density, Europress fee, sensor error) until the business-case owner signs them off.
- **What is robust**: the customer's cost per tonne falls in every tested combination (€113.1 → €96–100/t, default €98.0,
  −12 to −15 %). **What is not**: who wins each tender. Each customer goes to the single best bid, so the number of
  customers switching ranges from 8 to 19 depending on the assumptions.
- **Concentration can rise.** With the default assumptions the efficient incumbent wins more volume (HHI ~5,350 →
  ~6,170). The competition effect shows as price discipline (customers a challenger can win: 0 → 19 of 19), not as
  lower concentration.
- **Today's price is observed and checked**: the invoiced amount matches the contract-expected amount to the cent for
  97.6 % of 1,586 validation-period collections (total +0.34 %; the rest are billing discrepancies). Contract
  collection cost per lift is close to constant per device (median coefficient of variation 0.09), which supports
  scaling trip costs with the number of lifts.

## 5. Showcase customer (beats 2–3)
- **Chosen by a fixed rule as the best case**: the largest simulated saving among customers in the region with at
  least 3 devices and one fixed-schedule device (`pipeline/fullload/pick_heroes.py`). Its −31.9 % is not typical;
  the region-wide figure is about −13 %. Say so when presenting it.
- Per-device forecast errors are shown because errors partly cancel when devices are added up.

## 6. Premature-lift rule and operator scorecard
- The rule finds 71 % of labelled unjustified premature lifts (F1 0.81) and flags none of the justified ones; the
  kit's ML baseline finds more (F1 0.93) but flags 13 justified lifts and gives no reasons. We chose explainability.
- The scorecard's invoice-difference share scores weakly against the labels (0.32); treat it as indicative.

## 7. AI-summarized customer report
- Written by Claude (during development; no API call at runtime) as a template in `pipeline/fullload/reports/`;
  every figure is a placeholder filled from the computed fact sheet at build time, and the build rejects any number
  that is not in the facts. Wording and reasoning are not checked automatically, so a person must read it.

## 8. Business case (beat 6, `pipeline/fullload/value.py`, `business.py`)
- **Value per device is recomputed from our pipeline** and compared with the business team's independent figures.
  Close: avoidable visits (ours €686–1,469 vs team €1,570), tonnes priced above peers (€1,278 vs €1,245).
  Higher in ours: operator pricing risk (€2,712 vs €1,930: our forecast-error gap is wider, 27 vs 12 percentage
  points, and it depends on the market parameters) and invoice above contract (€301 vs €100: the kit's B1 calculator
  leaves gaps, the same reason the scorecard's invoice metric is weak). Contamination is not recomputed.
- **The business model uses the business team's assumptions** (params.yaml `business`); its scripts are not yet in
  this repo, so its inputs are traceable only to their message. With their €500 hopper cost the investment pays back
  in ~1.6 years; at Part 1's high installed cost (€2,363 factory-fit) payback is ~9 years, beyond the 6-year lease.
  The hardware cost decides whether the model works.
- Open: fee per device per month vs per verified tonne; extra machine sales is the most uncertain lever.

## 9. Not proven / untested (summary)
- That any weighing design reaches the stated accuracy, cost or durability.
- That operators would bid per kg, or that customers would tender on per-kg terms.
- Real savings, prices or market shares; real operator behaviour.
- That Europress may share forecasts from compactor data with operators (data ownership and consent).
- Seasonal effects and multi-year dynamics.
