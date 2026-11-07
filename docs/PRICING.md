# The operator fee: €30, not €20

Decided 7 Nov 2026 evening. All numbers are hypothetical model results on synthetic data, computed by
`pipeline/fullload/pricing.py` (inputs in `pipeline/fullload/params.yaml`, `pricing`) and shown in the bundle under
`pricing`. Reproduce: `.venv/bin/fullload build`, then read `pipeline/out/bundle.json` → `pricing`. 

## Recommendation

**Operators pay €30 per weighed device per month.** Customers pay nothing. The team's planning figure for the
self-lift is **€1,000 per new unit** (decided 7 Nov evening; Part 1 estimates €800–2,370). On that basis:

- **€30 is the break-even fee.** NPV over 10 years is **+€0.18 M**, the plan pays back in **year 9**, and the
  deepest cash position is **−€3.83 M**. It needs at least **59 %** of weighed units with a paying operator.
- **€20 does not pay back** (NPV −€2.46 M). At €20 the self-lift would have to cost €690 or less.

So €30 is not a comfortable price; it is the lowest price that works. Every euro the self-lift costs above
~€1,020 makes it lose money, and every euro below makes it better: at €800 capex and €39 upkeep (Part 1's cheapest estimate)
€30 gives NPV +€3.1 M and payback in year 7.

## The model

The team document's cash-flow model (the structure of `docs/fi/analysis/final_v2.py`, run with LIITE §6.3's inputs: 1,200 new units a year, H7 €825, no cap on units; the script's own defaults are the older rails case, 10,000 units, NPV +€2.41 M) is reproduced exactly: at €30 and H7
€825 it gives NPV +€2.49 M at 8 %, deepest −€2.94 M, cumulative +€6.41 M, payback in year 7 (a test checks this).
Per year, with every new unit weighed (1,200 a year):

- **Fees:** weighed units × adoption (60 %, reached linearly in 4 years) × fee × 12.
- **Tender packages:** €500 × 2.5 bidders × 35 % of contracts, retendered every 3 years.
- **Extra machine sales:** +5 % of new units × €22,500 × 25 % margin.
- **Costs:** €400k fixed, plus €26 platform and the H7 upkeep per weighed unit.
- **Investment:** H7 capex for each new unit.

The only change from the team model is the H7 cost: capex **€1,000** (the team's planning figure) and upkeep
**€73** a year (Part 1 midpoint, €39–106). Part 1's full factory-fit estimate (`part1/installed_cost.json`) is
capex €800–2,370, mid €1,585; those are shown as scenarios. The team document's €825 is the midpoint of a
parts-only range and is shown only for comparison.

## Europress: NPV over 10 years (€ M) and payback year

| Scenario | €20 | €30 | Break-even fee | Paying share needed at €30 |
|---|---|---|---|---|
| **Base: H7 €1,000, upkeep €73** | −2.46 (never) | **+0.18 (y9)** | **€30** | **59 %** |
| Team document (H7 €825, upkeep €50) | −0.15 (y9) | +2.49 (y7) | €21 | 42 % |
| Part 1 cheap H7 (€800, upkeep €39) | +0.49 (y9) | +3.12 (y7) | €19 | 37 % |
| Part 1 mid H7 (€1,585, upkeep €73) | −7.17 (never) | −4.53 (never) | €48 | 95 % |
| Part 1 dear H7 (€2,370, upkeep €106) | −14.78 | −12.15 | €77 | not reached |
| Base, adoption 40 % | −4.22 | −2.46 | €44 | – |
| Base, no tender packages | −7.80 | −5.16 | €50 | 100 % |
| Base, no extra machine sales | −4.00 | −1.36 (y10) | €36 | 71 % |

**The most H7 can cost per unit (capex) for NPV ≥ 0:** €690 at €20, €850 at €25, **€1,020 at €30**.

The table shows four things:

- At **€20** the plan works only if the self-lift costs about €700 or less. Payback is no earlier than year 9.
- At **€30** a self-lift of €1,000 just pays back (year 9). It is reachable at the cheap end of Part 1, where the
  parts alone are €550–1,300 (the team document says €550–1,100).
- The tender packages and extra machine sales carry a large share of the result. Without packages the base case needs €50.
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

1. Under the agreed architecture, where every new unit weighs itself, Europress carries the hardware. At the
   €1,000 planning figure, €30 is exactly the break-even fee and €20 loses €2.5 M.
2. €30 is the team document's number, at 25 % of the operator's gain, so the pitch, the PDF and the demo agree.
3. The operator case at €30 holds only on the full gain (pricing risk plus visits). It is a business case to
   prove in a pilot, not a given. Say so.

## Recheck, 7 Nov night (two questions from the team)

Recomputed independently of `pricing.py`; the results match it.

**Is the data worth €30 a month to an operator?** Only where it bills per tonne, and not on every site. Its
measurable gain is fewer visits: 41 visits × 6–18 % × €60–116 = €150–860 a year (mid ~€440) against €360. It breaks
even when the weight trigger removes ≥ 10 % of visits at €88 per visit (≥ 15 % at €60); the fleet model gives 17 %.
Under per-visit billing, fewer visits are lost revenue for the operator, so the case rests on per-kg contracts. The
incumbent already has its own weighbridge history; a challenger needs the data most, at tender time (the €500 bid
pack). After winning, the live weight is still worth something to it for dispatch (full loads), which the
weighbridge cannot give.

**Does the fee pay for giving the weighing away?** Barely, and not by itself. Per weighed unit and year the fee
brings €117 after platform and upkeep (60 % paying), about €785 over a 10-year life at 8 %, against €1,000 of capex.
The tender packages (~€146 per unit and year) and extra machine sales make the plan pay back; without packages NPV is
−€5.16 M, without extra sales −€1.36 M. Fees alone would need ~€56 a month. Once the ramp is over the plan earns
about +€1.9 M a year (year 10); the 10-year NPV is small because of the four-year ramp and the yearly capex.

## What would change the answer

- **H7 above ~€1,020 in production** and €30 no longer pays back. A supplier quote is the first thing to get
  (ENGINEER_QUESTIONS 11 and 12).
- **Charging part of the H7 in the machine price.** This would allow a lower operator fee. Tommi said today's
  weighing adds ~20 % to the price and customers are price-sensitive, so it is not modelled.
- **Adoption below 59 %** at €30 and the base case loses money.
- **Fee per tonne instead of per device.** The model is per device. A per-tonne fee shifts risk to Europress on
  low-volume sites and is not modelled.

## Limits

Model results, not forecasts. Adoption, the tender-package uptake, extra machine sales and the margin are guesses
(LIITE §6.3). Every weighed unit is assumed active for all 10 years (optimistic). The data is synthetic, and
operator margins are company-wide, not compactor-specific.
