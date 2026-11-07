# OpenWeight: customer value, business case and productisation in SMART

Since AI 2026, Europress challenge, deliverable 3. Draft of 7 Nov 2026.

**Read this first.** All data figures come from the challenge's synthetic dataset. All prices, fees, adoption rates
and cash flows are hypothetical model inputs or results, not forecasts. Each number carries an evidence tag in
brackets (observed, estimated, simulated or hypothetical) and a source number [S1] to [S16], listed at the end.
"Observed" means observed in the synthetic data, a public source or the challenge lead.

**In one paragraph.** Customers pay for truck visits, not tonnes. Only the incumbent operator knows how much a site
produces, so no challenger can safely offer a price per kg. OpenWeight puts a scale in every new compactor and gives
every operator the same weight data and site forecasts, with the customer's consent. Customers use it free. Operators
pay Europress €30 per weighed device per month. The bill stays on the operator's certified weighbridge. The team plans
with €1,000 per unit for the self-weighing hardware. At that cost €30 is the break-even fee: NPV +€0.18 M over ten
years, payback in year 9. The margin is thin, so the hardware cost is the main risk; a supplier quote comes first and
a pilot tests the rest.

---

## 1. The problem in numbers

| Fact | Value | Tag |
|---|---|---|
| Share of all charges that are per visit | 56.5 % (€3.58 M of €6.33 M) | observed [S3] |
| Lifts made under 60 % full | 33.4 %, about 1 in 3 | observed [S3] |
| Cost of a visit by fill (under 60 % / 60–90 % / 90 % or more) | €143 / €150 / €160 | observed [S4] |
| Cost per tonne in the same bands | €167 / €70 / €49 (3.4x) | estimated, tonnes from device weight [S4] |
| Forecast error for a site's monthly tonnage: incumbent (own history) vs challenger (peer sites) | ±10 % vs ±37 % (median) | estimated [S6] |
| Customers a challenger can safely bid per kg for today, simulated region | 0 of 19 | simulated [S5] |
| Property manager's working time spent on waste | about 3 % | observed (challenge lead) [S12] |
| Contract length | about 3 years, retendered mostly on price | observed (challenge lead) [S12] |

A visit costs about the same whether the container is half empty or full. So a half-empty visit costs the customer
more than three times as much per tonne. The incumbent has no reason to drive less: it is paid per visit. HSY's
logistics manager put it plainly: "the transport company that does the work does not directly save, it may even lose"
(observed [S12]).

The customer cannot fix this alone. The weight sits with the operator who bills, and a property manager has little
time for waste. A challenger cannot fix it either. Without the site's history its forecast is ±37 % off, so a per-kg
bid carries a large risk premium and loses to the per-visit price. This is an information asymmetry, not a technology
gap.

Real data points the same way. In HSY's municipal mixed-waste collection (crane-emptied containers, not compactors),
about a third of emptyings happened below 50 % fill, and fill-level sensors paid off only with a changed cost
structure, with sensors as a paid add-on [R1]. The billing model, not the sensor, is the problem.

**Why Europress's current services are not enough.** SMART fill-level sensing and automatic pickup calls reduce
visits, but they work against the incumbent's per-visit income, so incumbents argue against them. SMART Insights
reaches only about 15 % of the base (observed [S12]) and shows data without the weight. Without the weight, savings
cannot be proven and invoices cannot be checked. Scaletipper X1 weighs bin tips, not the whole container. A platform
scale costs about as much as the compactor (observed, challenge lead [S12]).

## 2. What OpenWeight does

**The weight.** Every new COMBI compactor gets the H7 hydraulic self-lift, fitted at the factory. One cylinder on
the unit's own power pack lifts the door end about 10 mm. The pressure gives the weight of the waste. A two-end
version (H7-2) is an option for higher accuracy. DUO containers have no hydraulics, so for DUO the hopper weighing
plate (H1) or weighing rails (H5) remain the options. The COMBI/DUO split of new units is unknown (no data); the business model assumes all ~1,200
new units a year are weighed.

**The rule for billing.** We bill by the real scales. The hydraulic scale gives estimates. Every bill stays on the
operator's certified weighbridge, as today (Directive 2014/31/EU). The device weight is used for planning, forecasts
and cross-checks, and each unit is calibrated by the weighbridge tickets the operator shares. Expected accuracy is
±4.4 % (1σ) after 10 tickets, about ±10 % without tickets; target ≤5 % (estimated, untested [S9]).

**Three parties.**

