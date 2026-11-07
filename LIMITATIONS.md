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

## 2. Weighing concept (Part 1, `part1/`)
- **Untested.** No hardware was built or measured; every accuracy figure is an estimate, a simulation target or a
  vendor claim. The team has no mechanical-engineering expertise; `part1/CLAIMS_LEDGER.md` lists every technical
  claim with its source and confidence, and `part1/ENGINEER_QUESTIONS.md` the questions for a Europress engineer.
- **Costs are ranges, mostly team estimates** (installed cost per device, 6-year lease, `part1/installed_cost.json`).
  Load-cell prices are single-unit list prices; volume prices could be much lower.
- **Chosen concept: H7 hydraulic self-lift on every new COMBI** (§2c). Its accuracy is an error-budget estimate:
  about ±10 % 1σ without tickets, **±4.4 % 1σ after 10 shared weighbridge tickets** (range 2.6–9.7 %), which
  calibrate each unit. Untested.
- **DUO containers have no hydraulics**; for DUO the hopper plate (H1) or weighing rails (H5) remain the options.
  The share of COMBI vs DUO in the ~1,200 new units a year is unknown (no data); the business model assumes all new
  units are weighed.
- **Prior art exists** for hopper-stage weighing, weighing rails and truck-side hydraulic weighing (patents listed in
  `part1/WEIGHING_CONCEPT.md` §11, §19). We claim no mechanical novelty; no freedom-to-operate check was done.
- **Not legal for trade.** Billing stays on the operator's certified weighbridge (EU Directive 2014/31/EU). The device
  weight is planning data and a cross-check.

## 2b. Virtual scale (`pipeline/fullload/virtual_scale.py`, roadmap only)
- **Not part of the product claim.** At most a roadmap item that could later estimate weights on older units.
- Simulated on synthetic data: a log-linear model (fill × volume, material, machine type, compaction cycles, days since
  the last lift) trained on 10 % reference devices estimates other devices' lift weights with ~8 % median error,
  ~7–8 % after 5 shared weighbridge tickets per device, ~5–6 % on monthly totals; fill alone ~16 %.
- **Likely optimistic**: the generator derives mass from similar quantities. Real pressure data was not available.
- A single ticket makes calibration worse (one noisy ratio); calibration needs ~5 tickets.
- The figures are **median** errors; as a 1σ the calibrated per-lift error is about 11 %.

## 2c. Hydraulic self-lift (H7, `part1/WEIGHING_CONCEPT.md` §19)
- Team idea, untested: the compactor lifts itself ~10 mm with its own hydraulics and weighs from cylinder pressure.
  Installed cost €1,034–3,008 factory-fit incl. 6 years' upkeep (team estimates; no supplier prices found): capex
  €800–2,370 (mid €1,585) plus upkeep €39–106 a year. The business case plans with €1,000 capex (team decision) and
  the €73/yr mid upkeep. Fitted to every new COMBI; retrofit not recommended. A
  two-end version (H7-2) is an option for higher accuracy. Accuracy target 1σ ≤ 5 % after 10 shared tickets (≤ 3 % lifting both ends, which needs a front
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
  advantage, route fit, route density, sensor error) until the business-case owner signs them off. The Europress fee is
  €3.9/t, the per-tonne equivalent of €30 per device per month (`PRICING.md`).
- **Result with the default assumptions and the €30 fee (€3.9/t)**: the customer's cost per tonne falls from €113.1
  to €99.6 (−12 %); visits in the region fall 19 % (fleet-wide the trips model gives 6–18 %). The sensitivity range
  was not recomputed for the €30 fee. **What is not robust**: who wins each tender. Each customer goes to the single best bid, so the number of
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
  least 3 devices and one fixed-schedule device (`pipeline/fullload/pick_heroes.py`). Its −30.8 % is not typical;
  the region-wide figure is about −12 %. Say so when presenting it.
- Per-device forecast errors are shown because errors partly cancel when devices are added up.

## 6. Premature-lift rule and operator scorecard
- The rule finds 71 % of labelled unjustified premature lifts (F1 0.81) and flags none of the justified ones; the
  kit's ML baseline finds more (F1 0.93) but flags 13 justified lifts and gives no reasons. We chose explainability.
- The scorecard's invoice-difference share scores weakly against the labels (0.32); treat it as indicative.

## 7. AI-summarized customer report
- Written by Claude (during development; no API call at runtime) as a template in `pipeline/fullload/reports/`;
  every figure is a placeholder filled from the computed fact sheet at build time, and the build rejects any number
  that is not in the facts. Wording and reasoning are not checked automatically, so a person must read it.

## 8. Business case (Business screen, `pipeline/fullload/value.py`, `pricing.py`, `PRICING.md`)
- **Value per device is recomputed from our pipeline** and compared with the business team's independent figures.
  Close: avoidable visits (ours €686–1,469 vs team €1,570), tonnes priced above peers (€1,278 vs €1,245).
  Higher in ours: operator pricing risk (€2,712 vs €1,930: our forecast-error gap is wider, 27 vs 12 percentage
  points, and it depends on the market parameters) and invoice above contract (€301 vs €100: the kit's B1 calculator
  leaves gaps, the same reason the scorecard's invoice metric is weak). Contamination is not recomputed.
- **The business model reproduces the team document's cash-flow model** (LIITE §6.3) in `pricing.py` (params.yaml
  `pricing`; all hypothetical). Operators pay €30 per weighed device per month; customers pay nothing.
  **Base: H7 €1,000 capex per new unit (team decision), upkeep €73/yr: NPV over 10 years at 8 % is +€0.18 M,
  payback year 9, deepest cash −€3.83 M**; it needs ≥ 59 % of weighed units paying. €30 is the break-even fee, the
  lowest that works; €20 gives −€2.46 M. The margin is thin: above ~€1,020 capex €30 loses money. Sensitivity:
  Part 1's mid installed cost (capex €1,585) gives −€4.53 M at €30 (break-even fee €48); its cheap end (€800) gives
  +€3.12 M. The team document's H7 €825 gives +€2.49 M, payback year 7. A supplier quote for the self-lift is the
  first thing to confirm. All ~1,200 new units a year are assumed weighed (COMBI/DUO split unknown).
- Tender packages and extra machine sales carry a large share of the result; extra machine sales is the most
  uncertain lever. €30 is 82 % of the operator's mid hard gain from fewer visits, a willingness-to-pay risk.

## 9. Not proven / untested (summary)
- That H7 (or any weighing design) reaches the stated accuracy, cost or durability, or can be built for the
  €1,000 planning cost (break-even ~€1,020 at €30).
- That operators would bid per kg, or that customers would tender on per-kg terms.
- Real savings, prices or market shares; real operator behaviour.
- That Europress may share forecasts from compactor data with operators (data ownership and consent).
- Seasonal effects and multi-year dynamics.
