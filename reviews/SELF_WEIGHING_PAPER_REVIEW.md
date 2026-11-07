# Review: "Self-weighing compactor: lift-based load measurement for CombiMax" (@Mike, 7 Nov 2026, 6 pp.)

Independent review for team OpenWeight/FullLoad. This is the English follow-up to the "Plus-malli" PDF
(`reviews/PLUS_MALLI_REVIEW.md`). It adds a Monte Carlo error table. Points already made in that review and in
`part1/WEIGHING_CONCEPT.md` §19 are only referenced here, not repeated. Check script: `/tmp/swcheck/mc.py` (not in repo).

## 1. What the paper claims

| Topic | Claim | Page |
|---|---|---|
| Principle | The rear cylinder lifts the rear ~10 mm about the front rails. W = (R − R₀)·L/x_w ("Plus"). "Pro" puts the whole unit on 3 cylinders, W = ΣR | 1–2 |
| Friction | R = A·(p_up + p_down)/2 cancels seal friction | 3 |
| Geometry | A 10 mm lift over 5.5 m is a 0.1° tilt; "tilt has no measurable effect" | 3 |
| Accuracy | 100,000-run Monte Carlo. Plus full (3 t): σ 3.2 %, 88 % within ±5 %. Plus half: σ 10 %, 39 %. Pro full: 99.9 %. With undetected rail contact: 52 %, bias −4.6 % | 3 |
| Requirements | Hardware 2–5 % of unit price (~€400–1,000) and ±5 %, both "Europress, on site" | 1 |
| Cost | Plus €550–1,100 (retail minus an assumed 50 %). Pro: "Plus + 2 front cylinders", no price | 4–5 |
| Procedure | Readings at tare, at the full alarm and nightly. Two-height lift check (20 and 30 mm) for rail contact | 1, 5 |
| Evidence | "Nothing here has been tested physically" | 5 |

## 2. Physics and numbers, recomputed

| # | Item | Check | Verdict |
|---|---|---|---|
| 1 | Plus statics | Same as §19.2. Correct if L, x₀ and x_w share one pivot | OK |
| 2 | Lateral position does not matter | True for 3-point support. **New gap:** the support triangle is narrow. Assume the rails are ~1 m apart (assumption). At the loaded CoG station (x/L ≈ 0.58) the triangle is only ±0.21 m wide. If an off-centre load (wet waste on one side) puts the CoG outside it, one rear rail stays on the ground. That is the "undetected contact" failure the paper calls its worst case | OK in principle, failure mode missed |
| 3 | Pressures | R₀ = 4,360·2.5/5.5 = 1,982 kg → **38.7 bar** (Ø80). Full 3 t → **83.4 bar**. 5 t at 4.2 m → **113 bar**, the same as §19 | Consistent |
| 4 | Sensor | 0.25 % FS of 160 bar = 0.4 bar. 1 bar = 51 kgf at the cylinder = 67 kg of waste (full) or 101 kg (half). §19 says 85 kg at x_w/L = 0.6 | Consistent |
| 5 | Tilt | θ = 0.104°, cos θ = 0.9999983 ✓. But the "< 0.01 mm" CoG shift is x(1 − cos θ). The real shift is h·sin θ ≈ **2.7 mm** for CoG height h = 1.5 m. That is still only ~0.07 % | Conclusion right, working wrong |
| 6 | Friction averaging | Valid for symmetric Coulomb friction only (as §19.5 says). Modelled as σ 0.5 % of force, with no temperature dependence. §19 puts winter friction as the high case | Plausible, untested |
| 7 | Monte Carlo | **Reproduced from the stated inputs:** Plus full σ 3.3 % / 86 %, half 10.1 % / 38 %, rail contact −4.7 % bias, Pro full 1.6 % / 99.8 %. The table is internally consistent. The CoG term alone (0.12 m / 4.2 m = 2.9 %) is ~90 % of the Plus variance. The "88 %" is therefore a restatement of the assumed σ_xw = 0.12 m, not a finding | Arithmetic OK, evidential value low |
| 8 | Half-fill CoG at 2.8 m | This assumes waste builds up from the press end. If it packs against the door first, x_w is larger and half-fill error is smaller. Unknown either way (ENGINEER_QUESTIONS 14) | Unsupported assumption |
| 9 | Two-height check (20 and 30 mm) vs stroke | Foot sits ≥30 mm above the rail when retracted, plus a 30 mm lift, = **60 mm before any uneven ground**. The paper gives a 50–80 mm stroke and a ~10 mm lift elsewhere. A 50 mm stroke cannot do the check, and 80 mm leaves 20 mm margin | **Internal contradiction** |
| 10 | Rail contact near the pivot | Lifting 10 mm at L raises the rail only 10·s/L. At s = 1 m that is 1.8 mm, and frame sag reduces it. Ice, mud or debris under the front third of the rails will often touch. Rails frozen to the ground can also bias the reading *high* (adhesion), which the paper does not cover | Risk under-modelled |
| 11 | Cost % | 550/20,000 = 2.75 %, 1,100/20,000 = 5.5 % ✓. The top end exceeds the paper's own 2–5 % target | Arithmetic OK |