| Party | Gives | Gets | Pays |
|---|---|---|---|
| Customer | Consent to share its weight profile with bidders, per tender | Plain-language reports, contract follow-up, a prompt to tender per kg | Nothing |
| Operator (incumbent or challenger) | Weighbridge tickets for calibration | Site forecasts, weight-triggered lift orders, tender packages | €30 per weighed device per month; €500 per tender package |
| Europress | The H7 hardware and the platform | Service income, more machine sales, a role in every tender | Funds H7 capex and upkeep |

**Why Europress, not a transport company.** Europress is not a party to transport or treatment contracts [S12]. It
does not drive trucks and does not want to (observed, challenge lead [S12]). If one operator held the data, it would
rebuild the same monopoly. A neutral device maker can sell the same data to every operator on equal terms, and it
already has the device and the SMART connection on every site.

Research on procurement auctions supports the core claim. In German railway tenders, the incumbent's dominance came
mainly from better information, not lower cost: in the authors' counterfactual, removing the bidders' strategic
response to the information gap raised the chance of picking the most efficient bidder by more than 40 percentage
points [R2]. In US highway auctions, releasing public cost information
reduced the spread of bids, most where cost uncertainty was largest [R3].

## 3. Customer value

| Lever (per device per year) | Value | Tag |
|---|---|---|
| Avoidable visits | €686–1,469 | simulated [S7] |
| Tonnes priced above peer sites | about €1,278 | estimated [S7] |
| Invoiced above the contract terms | about €301 | observed (kit calculator) [S7] |
| Fewer visits with a weight trigger, fleet-wide | 6–18 % | simulated [S8] |

The levers overlap partly (fewer visits also lowers cost per tonne), so they must not be added up. The team's
earlier single figure of about €1,900 is not used for that reason.

**One simulated region (FI-01), one tender round, €30 fee included (€3.9 per tonne):**

| | Today | With OpenWeight | Tag |
|---|---|---|---|
| Customer cost per tonne | €113.1 | about €99.6 (−12 %) | observed → simulated [S5] |
| Visits in the region | 3,845 | 3,102 (−19 %) | simulated [S5] |
| Customers contestable per kg | 0 of 19 | 19 of 19 | simulated [S5] |
| Customers who switch operator | | 9 | simulated [S5] |

The −19 % visits is for this region only. The fleet-wide figure is 6–18 % (6 % is the dataset's own label for
premature lifts, 18 % our model; per-device correlation r = 0.85 [S8]).

**Visibility between tenders.** The customer also sees whether the contract is kept. For the showcase customer:
68.3 % of lifts on time, 93.9 % of weighbridge tickets shared, 24 of 712 invoice lines differing from the contract
(observed [S10]). Differences are prompts for review, not accusations.

## 4. Operator value and the €30 fee

The operator gets two things. First, the incumbent's information advantage disappears: any operator can bid per kg
without a risk premium. Second, it runs fuller trucks. Under per-kg pricing a full load is the operator's gain, not
its loss.

| Per device per year | Value | Tag |
|---|---|---|
| Visits per device | 41 | observed [S2] |
| Fewer visits with a weight trigger | 6–18 % | simulated [S8] |
| Operator's cost of an avoided visit | €60–116 | estimated [S13] |
| Hard gain from avoided visits (low / mid / high) | €150 / €437 / €862 | estimated [S2] |
| Team estimate of the full gain, incl. removed pricing risk | €1,360 | hypothetical [S2] |
| Operator profit per device today (median spend €10,220 × margin 2.7–8.0 %) | €276–818 | observed + estimated [S2] |

| Fee | Per year | Share of the mid hard gain | Share of the full gain | Share of today's profit per device |
|---|---|---|---|---|
| €20 | €240 | 55 % | 18 % | 29–87 % |
| €30 | €360 | 82 % | 26 % | 44–130 % |

(hypothetical [S2])

€10,220 is the customer's median yearly spend per device, not the operator's revenue after pass-through costs.
Operator margins are company-wide: L&T 8.0 % in 2025 and −0.8 % in Q1/2026, Stena Recycling about 2.7 %, Remeo
−3.7 % (observed [S14]).

**€30 is a real ask.** It takes most of the gain an operator can measure in year one (fewer visits). A thin-margin
operator would pay more in fees than it earns on the device today. So the sales pitch is "you win per-kg contracts
and run fuller trucks", not "you save money". €30 is about a quarter of the operator's full gain, the same share the
team document used. Whether operators pay it is untested; it is a pilot hypothesis.

## 5. Europress: business model and cash flow

