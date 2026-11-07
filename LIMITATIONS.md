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
- **Stylised**: one region (FI-01, 19 customers, 3 operators + new entrants), one tender round, closed-form bids. No
  routing, capacity limits, learning or repeated games.
- **Assumptions are placeholders** (`pipeline/fullload/params.yaml`: cost share, margin, risk aversion, entrant
  advantage, route fit, route density, Europress fee, sensor error) until the business-case owner signs them off.
- **What is robust**: the customer's cost per tonne falls in every tested combination (€122.5 → €106–111/t,
  −9 to −13 %). **What is not**: who wins each tender. Each customer goes to the single best bid, so the number of
  customers switching ranges from 8 to 19 depending on the assumptions.
- **Concentration can rise.** With the default assumptions the efficient incumbent wins more volume (HHI ~5,200 →
  ~6,100). The competition effect shows as price discipline (customers a challenger can win: 0 → 19 of 19), not as
  lower concentration.
- **Today's price is observed and checked**: the invoiced amount matches the contract-expected amount to the cent for
  97.6 % of 1,586 validation-period collections (total +0.34 %; the rest are billing discrepancies). Contract
  collection cost per lift is close to constant per device (median coefficient of variation 0.09), which supports
  scaling trip costs with the number of lifts.

## 5. Showcase customer (beats 2–3)
- **Chosen by a fixed rule as the best case**: the largest simulated saving among customers in the region with at
  least 3 devices and one fixed-schedule device (`pipeline/fullload/pick_heroes.py`). Its −31.5 % is not typical;
  the region-wide figure is about −11 %. Say so when presenting it.
- Per-device forecast errors are shown because errors partly cancel when devices are added up.

## 6. Premature-lift rule and operator scorecard
- The rule finds 71 % of labelled unjustified premature lifts (F1 0.81) and flags none of the justified ones; the
  kit's ML baseline finds more (F1 0.93) but flags 13 justified lifts and gives no reasons. We chose explainability.
- The scorecard's invoice-difference share scores weakly against the labels (0.32); treat it as indicative.

## 7. AI-summarized customer report
- Written by Claude (during development; no API call at runtime) from the computed fact sheet and frozen in
  `pipeline/fullload/reports/`. The build checks that **every number** in the text appears in the facts; it does not
  check wording or reasoning, so a person must read it before it is shown.

## 8. Business case (beat 6, `pipeline/fullload/value.py`, `business.py`)
- **Value per device is recomputed from our pipeline** and compared with the business team's independent figures.
  Close: avoidable visits (ours €891–1,547 vs team €1,570), tonnes priced above peers (€1,455 vs €1,245).
  Higher in ours: operator pricing risk (€3,038 vs €1,930: our forecast-error gap is wider, 27 vs 12 percentage
  points, and it depends on the market parameters) and invoice above contract (€328 vs €100: the kit's B1 calculator
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
