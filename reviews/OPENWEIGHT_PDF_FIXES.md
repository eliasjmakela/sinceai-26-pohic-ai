# OpenWeight.pdf: what to fix

For the author of `OpenWeight.pdf`. Checked on 7 Nov against `LIITE_perustelut.md`, the demo's numbers and two
independent reviews. The arithmetic in the PDF and LIITE is correct: every calculation was recomputed, and the
10-year cash-flow table was rebuilt exactly. The problems below are about *which* numbers and claims we use.

The full table with working: `reviews/LIITE_VS_OPENWEIGHT_CHECK.md`. The H7 review:
`reviews/SELF_WEIGHING_PAPER_REVIEW.md`.

## The rules for weight (agreed)

**Every new compactor weighs itself (hydraulic self-lift). We bill by the real scales; the hydraulic scale gives estimates.** The certified weighbridge stays the basis of
every bill, as today (EU Directive 2014/31/EU on non-automatic weighing instruments). The hydraulic scale in the
compactor gives planning weights and checks itself against the weighbridge tickets. It is not a legal-for-trade
scale. Every weight claim in the PDF should follow this rule.

## Must fix (the PDF disagrees with the demo)

1. **Business model: keep €30, use the €1,000 H7 base.** The €30 fee and "every new unit weighs itself" are now
   agreed (see `PRICING.md`). Our model reproduces the PDF's cash flow exactly (NPV 2.49 M€, year 7), but that rests
   on H7 at €825, a parts-only midpoint. The team now plans with **H7 €1,000 capex per new unit plus €73 a year
   upkeep**. Replace the PDF's headline with: **"NPV +0.18 M€ over 10 years at 8 %, payback year 9, deepest cash
   −3.83 M€; €30 is the break-even fee and needs ≥ 59 % of weighed units paying (at €20: −2.46 M€)."** Add one line:
   **"The margin is thin: above ~€1,020 per unit €30 no longer pays back (Part 1's mid estimate €1,585 gives
   −4.53 M€), so a supplier quote for the self-lift is the first thing to confirm."** Replace "break-even
   €21/month" with €30. The model assumes all ~1,200 new units a year are weighed (the COMBI/DUO split is unknown).
2. **The hydraulic scale's numbers.** Do not use these, the review found them unsupported:
   - "±3 % when full" (and "3.1 t ± 0.1 t"). Use: **target 1σ ≤ 5 % after 10 weighbridge tickets, 4.4 % in our
     error budget, untested.** Without tickets the error is about 10 %.
   - "€550–1,100" and the €825 derived from it as the device cost. That is parts only. Use: **€800–2,370 capex
     per new unit (factory fit) plus €39–106 a year upkeep** (Part 1). Recompute the €190 a year weighing cost.
   - "Fits every compactor". Use: **COMBI, new units only.** DUO is not costed; retrofit costs €1,994–6,168.
   - "Europress's own IP". Use: "We found no compactor that lifts itself to weigh; similar weighing exists on trucks
     (Hiab patent US 2020/0096383)."
3. **The virtual scale (p7).** Fine to leave it out: every new unit weighs itself. If it stays in "what we won't
   do", add "for now; it could later estimate weights on the older fleet" so judges don't read it as a gap.
