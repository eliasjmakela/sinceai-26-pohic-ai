# Check: docs/fi/OpenWeight.pdf vs docs/fi/LIITE_perustelut.md vs the repo

> **Superseded on 7 Nov evening — see MASTER.md and docs/PRICING.md.** The €20 fee, the 1.6-year payback and the virtual
> scale marked "agreed" below are no longer current: the fee is €30 per weighed device per month, every new COMBI
> gets the H7 self-lift, and the virtual scale is roadmap only. `reviews/OPENWEIGHT_PDF_FIXES.md` has the current fix list.

Checked 7 Nov 2026. Sources: `docs/fi/OpenWeight.pdf` (8 pp., Finnish), `docs/fi/LIITE_perustelut.md` (its appendix), and in this repo
PRODUCT.md (Figure decisions, §1, §4), docs/LIMITATIONS.md, `web/public/data/bundle.json`, `part1/WEIGHING_CONCEPT.md` §19,
`reviews/SELF_WEIGHING_PAPER_REVIEW.md`, `pipeline/fullload/params.yaml` and the kit's `docs/BENCHMARK.md` and `docs/ECONOMIC_MODEL.md` (read only).

## Verdict

**The arithmetic is sound, but the figures are not the team's agreed ones.** I recomputed every calculation in LIITE
and it holds, including the full 10-year cash-flow table, which I rebuilt from its stated assumptions to the cent
(NPV 2.49 M€, cumulative +6.41 M€, deepest −2.94 M€). The appendix is honest and flags its own weak points.

The problem is that the PDF runs on a **different business model and weighing architecture** from the repo, and
PRODUCT.md says the repo's figures supersede other team documents:

- **Fee:** €30 per device per month plus €500 per tender, against the agreed €20.
- **Hardware:** an H7 lift (€825) on every new unit, against the virtual scale on every device plus a ~5 % reference subset.
- **Return:** NPV and payback in year 7, against payback in 1.6 years.
- **Information gap:** 21 % vs 9 %, against ±37 % vs ±10 %.

Three of the PDF's points actively contradict the repo:

- It lists the virtual scale under "what we will not do".
- Under the PDF's own model, the agreed €20 fee has a negative NPV (−0.15 M€).
- It quotes H7 claims that the self-weighing review says must not be cited: ±3 % full and €550–1,100.

The PDF also keeps four errors that LIITE §9 itself says must be fixed.

The regulatory framing is right where the PDF states it: billing stays on the weighbridge. But it never names
Directive 2014/31/EU, and "Varmennettu paino" (verified weight) reads as legal-for-trade.

## Claims table

Status key: **OK** = justified and agreed with the repo, **mismatch** = differs from the repo, **unsupported** = no
justification given, **wrong** = incorrect arithmetic or wording.

