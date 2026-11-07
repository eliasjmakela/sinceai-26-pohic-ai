# Review: "Duo: lift each end once, solve for weight and centre of gravity" (team sheet, 7 Nov 2026, 1 p.)

Independent review for team OpenWeight/FullLoad. Same method as `reviews/SELF_WEIGHING_PAPER_REVIEW.md`. Points
already made there or in `part1/WEIGHING_CONCEPT.md` §19 are referenced, not repeated. Check scripts:
`/tmp/duo_scripts/check.py`, `/tmp/duo_scripts/cost.py` (not in repo). The sheet is one landscape page (1200 × 900 pt);
"p. 1, box n" below refers to its numbered boxes. Author not stated.

## 0. The headline finding: this is not a DUO mechanism

"Duo" here means **two cylinders**, not the Europress DUO product. The sheet draws a **CombiMax 20 m³** (subtitle):
press unit and compacted waste in one body on runners, lifted by "the compactor's own power unit" (p. 1, box 1).
A DUO container has no power unit. So the sheet is a concrete layout for §19.5 **case C (two-end lift)**, the PDF
"Pro" idea [39]. It says nothing about the DUO problems we listed in §19.3 (coupling bypass, per-container geometry,
jack in the exchange path). Using "Duo" for it in a pitch would confuse Europress, who sell DuoMax and DuoMega.
**Rename it "H7-2" (two-end lift).**

## 1. What the sheet proposes

| Topic | Claim | Where |
|---|---|---|
| Mechanism | Two cylinders retracted inside the frame, feet ≥ 30 mm above the rail underside. Front cylinder under the press unit, a ≈ 0.8 m; rear cylinder at c ≈ 6.2 m, "away from the rear impact zone". One shared pressure sensor + valves in the power-unit cabinet; steel line inside the frame | box 1 |
| Statics | Step 1: lift front, rear rails pivot: Rf(br − a) = W(br − x). Step 2: lift rear, front rails pivot: Rr(c − bf) = W(x − bf). Solve: W = [Rf(br − a) + Rr(c − bf)]/(br − bf), x = bf + Rr(c − bf)/W. "No centre-of-gravity model" | boxes 2–4 |
| Procedure | Same two lifts on the empty unit (tare), net = W − W_empty. R = A(p_up + p_down)/2. Each end at two heights (20 and 30 mm); a changing force means a rail still touches. ~2 min per measurement, press idle | box 4 |
| Extra signal | "x is a free extra signal: a sudden shift reveals wet, heavy or wrong material" | box 4 |
| Accuracy | "Simulated: ±5 % in 99.9 % of readings at full, 95.6 % at half fill · weighbridge audit floor ≈ 1.3 % over 20 pickups" | box 4 |
| Cost | "~860–1,725 € = 4.3–8.6 % of a 20 k€ unit" (OEM) | box 4 |
| Evidence | "Geometry (a, c, pivots), costs and error assumptions as in the technical appendix; untested" | footer |

## 2. Physics and numbers, recomputed

| # | Item | Check | Verdict |
|---|---|---|---|
| 1 | Two-moment solve | Adding the two equations eliminates x: W(br − bf). Both formulas are correct. Valid if a < br and c > bf | **OK** |
| 2 | Cylinder forces (not given) | Our envelope (M 3–4.5 t, press-end share 0.55–0.70, 0–5 t waste, bf 0.3–0.5 m, br 6.5–6.7 m): front 17–64 kN, rear 14–49 kN. On an 80 mm bore: front ≤ **128 bar**, rear ≤ 98 bar. Under ~200 bar [36], but the front peak is above H7's 57 kN design case | OK, bore not stated |
| 3 | Shared sensor | One 0–250 bar sensor at 0.10–0.25 % FS = 0.25–0.62 bar = 13–32 kgf. Four readings (2 ends × tare + full) give **1.0–2.4 % of 2.5 t**, 0.5–1.2 % of 5 t. Same size as H7's one-end term | OK |
| 4 | "No CoG model" | True for W. But net waste still carries tare change, snow (R25), friction residue and span drift (§19.5). The x_w term goes; nothing else does | Right, but oversold |
| 5 | Pivot location | A constant 5 cm error in bf or br costs only ≈ 0.3 % (it cancels in W − W_empty). A pivot that **moves** 5 cm between tare and reading costs ≈ 0.9–1.1 % per pivot, so ≈ 2 % if both move. Not better than one-end (§19.5) | Gap |
| 6 | Tilt | The CoG moves h·θ toward the pivot in both lifts, so W reads low by h(θ1 + θ2)/(br − bf): 0.08 % of the waste at 10 mm lifts, 0.25 % at 30 mm (h = 1.5 m) | Negligible |
| 7 | Two-height contact check | Without contact, R changes only ≈ 0.06–0.09 % from 20 to 30 mm (tilt). A 3σ detection threshold is 0.75–1.9 bar = 38–95 kgf. So partial contact below **~1.5–4 % of a 2.5 t load** passes unseen. The check is a good idea with a floor | OK, floor not stated |
| 8 | Stroke | Feet ≥ 30 mm up + 30 mm lift = **60 mm before any uneven ground**. Stroke is not given. Same contradiction as SELF_WEIGHING_PAPER_REVIEW row 9 | Gap |
| 9 | Runner contact near the pivot | At 10 mm lift a runner point 1 m from the pivot rises 1.7 mm; at 30 mm, 5.2 mm. The 30 mm lift helps against R30 | Improvement |
| 10 | Side tipping (R29) | Now at both ends: support triangle ±0.22 m (front lift) and ±0.25 m (rear lift) at the CoG, runners 1 m apart (assumption) | Not addressed |
| 11 | Accuracy | 99.9 % within ±5 % implies σ ≈ **1.5 %** (unbiased normal); 95.6 % implies σ ≈ **2.5 %**. Our case C (§19.5): 1.9 % at 5 t, 3.2 % at 2.5 t (mid) → 99.2 % and 88 %. The sheet sits between our low and mid sets. "Audit floor 1.3 % over 20 pickups" matches 1.96·σ/√20 with σ ≈ 3.0 %, but the sheet does not say what it means | Plausible, unsourced |
| 12 | "x shift reveals wet material" | x moves with *where* waste lies, not its density. Fill % from SMART plus W gives density more directly. The real value of x is different: it measures x_w(fill), which trains the one-end fill model (§19.5 mitigation 1) | Weak claim, better use exists |
| 13 | Cost %, time | 860/20,000 = 4.3 %, 1,725/20,000 = 8.6 % ✓ (€20–25k unit price traces to [36]). ~2 min per reading ✓; ≈ 445 strokes a year per cylinder | OK |