**Revenue and cost lines** (all hypothetical [S1]). Ten years, 8 % discount rate. 1,200 new units a year, all
weighed. Adoption by operators 60 %, reached linearly over 4 years. Tender packages €500 × 2.5 bidders × 35 % of
contracts, retendered every 3 years. Extra machine sales +5 % of new units × €22,500 × 25 % margin. Fixed cost
€400k a year, platform €26 per unit a year, plus H7 capex and upkeep per unit. **H7 capex €1,000 per new unit (team
decision, planning figure) and upkeep €73 a year (Part 1 midpoint)**; Part 1's estimate range is shown as scenarios.

**NPV over 10 years (€ M) and payback year** (hypothetical [S1]):

| Scenario | €20 | €25 | €30 | Break-even fee |
|---|---|---|---|---|
| **Base: H7 €1,000, upkeep €73 (team decision)** | −2.46 (never) | −1.14 (y10) | **+0.18 (y9)** | **€30** |
| Team document (H7 €825, upkeep €50) | −0.15 (y9) | +1.17 (y8) | +2.49 (y7) | €21 |
| Part 1 cheap H7 (€800, upkeep €39) | +0.49 (y9) | +1.80 (y8) | +3.12 (y7) | €19 |
| Part 1 mid H7 (€1,585, upkeep €73) | −7.17 (never) | −5.85 (never) | −4.53 (never) | €48 |
| Part 1 dear H7 (€2,370, upkeep €106) | −14.78 | −13.46 | −12.15 | €77 |
| Base, adoption 40 % | −4.22 | −3.34 | −2.46 | €44 |
| Base, no tender packages | −7.80 | −6.48 | −5.16 | €50 |
| Base, no extra machine sales | −4.00 | −2.68 | −1.36 (y10) | €36 |

**What the table says, plainly.**

- The team document's model is reproduced exactly: at €30 and H7 €825 it gives NPV +€2.49 M, deepest cumulative
  −€2.94 M, payback in year 7 [S1].
- **Base (H7 €1,000, team decision): at €30 NPV is +€0.18 M, payback in year 9, deepest cumulative −€3.83 M.**
  It needs at least 59 % of weighed units with a paying operator. €30 is the break-even fee, the lowest that works;
  €20 gives −€2.46 M (hypothetical [S1]).
- €825 is the midpoint of a parts-only range. Part 1's factory-fit estimate is €800–2,370 capex (mid €1,585)
  plus €39–106 a year upkeep (estimated [S9]). At Part 1's mid cost NPV is −€4.53 M at €30 and the plan never pays
  back; at the cheap end (€800, upkeep €39) it is +€3.12 M.
- **The margin is thin:** at €30, NPV stays at zero or above only if H7 capex is at most €1,020 (upkeep €73)
  or €1,130 (upkeep €50) (hypothetical [S1]), just above the €1,000 planning figure. At €20 the limit is €690,
  below even our cheapest estimate. That is why the fee is €30 and not €20.
- Tender packages and extra machine sales carry a large share of the result. Revenue is fee × adoption, so a higher
  fee only helps if it does not cut adoption by more than a third.

**This is the main risk of the business case.** The €1,000 planning figure sits at the cheap end of Part 1's range
and only about 2 % below the ~€1,020 break-even cost. A supplier quote for the self-lift is the first thing to confirm, then a
pilot, before any fleet-wide rollout. Charging part of H7 in the machine price would lower the fee needed, but the challenge lead said customers
are price-sensitive and today's weighing adds about 20 % to the price (observed [S12]), so it is not modelled.

**Why customers do not pay.** If customers had to pay for weighing, some would opt out. An operator will not move
its customers to per-kg pricing if some sites are unweighed. In the team's earlier model, even 10 % opt-outs remove
most of the gain of charging customers (estimated, older model version [S13]).

## 6. Productisation in SMART

**The offer.** OpenWeight is a SMART add-on subscription sold to operators: €30 per weighed device per month, plus
€500 per tender package. The customer side is free and comes with every new weighed compactor.

**Data flows.**

| Step | From → to | Content |
|---|---|---|
| 1 | Compactor → SMART cloud | Fill level, ram pressure, compaction cycles (today); H7 lift pressure and weight estimate (new) |
| 2 | Operator → SMART cloud | Shared weighbridge tickets, used only to calibrate each unit and to cross-check |
| 3 | OpenWeight engine | Per-unit calibration, site tonnage forecasts with ranges, contract and invoice cross-check |
| 4 | → Customer | Plain-language report: what happened, is the contract kept, should you tender |
| 5 | → Operator | Forecast API to price per kg; weight-triggered lift orders |
| 6 | → Bidding operators (with consent) | Tender package: kg per visit (P10/P50/P90), fill rate, seasonality, 12-month forecast |