| # | Claim | PDF | LIITE | Repo value | Status | Fix |
|---|---|---|---|---|---|---|
| 1 | Customer gains ~€1,900 per device per year | p1, p6 | §1.1: 634+806+248+122+94 = 1,904 ✓; 7.9 % × 10,200 = 806 ✓; 827 × 0.3 = 248 ✓ | Avoidable visits €0.7–1.5k plus expensive tonnes ~€1.3k, "do not add them up" | mismatch / overstated | LIITE says the levers overlap (worst case €1.1–1.3k) and the 30 % realisation rate is a guess. Use the repo's ranges |
| 2 | Operator gains ~€1,400 per device per year | p1, p6 | §1.2: 634+130+643 = 1,407 ✓ | No single € figure (ours €2,712, team €1,930 pricing risk) | mismatch | Use "removes the risk premium on per-kg bids" |
| 3 | Wasted visits €130 | p6 | 0.89 × 130.5 = 116; LIITE says €60–116 | – | wrong (rounded up; LIITE §9) | €60–116, or drop |
| 4 | Pricing risk €643 = 1,930 / 3 | p6 | Arithmetic ✓, but the "ks. 2.3" link does not derive €1,930 | Team €1,930 vs ours €2,712 | unsupported | Show the €1,930 derivation |
| 5 | Operators earn €0–800 per device now | p1, p6 | 10,200 × 8.0 % = 816; × 2.7 % = 275 ✓ | – | OK, weak | €10,200 is the customer's cost (a mean; the median is €6,578), not operator revenue. Say so |
| 6 | Operating margins: L&T 8.0 %, Stena 2.7 %, L&T Q1 −0.9 %, Remeo −3.7 % | p6 | 34.2/426.6 = 8.0 % ✓; 4.693/176.1 = 2.67 % ✓; −0.8/94.8 = **−0.84 %** | – | minor | Use −0.8 % (or the unrounded inputs) |
| 7 | Europress NPV +2.5 M€; +2.4 M€ per year; payback in year 7; deepest −2.9 M€ | p1, p6 | Rebuilt exactly: fee 1,200·y × 0.6·min(y/4,1) × 360; packs ÷3 × 0.35 × 2.5 × 500; costs 400k + 76 per device | €20 per month, payback **1.6 years** (`business.payback_years`), 10,000 devices, 6-year horizon | mismatch | Pick one model. PRODUCT.md mandates €20 and 1.6 years |
| 8 | Fee €30 per month plus €500 per tender | p3, p6 | 1,400 × 25 % / 12 = 29 ✓; "no reference point" | **€20 per device per month** | mismatch | €20. At €20 the PDF's own model gives NPV −0.15 M€ |
| 9 | Weighing cost ~€190 per year (€825 over 8 years) | p6 | 825 / 5.747 + 50 = €193.6 ✓ | H7 €1,034–3,008 installed factory-fit | mismatch | €825 is the midpoint of a parts-only range, and the review says not to cite that range |
| 10 | Deepest point ≈ 0.7 × profit before tax (4.0 M€); +60 % of profit | p6 | 2.94/3.97 = 0.74 ✓; 2.38/3.97 = 0.60 ✓ | – | wrong source | The PDF cites PRH, but LIITE says the number came from Orbis (academic licence only) and PRH was never fetched. Fetch PRH or drop the comparison. It also compares cash flow with profit before tax |
| 11 | Sensitivity: +€100 ≈ −0.8 M€; break-even fee €21; €1,100 → +0.3 M€ | p7 | (4.71−0.28)/5.5 = 0.81 ✓; 30 − 2.49/0.264 = 20.6 ✓ | – | OK internally | Rebase on the agreed model |
| 12 | Pilot loss ~1 M€ (not 5–11 M€) | p7 | 0.825 + 0.80 + 0.152 − 0.27 = **1.5 M€**; "5–11" is from older model versions | – | wrong (LIITE §9) | ~1.5 M€. Drop or recompute "5–11 M€" |
| 13 | 10–25 % opt-outs wipe out the gain from charging | p3 | Earlier model (€600, 6 years): 10 % eats 80–130 %; free wins at 24–39 % | – | overstated | "Even 10 % opt-outs remove most of the gain" |
| 14 | 33 % of lifts at < 60 % fill | p2 | 33.0 % of 18,297 completed lifts | 33.4 % (`fleet.low_fill_lift_share_pct`) | OK | "1 in 3" |
| 15 | 18 % fewer lifts when full | p2 | 17.9 %, called an upper bound | **6–18 %** (labels 6.1 %, model 18.1 %, r = 0.85) | mismatch | Give the range 6–18 % |
| 16 | Guessing kg per lift: 21 % vs 9 % error | p2, p4, p7 | Median 20.6 % / 9.1 %. LIITE: with device error ~10–12 % | **±37 % vs ±10 %** (monthly tonnage, 385 devices) | mismatch | PRODUCT.md: use 37 vs 10 and don't show both |
| 17 | The incumbent wins every third year | p2 | Tommi gave no figure; "wins" is the team's reading | – | unsupported | "Contracts are retendered about every 3 years, mostly on price" |
| 18 | ~3 % of a property manager's time; HSY quote; Insights ~15 %; SMART −37 % | p2 | §2.5–2.8 | Same in PRODUCT.md | OK | Keep SMART's 37 % away from the 37 % forecast-error figure |
| 19 | Device vs weighbridge tolerance ±3.3 % | p4 | Kit ECONOMIC_MODEL "e.g." | Kit line 58 ✓ | OK | Say "the kit's example tolerance" |
| 20 | Weigh every new compactor with H7; the customer cannot opt out | p3, p5 | Team choice | Virtual scale on every device; H7 only for the ~5 % reference subset | mismatch | Align the architecture |
| 21 | "What we won't do: a virtual scale" | p7 | §7.5 Nooa's decision | The virtual scale is core: ~8 % median per lift (≈11 % as 1σ), 5.5 % monthly | **mismatch (critical)** | Remove. The PDF's own "±10–15 % is enough for pricing" (p5, unsupported in LIITE) actually argues for it |
| 22 | Lift force 4–6 t (≈60 kN), Ø80 → ~120 bar | p5 | 60,000 / 5,027 mm² = 11.9 MPa ✓ | 31–57 kN, ≤113 bar | OK (conservative) | LIITE's 50–60 % door-end share is higher than §19's 0.30–0.45 |
| 23 | Sensor ±0.25 % FS → ±30 kg | p5 | 0.625 bar × 5,027 mm² = 314 N = 32 kgf of force | ≈85 kg of waste per bar → ~53 kg per reading, ~75 kg with tare plus reading | wrong (LIITE §9) | "±50–75 kg of waste" |
| 24 | Accuracy ±3 % full, ±8–10 % half-full; "3.1 t ± 0.1 t" | p5 | Mike's estimate, "unvalidated" | Target 1σ ≤ 5 % after 10 tickets (budget 4.4 % mid); 10.7 % with no tickets; example ±0.15 t | mismatch / do-not-cite | State it as an untested target, with tickets |
| 25 | Device cost €550–1,100; two cylinders €700–1,200; load cells €530 up to the unit price | p5 | Parts only (retail −50 %); the €530–1,300 source "§6.3" does not exist | €1,034–3,008 installed factory-fit; platform scale €7,860–22,160 | mismatch / unsupported | Use the installed range; source or drop the other two |
| 26 | Foot plate 400 mm ≈ 0.4 MPa | p5 | 60 kN / 0.16 m² = 0.375 MPa ✓ | 300 mm → 0.63 MPa; hot asphalt allows 0.4 | OK, marginal | – |
| 27 | Fits all compactors: DUO cylinder in the rail; retrofit at service | p5 | LIITE: "unchecked" / "a guess" | DUO speculative, not costed; retrofit not recommended (€1,994–6,168) | overstated | "COMBI, new units only" |
| 28 | "Europress's own IP" | p5 | "a wish, not a fact"; patent US11148383 | Prior art exists (Hiab US 2020/0096383); no freedom-to-operate check | overstated | "We found no compactor that lifts itself; prior art exists for trucks" |
| 29 | Safety list | p5 | No machinery-directive risk assessment | §19.6: CE under 2006/42/EC, and Regulation (EU) 2023/1230 from Jan 2027 | gap | Add "needs a CE risk assessment" |
| 30 | Demo: €2,100–3,400 per year saving, "contract ends in 7 months" | p7 | "Invented placeholder" | Customer €/t **−13 %** (113.1 → 98.0; range −12 to −15 %); showcase −31.9 % = best case | unsupported | Use the pipeline's figures. The PDF never mentions the agreed −13 % |
| 31 | Baselines: A 96 %, B F1 0.73 / recall 0.59, B2 68, C2 regret €240 | p8 | Kit BENCHMARK ✓ (0.964, 0.7309, 0.5941, 67.75, 240.07) | Our rule: recall 71 %, F1 0.81 | minor | C2 is the **dev** split, not validation. The "(recall 0.59)" in the improvement column reads as our result |
| 32 | Installed base ~20,000; 1,200 new per year; ~70 % leased | p6, p8 | Tommi (L6) | `params.business.devices_total` 10,000 | mismatch | Agree on one installed-base figure |
| 33 | No billing on the device weight; the weighbridge stays the basis | p7 | Kit ECONOMIC_MODEL §2b | LIMITATIONS §2: Directive 2014/31/EU; planning data plus cross-check | OK, incomplete | Name the directive. Change "Varmennettu paino" (p4) to "weighbridge-checked weight", and "Kalibrointi" to "calibration against weighbridge tickets" |
| 34 | Calculations in `docs/fi/analysis/` | p1, p8 | LIITE paths | Not in this repo (LIMITATIONS §8) | unsupported | Add the scripts or point to the repo pipeline |