4. **Market figures.** Use the demo's numbers:

   | PDF | Use instead |
   |---|---|
   | forecast error 21 % vs 9 % | **±37 % vs ±10 %** (without vs with the site's own data, monthly tonnes) |
   | 18 % fewer visits | **6–18 % fewer visits** (6 % is the dataset's own label, 18 % our model) |
   | (missing) | **customer cost per tonne €113.1 → €99.6, −12 %** in the simulated region, with the €30 fee (€3.9/t) |
   | demo saving €2,100–3,400 a year | remove: LIITE itself calls it an invented placeholder |

## Must fix (errors LIITE §9 already lists)

5. Sensor error is **±50–75 kg of waste**, not ±30 kg (±30 kg is the cylinder force, about 85 kg of waste per bar).
6. A wasted visit is worth **€60–116**, not €130.
7. The pilot loss is **about €1.5 M**, not about €1 M. Drop "€5–11 M" (from older model versions).

## Should fix (overstated or unsourced)

8. Customer gain "~€1,900 per device per year" adds levers that overlap. LIITE's own worst case is €1.1–1.3k.
   Give a range and say the levers overlap.
9. Operator gain "~€1,400": the €1,930 pricing-risk figure points to LIITE §2.3, which does not derive it. Show the
   derivation, or say "removes the risk premium on per-kg bids" without a € figure.
10. "€530–1,300" for load cells cites LIITE §6.3, which does not exist. Source it or drop it.
11. "10–25 % opt-outs wipe out the gain" comes from an older model. Say "even 10 % opt-outs remove most of the gain".
12. "The incumbent wins every third year" has no figure behind it. Say "contracts are retendered about every 3 years,
    mostly on price".
13. "Operators earn €0–800 per device": €10,200 is right (it is the median yearly invoice per device), but it is
    the customer's spend, not the operator's revenue after pass-through costs. Say so in one clause.
14. L&T Q1 margin: −0.84 %, so write −0.8 %, not −0.9 %.

## Sources and wording

15. The Europress profit figure is cited as PRH, but LIITE says it came from Orbis (academic licence, not usable).
    Fetch it from PRH or drop the comparison. It also compares a cash flow with profit before tax.
16. "Varmennettu paino" (p4) reads as a legal-for-trade weight. Use "vaa'an kuittiin verrattu paino" (weight checked
    against the weighbridge ticket). "Kalibrointi" → "kalibrointi vaakakuittien avulla".
17. Name the directive: billing stays on the certified weighbridge under **Directive 2014/31/EU**.
18. Safety list (p5): add that a self-lifting compactor is a new machine function and **needs a CE risk assessment**
    (Machinery Directive 2006/42/EC; Regulation (EU) 2023/1230 from 20 Jan 2027). Also add the two new risks:
    sideways tipping on the narrow three-point support, and ice or debris under the runner fronts (only ~1.8 mm of
    lift at 1 m from the pivot).
19. Baselines (p8): the €240 C2 regret is from the kit's dev split, not validation. The "(recall 0.59)" in the
    improvement column reads as our result; it is the kit's.
20. "Calculations in `analysis/`" (p1, p8): those scripts are not in the repo. Add them or point to the repo pipeline.
21. Keep SMART's "37 % fewer lifts" claim visually apart from the "±37 %" forecast error; they are unrelated numbers.

## Fine as is

The physics and statics of the hydraulic lift (80 mm bore, ~120 bar at 60 kN, foot pressure), the kit baselines,
the ±3.3 % device-vs-weighbridge tolerance (say it is the kit's example), the interview quotes (HSY, ~3 % of a
property manager's time, Insights ~15 %), "1 in 3 lifts under 60 % full", and the up/down averaging that cancels
seal friction.

## References you can cite (verified to exist; use only for the claim given)

1. **Problem page:** Paananen, P. (2024). *Evaluating the economic impact of implementing fill level sensors in HSY
   municipal solid waste collection.* Master's thesis, LUT University. https://lutpub.lut.fi/handle/10024/167131 —
   in real HSY data about a third of emptyings happen below 50 % fill. Say it is crane-emptied municipal mixed-waste
   containers, not compactors. It also found sensors pay off only with a changed cost structure.
2. **Core claim:** Carnehl, C. & Weiergraeber, S. (2023). Bidder asymmetries in procurement auctions: Efficiency vs.
   information. *International Journal of Industrial Organization* 87, 102902 — the incumbent's dominance came mainly
   from better information, not lower cost; in a counterfactual, removing the bidders' strategic response to the
   information gap raised the chance of picking the most efficient bidder by more than 40 percentage points.
3. **Core claim, second source:** De Silva, D.G., Dunne, T., Kankanamge, A. & Kosmopoulou, G. (2008). The impact of
   public information on bidding in highway procurement auctions. *European Economic Review* 52(1), 150–181 —
   releasing public cost information narrowed the spread of bids, most where cost uncertainty was largest.
4. **Free for the customer:** Rochet, J.-C. & Tirole, J. (2003). Platform competition in two-sided markets. *Journal
   of the European Economic Association* 1(4), 990–1029 — on two-sided platforms one side is often subsidised.
5. **Risks:** Gebauer, H., Fleisch, E. & Friedli, T. (2005). Overcoming the service paradox in manufacturing
   companies. *European Management Journal* 23(1), 14–26 — service investment often raises costs without matching
   returns.

Skipped: the "temperature and ≤ 5 % review" for weighing. We could not identify a specific paper; our accuracy
figures come from our own error budget (Part 1 §19.5) and should be cited as such.