## 3. Evidence quality

- **No links, no references.** Nothing to check online. All inputs point to a "technical appendix" that was not
  supplied. We cannot reproduce the 99.9 % / 95.6 % without it.
- **Untested**, as the footer says. The simulation restates its assumptions (as in the COMBI paper review, row 7).
- **Cost** has no line items. €860–1,725 is plausible as OEM hardware with one shared sensor: it equals the PDF's
  one-end parts (€550–1,100 [39]) plus €310–625. It is not an installed cost.
- **Geometry** (a ≈ 0.8 m, c ≈ 6.2 m) is new but unsourced; bf and br are not given.

## 4. Safety, CE and practical gaps

- **CE.** Two automatic lifts per reading. Same duties as §19.6: risk assessment and technical-file update under
  2006/42/EC, and Regulation (EU) 2023/1230 from 20 Jan 2027 [48]. The hold/lower function is a safety function and
  needs a performance level (EN ISO 13849-1). Not mentioned on the sheet.
- **New hazard: the front lift moves the press end.** That is where the charging opening is. Where a COMBI docks to a
  wall chute, hood or bin lifter, a 10–30 mm lift can crush against it, or the fixed part carries load (a new load
  bypass). Interlock: no front lift with the charging door open or a bin lifter cycling; site flag for docked units.
- **Front foot in the pick-up path.** The hook lifts the front first. A front rod not retracted is dragged at once.
  R26 (spring return, position switch, pick-up interlock) must cover both rods.
- **One sensor, two cylinders.** Isolation valves decide which cylinder is read. A leaking valve mixes the two. Each
  cylinder still needs its own load-holding valve (not shown). No relief valve is shown.
- **Frame.** Up to 64 kN under the press unit, where the frame already carries the press. FEA and reinforcement.
- **Missing, as in §19.6:** ground bearing, stroke-out detection, noise, SMARTSolar energy.

## 5. Cost (team estimate, same lines as `installed_cost.json`)

| line | H7 one-end, factory | H7-2 two-end, factory | basis |
|---|---|---|---|
| sensors | 60–200 | 80–270 | one shared transducer (sheet) + 2nd position switch, 2-axis tilt |
| electronics | 40–150 | 50–190 | 2nd valve driver and inputs |
| mechanical | 450–950 | 900–1,900 | 2nd cylinder, foot, housing, valve section, front reinforcement |
| site work | 0–150 | 0–250 | two pads |
| labour | 165–540 | 275–810 | 5–9 h × €55–90 [24] |
| calibration | 55–180 | 82–270 | 1.5–3 h; known load at two positions per end |
| maintenance (6 y) | 234–638 | 374–1,061 | 0.75 h/yr; two seal kits at 30–60 %; shared sensor |
| development (NRE) | 30–200 | 40–275 | €200–550k over 5,000–2,000 units |
| **total incl. 6 y upkeep** | **1,034–3,008** | **1,801–5,026** | |
| **capex without upkeep** | **800–2,370** | **1,427–3,965** | 7.1–19.8 % of €20k |

Our H7-2 hardware is €1,030–2,360 against the sheet's €860–1,725. The extra over H7 (€480–1,060 hardware) matches the
€510–1,150 front-cylinder estimate in §19.5. A real DUO-product variant (jack in the docking frame) is an order-of-
magnitude €1,970–6,990 factory-fit, mostly site work (draft §20.5).

## 6. Verdict: **partly** (as a COMBI two-end lift); **no** (as a DUO mechanism)

The statics are right and the solve is clean. It is the cleanest statement yet of case C, and it adds a layout and a
price. It does not show viability: nothing is measured, the appendix is missing, the stroke is unspecified, and it
inherits every H7 risk at two ends instead of one.

**Safe to cite in a pitch:**

- Lifting each end once gives total weight and centre of mass without a fill model (two moment equations).
- On reference units this measures x_w(fill), which trains the cheaper one-end fleet.
- Forces stay under ~130 bar on an 80 mm bore. Two-height check catches rail contact above a ~2–4 % floor.
- Team estimate €1.4–4.0k capex, untested, not legal-for-trade.

**Do not cite:**

- "Duo" as a name, or as a solution for DUO compactors.
- "99.9 %" / "95.6 % within ±5 %" or "1.3 % audit floor" as results.
- €860–1,725 as the device cost.
- "No CoG model" as "no error model": tare, snow, friction and pivot shift remain.

**Top fixes:** (1) rename, and add one line that the DUO product is still open; (2) give stroke (≥ 80 mm), bore, the
pivot positions bf/br and the missing safety valves; (3) ship the appendix or replace the % claims with our case C
budget; (4) add the press-end hazards (wall chute, bin lifter) and the two-pivot side-tipping check.
