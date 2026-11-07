# The operator fee: €30, not €20

Decided 7 Nov 2026 evening. All numbers are hypothetical model results on synthetic data, computed by
`pipeline/fullload/pricing.py` (inputs in `pipeline/fullload/params.yaml`, `pricing`) and shown in the bundle under
`pricing`. Reproduce: `.venv/bin/fullload build`, then read `web/public/data/bundle.json` → `pricing`. The browser
copy of the model (Business detail screen) is checked against Python by `npm run parity`.

## Recommendation

**Operators pay €30 per weighed device per month.** Customers pay nothing. At €20 the plan never pays back once
every new compactor carries the hydraulic self-lift. At €30 it pays back in year 7 with the team document's H7 cost
(€825). With our own installed-cost estimate it does so only if the self-lift is built for **at most about
€1,020** per unit. That design-to-cost target is now the single biggest business risk.

## The model

The team document's cash-flow model (LIITE §6.3, `analysis/final_v2.py`) is reproduced exactly: at €30 and H7
€825 it gives NPV +€2.49 M at 8 %, deepest −€2.94 M, cumulative +€6.41 M, payback in year 7 (a test checks this).
Per year, with every new unit weighed (1,200 a year):

- **Fees:** weighed units × adoption (60 %, reached linearly in 4 years) × fee × 12.
- **Tender packages:** €500 × 2.5 bidders × 35 % of contracts, retendered every 3 years.
- **Extra machine sales:** +5 % of new units × €22,500 × 25 % margin.
- **Costs:** €400k fixed, plus €26 platform and the H7 upkeep per weighed unit.
- **Investment:** H7 capex for each new unit.

The only change from the team model is the H7 cost. We use Part 1's factory-fit estimate
(`part1/installed_cost.json`), split into capex (€800–2,370, mid **€1,585**) and upkeep (€39–106 a year, mid
€73). The team's €825 is the midpoint of a parts-only range. The H7 review said not to cite it as the device cost.

## Europress: NPV over 10 years (€ M) and payback year

| Scenario | €20 | €25 | €30 | Break-even fee |
|---|---|---|---|---|
| Team document (H7 €825, upkeep €50) | −0.15 (y9) | +1.17 (y8) | **+2.49 (y7)** | €21 |
| Part 1 cheap H7 (€800, upkeep €39) | +0.49 (y9) | +1.80 (y8) | +3.12 (y7) | €19 |
| **Part 1 mid H7 (€1,585, upkeep €73)** | −7.17 (never) | −5.85 (never) | **−4.53 (never)** | **€48** |
| Part 1 dear H7 (€2,370, upkeep €106) | −14.78 | −13.46 | −12.15 | €77 |
| Mid H7, adoption 40 % | −8.93 | −8.05 | −7.17 | €71 |
| Mid H7, no tender packages | −12.51 | −11.19 | −9.87 | €68 |
| Mid H7, no extra machine sales | −8.71 | −7.39 | −6.07 | €54 |

**The most H7 can cost per unit (capex) for NPV ≥ 0:** €690 at €20, €850 at €25, **€1,020 at €30**.

The table shows four things:

- At **€20** the plan works only if the self-lift costs about €700 or less. That is below even our cheapest
  estimate once upkeep is counted. Payback is no earlier than year 9.
- At **€30** there is room for a self-lift of about €1,000. That is reachable at the cheap end of Part 1, where
  the parts alone are €550–1,100.
- The tender packages and extra machine sales carry a large share of the result. Without packages, no fee up to
  €60 pays back with the mid H7 cost.
- Revenue is fee × adoption, so €30 at 40 % adoption earns the same as €20 at 60 %. A higher fee only helps if it
  does not cut adoption by more than a third.

## The operator: can it afford €30?

These figures are per device per year, from our trips model and the dataset's invoices.

| | Value |
|---|---|
| Visits per device | 41 |
| Fewer visits with a weight trigger | 6–18 % (dataset label to our model) |
| Operator's cost of an avoided visit | €60–116 (LIITE §1.2, corrected) |
| **Hard gain from avoided visits** | **€150 – €437 (mid) – €862** |
| Team estimate of the full operator gain (incl. pricing risk) | €1,360 |
| Operator profit per device today (median revenue €10,220 × 2.7–8.0 % margin) | €276–818 |

| Fee | Per year | Share of the mid hard gain | Share of the team's full gain | Share of today's profit per device |
|---|---|---|---|---|
| €20 | €240 | 55 % | 18 % | 29–87 % |
| €30 | €360 | 82 % | 26 % | 44–130 % |

What this means for the operator:

- **€30 is a real ask.** It takes most of the gain the operator can measure in its first year, which is fewer
  visits. Only the pricing-risk gain, from winning per-kg tenders without a risk premium, makes it clearly worth
  paying.
- **€30 is about a quarter of the operator's full gain.** That is the same share the team document used
  (25 % of €1,400).
- **A thin-margin operator** (2.7 %) would pay more in fees than it earns on the device today. So the sales pitch
  is "you win contracts and run fuller trucks", not "you save money".

## Why €30

1. Under the agreed architecture, where every new unit weighs itself, Europress carries the hardware. €20 does not
   cover it at any cost estimate we can defend.
2. €30 is the team document's number, at 25 % of the operator's gain, so the pitch, the PDF and the demo agree.
3. The operator case at €30 holds only on the full gain (pricing risk plus visits). It is a business case to
   prove in a pilot, not a given. Say so.

## What would change the answer

- **H7 at €1,000 or less in production.** This is the condition for €30 to work. A supplier quote is the first
  thing to get, and ENGINEER_QUESTIONS 11 and 12 cover it.
- **Charging part of the H7 in the machine price.** This would allow a lower operator fee. Tommi said today's
  weighing adds ~20 % to the price and customers are price-sensitive, so it is not modelled.
- **Adoption below 40 %.** No fee in the range pays back with the mid H7 cost.
- **Fee per tonne instead of per device.** The model is per device. A per-tonne fee shifts risk to Europress on
  low-volume sites and is not modelled.

## Limits

Model results, not forecasts. Adoption, the tender-package uptake, extra machine sales and the margin are guesses
(LIITE §6.3). Every weighed unit is assumed active for all 10 years (optimistic). The data is synthetic, and
operator margins are company-wide, not compactor-specific.