## Most important fixes, in priority order

1. **Choose one business model.** Either switch the PDF to the agreed €20 per device per month, the virtual scale
   plus reference subset, and ~1.6-year payback, or get the team to formally change PRODUCT.md. The PDF's own
   sensitivity table says the agreed €20 loses money (NPV −0.15 M€), so the two documents cannot both go to judges.
2. **Delete "No virtual scale" (p7)** and stop implying that every unit gets H7. The virtual scale is the repo's
   core weighing claim.
3. **Remove the H7 claims the review bans:** ±3 % full, €550–1,100 and €825 as the device cost, "Europress's own
   IP", and "fits every compactor". Use €1,034–3,008 installed factory-fit, the 1σ ≤ 5 % target (4.4 % mid
   budget) and "untested, COMBI only".
4. **Use the agreed market figures:** ±10 % vs ±37 % (not 9 vs 21), 6–18 % fewer visits (not 18 %), and add the
   customer's €/t falling from 113.1 to ~98 (−13 %, range −12 to −15 %). Replace the invented demo saving of
   €2,100–3,400.
5. **Apply LIITE §9's own corrections:** sensor ~±50–75 kg of waste; wasted visits €60–116; pilot loss ~1.5 M€;
   drop "5–11 M€". Also: the opt-out figure "10 %", the missing €1,930 and €530–1,300 sources, and "every third
   year".
6. **Fix the sources and the regulatory wording.** The Europress profit figure is cited as PRH but came from
   Orbis, which cannot be used. Cite Directive 2014/31/EU, avoid "varmennettu", and add the CE risk-assessment note.
7. **Repo side (for the lead developer):** PRODUCT.md attributes the team's operator figures as "€1.4k / €1.9k".
   In the PDF, €1.9k is the customer figure and €1.4k the operator figure. Worth correcting the attribution.
