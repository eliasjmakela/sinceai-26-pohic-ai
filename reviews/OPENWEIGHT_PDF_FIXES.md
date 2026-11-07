# OpenWeight.pdf: what to fix

For the author of `OpenWeight.pdf`. Checked on 7 Nov against `LIITE_perustelut.md`, the demo's numbers and two
independent reviews. The arithmetic in the PDF and LIITE is correct: every calculation was recomputed, and the
10-year cash-flow table was rebuilt exactly. The problems below are about *which* numbers and claims we use.

The full table with working: `reviews/LIITE_VS_OPENWEIGHT_CHECK.md`. The H7 review:
`reviews/SELF_WEIGHING_PAPER_REVIEW.md`.

## The one rule for weight

**We bill by the real scales. The hydraulic scale gives estimates.** The certified weighbridge stays the basis of
every bill, as today (EU Directive 2014/31/EU on non-automatic weighing instruments). The hydraulic scale in the
compactor gives planning weights and checks itself against the weighbridge tickets. It is not a legal-for-trade
scale. Every weight claim in the PDF should follow this rule.

## Must fix (the PDF disagrees with the demo)

1. **Business model.** The PDF uses €30 per device per month plus €500 per tender, and pays back in year 7. The demo
   uses **€20 per device per month and pays back in about 1.6 years** (business team assumptions). By the PDF's own
   sensitivity table, €20 gives NPV −0.15 M€, so judges would see two contradicting business cases. Agree one model
   with Elias before changing either document.
2. **The hydraulic scale's numbers.** Do not use these, the review found them unsupported:
   - "±3 % when full" (and "3.1 t ± 0.1 t"). Use: **target 1σ ≤ 5 % after 10 weighbridge tickets, 4.4 % in our
     error budget, untested.** Without tickets the error is about 10 %.
   - "€550–1,100" and the €825 derived from it as the device cost. That is parts only. Use: **€1,034–3,008
     installed, new units (factory fit).** Recompute the €190 a year weighing cost from this range.
   - "Fits every compactor". Use: **COMBI, new units only.** DUO is not costed; retrofit costs €1,994–6,168.
   - "Europress's own IP". Use: "We found no compactor that lifts itself to weigh; similar weighing exists on trucks
     (Hiab patent US 2020/0096383)."
3. **The "what we won't do" list (p7)** lists the virtual scale. The demo uses it: it estimates lifts from fill,
   compaction cycles and days since the last lift, trained on the units that weigh (about 8 % median error per lift,
   5.5 % per month). Remove it from the list, or agree with Elias that every unit gets a hydraulic scale. Your own
   line on p5, "±10–15 % is enough for pricing", supports keeping it.
4. **Market figures.** Use the demo's numbers:

   | PDF | Use instead |
   |---|---|
   | forecast error 21 % vs 9 % | **±37 % vs ±10 %** (without vs with the site's own data, monthly tonnes) |
   | 18 % fewer visits | **6–18 % fewer visits** (6 % is the dataset's own label, 18 % our model) |
   | (missing) | **customer cost per tonne €113 → €98, −13 %** (range −12 to −15 %) |
   | demo saving €2,100–3,400 a year | remove: LIITE itself calls it an invented placeholder |
   | installed base ~20,000 | agree one figure; the demo's business model uses 10,000 |

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
13. "Operators earn €0–800 per device": €10,200 is the customer's average cost (the median is €6,578), not the
    operator's revenue. Say so.
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