**Who pays.** In two-sided platforms the price structure matters, and one side is often subsidised [R4]. That is why
customers use OpenWeight free and operators pay.

**Consent.** The customer owns its data. Sharing the weight profile with bidders is a consent step, given per tender.

**Human approval.** Every recommendation is a proposal with `requires_human_approval: true`. Nothing is sent or
executed automatically. The demo's proposal payload (`openweight.proposal.v1`) keeps the starter kit's
recommendation fields (evidence observed / estimated / hypothetical, not proven) and adds ours. AI-written report
text is checked against computed numbers; the numbers never come from the language model.

**Safety interlock.** A pickup is blocked in SMART until the lift cylinder is retracted.

**Sales channel.** Europress sells to operators, as some already resell SMART Insights to retail chains to win
contracts [S12]. Once per-kg pricing rewards full loads, operators have a reason to recommend Europress compactors.
That step is a hypothesis.

## 7. Pilot proposal

Before a fleet-wide rollout, a pilot of about 1,000 new units with one challenger operator over two years.

| Question | What the pilot measures | Pass condition (team proposal, hypothetical) |
|---|---|---|
| Can H7 be built for about €1,000? | Supplier quotes for cylinder, valve section and sensor; factory-fit time | Capex ≤ €1,020 at upkeep ≤ €73 |
| Is H7 accurate enough? | Known test loads at different positions; device weight vs weighbridge tickets | 1σ ≤ 5 % after 10 tickets |
| Do operators pay €30? | Signed operator subscriptions | Adoption on track for 60 % |
| Do customers consent and tender per kg? | Consent rate; tenders run on per-kg terms | Most customers consent |
| Does a challenger win with the data? | Bids and wins in the pilot region | Per-kg bids beat per-visit prices |

If operators do not join, Europress stops the pilot at a loss of about €1.5 M in the team model (hypothetical [S13]).
That figure uses H7 at €825; at the €1,000 base or higher the loss is larger, which is one more reason to get the
quote first.

## 8. Risks and what is untested

| Risk | Status | Answer |
|---|---|---|
| **H7 cost above about €1,000** | Biggest risk. Above ~€1,020 €30 no longer pays back; Part 1's mid estimate €1,585 gives NPV −€4.53 M | Supplier quote first; pilot |
| Operators will not pay €30 | Untested; no reference point | Pitch on contracts won and risk premium removed; pilot |
| Adoption below 60 % | A guess. At the base the plan needs ≥ 59 % paying at €30; at 40 % NPV is −€2.46 M [S1] | Pilot |
| H7 physics in the field | Untested: centre of mass, sideways tipping on a narrow three-point support, ice or debris under the runner fronts (only about 1.8 mm of lift at 1 m from the pivot) [S9] | Test loads; contact check; pilot |
| CE marking | A self-lifting compactor is a new machine function and needs a CE risk assessment (Machinery Directive 2006/42/EC; Regulation (EU) 2023/1230 from 20 Jan 2027) | Risk assessment before the pilot |
| DUO not costed | H7 is COMBI only; DUO uses H1 or H5. The COMBI/DUO split is unknown; the model assumes all 1,200 new units are weighed at the H7 cost | Cost H1/H5 for DUO |
| Customer consent | Assumed, not asked | Measure in the pilot |
| Incumbent reaction | Not modelled | Same service on equal terms for all operators |
| Market concentration | In the simulation it can rise (HHI about 5,350 → 6,170) [S5] | Watch in the pilot |
| All market numbers are synthetic | One region, one tender round, closed-form bids | Real tender data from the pilot |

Manufacturers that invest in services often see costs rise without matching returns [R5]. The supplier quote
for H7 and the pilot gates are our answer to that risk.

**What we will not do.** No route optimisation: Europress does not want to enter transport, and direct integration
with operators has not worked [S12]. No billing by device weight: the certified weighbridge stays the bill. No
municipal waste: there the customer cannot choose the operator. Biowaste is left out of the business claims.

## 9. Roadmap