**Error terms the paper does not model** (all are in §19.5 or new):

- tare change from rain, ice or residue (1–6 %), and roof snow (0.7–1.4 t);
- sensor span and temperature drift (the 0.25 % FS spec is usually at 25 °C, and the total error band over −30…+30 °C is larger);
- pivot shift *between* tare and reading (the paper uses one pivot σ for both, so the machine term cancels exactly);
- ground slope (2 % slope with waste CoG at 1.5 m height ≈ 0.7 %);
- end-on wind (≈ 0.5 % at 10 m/s, ≈ 2 % in gusts at 20 m/s, team estimate);
- days or weeks of drift between the tare and the full reading.

## 3. Evidence quality

- **Nothing is measured.** The paper says so (p. 5). Every row of the accuracy table comes from assumed Gaussians. The 100,000 runs add precision to the assumptions, not evidence. The code is "available on request" and was not supplied. We reproduced it anyway.
- **σ_xw = 0.12 m (full) and 0.25 m (half) have no source.** These two inputs decide the headline.
- **References:**
  - Europress CombiMax page: confirms 35/40 t and a length of 6,990 mm (so L = 5.5 m is geometrically plausible). It does **not** show the 4,360 kg empty weight (our listings say 4,010–4,435 kg, so the figure is plausible).
  - Komatsu article: **HTTP 403**, could not be checked.
  - Safe-Weigh forklift scale: **404, dead link**.
  - The loader and forklift analogies are real prior art for hydraulic weighing. Those systems are factory-calibrated with known loads on a fixed geometry, so they do not support an uncalibrated CoG model.
- **"Europress, on site" requirement (2–5 %, ~€400–1,000)** is not in our transcripts. Tommi spoke of roughly 20 % of price and "saving €2,000" (`Since.AI.2.txt` l. 581, 589). The ±5 % figure also appears to be Tommi on *fill-level* accuracy (`Röst…txt` l. 163), not weight.
- **Presentation:** on pp. 2–3 the equations appear as raw LaTeX source. The diagram on p. 2 renders correctly.

## 4. Contradictions with our §19

| Topic | Paper | §19 | Better supported |
|---|---|---|---|
| Bore and pressure | Ø80, 83 bar at 3 t, 160 bar sensor | Ø80, max 113 bar vs ~200 bar | **Agree** (113 bar at 5 t in both) |
| Plus accuracy | σ 3.2 % at 3 t, no tickets | 10.7 % no tickets (case A), 4.4 % at 2.5 t after tickets (B) | **§19**: more terms (tare, temperature, pivot shift). The paper's 0.12 m is a post-calibration value with no calibration behind it |
| Calibration | Tickets "weaken independence", so Pro reference units | H2 ticket calibration, Pro only as a pilot | Judgement call. Independence matters only if the aim is auditing the weighbridge. Billing stays on it either way (PDF limitation 5) |
| Stroke | 50–80 mm, ~10 mm lift, 20/30 mm check | 50 mm, 10 mm margin "thin" | **§19 on margin.** The paper contradicts itself |
| Cost | €550–1,100 parts | €1,034–3,008 factory-fit installed | **§19**: it includes labour, NRE, CE, frame and maintenance |
| Cost target | 2–5 % (~€400–1,000) | ~€2,000 reference | **§19** (traceable to the transcript) |
| Tare door-end share | 0.455 (2.5/5.5) | 0.30–0.45 | Paper is at our upper edge. Fine |
| Lifts per year | ~1,000 | ≈445 | §19 (already noted) |
| Pro | 99.9 %, no cost | case C 1.9 % at 5 t, front cylinder €510–1,150 | §19 (costed); the paper's numbers are consistent |

## 5. Safety, regulatory and practical gaps

- **No CE mention at all.** An automatic self-lift is a new machine function. It needs a risk assessment and a technical-file update under 2006/42/EC, and under Regulation (EU) 2023/1230 from 20 Jan 2027 (§19.6).
- **Missing hydraulic safety parts:** no load-holding valve (hose burst) and no relief valve. No door or ram interlock.
- **"Instant lowering"** of a 7–9 t unit on a motion trigger is itself a hazard. It should be *controlled* lowering.
- **No guarding** for people's feet at the foot. Night pump noise is not covered.
- **Lateral stability** (row 2) and frozen rails (row 10) are not covered.
- **Ground bearing:** the 300 × 300 mm plate is given, but the pressure is not checked (0.6 MPa fails on hot asphalt and gravel, §19.6).
- **Frame:** the 40–57 kN point load on the rear frame needs FEA and reinforcement. Not mentioned.
- **Pro:** lifting the whole unit on 3 points puts cylinders under the hook-lift A-frame and press. No layout or cost is given.

## 6. Verdict: **partly**

The physics is right, and the numbers are internally consistent: we reproduced the Monte Carlo and the pressures. It is a clear, honest concept note, and it states its own limits well. It does **not** show viability. No data exists, the headline accuracy is set by one unsourced input (σ_xw), several real error terms are missing, the cost leaves out installation and compliance, and the stroke spec contradicts the two-height check.

**Safe to cite in a pitch:**

- The principle and the statics. Sensors carry load only ~30 s per reading.
- An 80 mm bore needs ≤113 bar at 5 t, well under the ~200 bar on board.
- Up/down averaging cancels *symmetric* friction.
- Undetected rail contact is the critical risk; a lift check detects it.
- Parts of roughly €0.5–1.1k (installed ≈ €1–3k, team estimate).
- Untested, and not legal-for-trade.

**Do not cite:**

- "88 %" or "99.9 % within ±5 %" as results. They are assumptions restated.
- "Meets ±5 %": Plus fails at the 95th percentile even when full (6.3 %).
- "2–5 % of unit price" as a Europress requirement.
- €550–1,100 as the device cost.
- Any Pro figure without a cost.
- The dead or blocked references.

**Top 3 fixes:**

1. **Make the accuracy honest.** Add the missing terms (tare change and snow, temperature span, pivot shift between tare and reading, slope, wind). Replace the headline with a curve of error against σ_xw. State how x_w is obtained, either from ticket calibration (§19 case B) or a measured fill profile, and drop the bare 88 %.
2. **Fix the geometry.** Make the stroke match the procedure: a 20/30 mm check needs ≥60 mm plus margin, so specify 80–100 mm. Then check lateral stability, rail clearance near the pivot, frozen rails and ground bearing.
3. **Cost and trace it.** Give an installed cost (labour, frame NRE, CE, valves, interlocks) and a Pro cost. Source the 2–5 % / ±5 % requirement or drop it. Ship the Monte Carlo code and fix the links. A one-day bench test (one cylinder, known loads, up and down) would be the first real evidence.