1. **Now:** supplier quote for H7 (confirm the €1,000 planning figure); CE risk assessment; cost H1/H5 for DUO.
2. **Pilot (2 years):** about 1,000 new COMBI units, one challenger, the pass conditions in §7.
3. **Rollout:** H7 on every new COMBI; DUO with H1 or H5 if the pilot supports it; H7-2 where higher accuracy pays.
4. **Older fleet (for now not in the plan):** a virtual scale could later estimate weights for the existing base of
   about 20,000 units (observed, challenge lead [S12]) from fill level and ram pressure, calibrated by weighbridge
   tickets. H7 retrofit costs €1,994–6,168 per unit (estimated [S9]), so it is not proposed.

---

## Sources

- [S1] `PRICING.md`; `pipeline/fullload/pricing.py`; `pipeline/fullload/params.yaml` (`pricing`); bundle
  `pricing.headline` (`npv_30_eur`, `npv_20_eur`, `team_npv_eur`, `team_payback_year`, `break_even_fee`),
  `pricing.max_h7_capex_eur`, `pricing.scenarios`, `pricing.parity`.
- [S2] Bundle `pricing.operator` (`visits_per_device`, `fewer_visits_pct`, `hard_gain_eur`, `team_value_eur`,
  `spend_median_eur`, `profit_per_device_today_eur`, `by_fee`); `PRICING.md` operator table.
- [S3] Bundle `fleet.trip_share_pct`, `fleet.gross_charges_eur`, `fleet.trip_charges_eur`,
  `fleet.low_fill_lift_share_pct`.
- [S4] Bundle `fleet.visit_cost_by_fill` (`visit_eur`, `eur_per_t`; tonnes are device estimates).
- [S5] Bundle `market.headline` (`cost_per_t_before` 113.1, `cost_per_t_after` 99.55, `lifts_before`,
  `lifts_after`, `contestable_before`, `contestable_after`, `accounts_switched`), `market.params`
  (`europress_fee_cents_per_t` 390); HHI from `LIMITATIONS.md` §4.
- [S6] Bundle `forecast.own_history_error_median_pct`, `forecast.peer_error_median_pct`.
- [S7] Bundle `value_per_device.rows` (`avoidable_trips`, `expensive_tonnes`, `invoice_differences`).
- [S8] Bundle `validation.trips_check` (`labelled_premature_pct` 6.1, `model_removed_pct` 18.1,
  `per_device_pearson` 0.852).
- [S9] `part1/WEIGHING_CONCEPT.md` §19 (H7 statics, error budget §19.5, safety §19.6, retrofit §19.3);
  `part1/installed_cost.json`; bundle `pricing.h7_cost`; `MASTER.md` §C2.
- [S10] Bundle `hero.service_check`.
- [S11] `reviews/OPENWEIGHT_PDF_FIXES.md` (wording rules, Directive 2014/31/EU, CE note).
- [S12] Challenge lead's comments 6–7 Nov 2026 and public sources as recorded in `LIITE_perustelut.md` §2.4–2.12,
  §7.5, §8.3 and `PRODUCT.md` §2; HSY logistics manager's email 26 Jun 2026; starter kit `START_HERE.md`.
- [S13] `LIITE_perustelut.md` §1.2 and §9 (cost of an avoided visit), §3.2 (opt-outs, older model), §7.3 (pilot
  loss); `MASTER.md` §C3–C4.
- [S14] `LIITE_perustelut.md` §6.2 (L&T Q1/2026 interim report, Asiakastieto, Finder); `MASTER.md` §C3.
- [S15] Team document `OpenWeight.pdf` (structure, three-party loop, pilot design, what we will not do).
- [S16] `MASTER.md` §A–C, §F (agreed numbers and recommended answers).

## References

- [R1] Paananen, P. (2024). Evaluating the economic impact of implementing fill level sensors in HSY municipal solid
  waste collection. Master's thesis, LUT University. https://lutpub.lut.fi/handle/10024/167131
- [R2] Carnehl, C. & Weiergraeber, S. (2023). Bidder asymmetries in procurement auctions: Efficiency vs. information –
  Evidence from railway passenger services. International Journal of Industrial Organization 87, 102902.
  doi:10.1016/j.ijindorg.2022.102902
- [R3] De Silva, D.G., Dunne, T., Kankanamge, A. & Kosmopoulou, G. (2008). The impact of public information on
  bidding in highway procurement auctions. European Economic Review 52(1), 150–181.
- [R4] Rochet, J.-C. & Tirole, J. (2003). Platform competition in two-sided markets. Journal of the European Economic
  Association 1(4), 990–1029.
- [R5] Gebauer, H., Fleisch, E. & Friedli, T. (2005). Overcoming the service paradox in manufacturing companies.
  European Management Journal 23(1), 14–26. doi:10.1016/j.emj.2004.12.006
