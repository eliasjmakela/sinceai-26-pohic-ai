# Review: `weighing_appendix.py` (technical appendix to the "Duo" sheet)

Checked 7 Nov 2026 evening. The script is the team's technical appendix for the two-end lift (our H7-2,
`part1/WEIGHING_CONCEPT.md` §20). We ran its Monte Carlo core with seed 42 in an isolated folder (plotting and PDF
output stubbed out).

## Verdict: about right as a model, with three things to fix

The script is sound and it reproduces its own PDF exactly. The physics is correct and the method is a proper
Monte Carlo (JCGM 101). It is still a model of an untested design. Three things need fixing before citing it:

1. **The main sheet quotes numbers the appendix does not give.**
   - The sheet says 99.9 % of readings within ±5 % at full and **95.6 % at half fill**.
   - The appendix gives **99.8 %** and **94.0 %**. Its own Figure 2 caption also says 94 %.
   - The "1.3 % audit floor over 20 pickups" does match (n = 20, 1.3 %).
2. **Some error sources are left out,** so the accuracy is optimistic (see the gaps table).
3. **The cost is parts-only retail × an OEM factor.** It is not an installed cost.

## What we reproduced

| Scenario (100,000 runs) | σ | Within ±5 % | 95th pct. | Matches its PDF |
|---|---|---|---|---|
| Duo (two-end), full | 1.64 % | 99.8 % | 3.21 % | yes |
| Duo, half | 2.66 % | 94.0 % | 5.22 % | yes |
| Duo, full, friction residual 1 % | 2.41 % | 96.2 % | 4.73 % | yes |
| Duo, full, undetected rail contact ≤ 5 % | 2.99 % | **35.6 %** | 11.08 % | yes |
| Plus (one-end + centre-of-mass model), full | 3.42 % | 85.8 % | 6.69 % | yes |
| Plus, half | 10.94 % | 36.4 % | 21.37 % | yes |

Other checks:

- The analytic cross-check for Plus gives 3.41 % (1σ) against the Monte Carlo's 3.42 %, so the implementation
  is consistent.
- The two-level split (systematic per unit vs random per pick-up) is a good addition. It shows why averaging
  tickets cannot remove a centre-of-mass bias in the one-end design (floor ~4 %) but does for the two-end one
  (~1.2–1.5 %).

## Physics and inputs

- **Equations:** correct. Front lift: R_f(b_r − a) = W(b_r − x). Rear lift: R_r(c − b_f) = W(x − b_f). Adding the
  two gives W(b_r − b_f). Net waste = full − empty at the same placement.
- **Derived values:**
  - pressures: 87 bar front and 74 bar rear when full, 2.9× margin to a 250 bar pack;
  - foot pressure: 0.49 MPa;
  - oil flow: 0.6 L/min.

  These are plausible for its geometry. They differ from our §20 estimates (up to 128 / 98 bar) because the
  appendix assumes a different geometry (tare centre of mass 2.5 m, cylinders at 0.8 m and 6.0 m). The geometry
  is labelled ASM; Europress drawings should replace it.
- **Inputs to correct or source:**
  - `W0 = 4,360 kg` is labelled SRC [S1], but the CombiMax page we checked confirms the length and compaction
    force, not the empty weight.
  - `acc = 5 %` is labelled SITE and `budget ≤ 10 %` is labelled REQ ("revised from 2–5 %"). Neither is in our
    transcripts. Tommi spoke of roughly €2,000 per device and ~20 % of price for today's weighing, and his ±5 %
    sounded like fill-level accuracy. Label both as team targets.
  - The centre-of-mass σ for Plus (0.12–0.25 m) drives most of the Plus error and is an assumption. This is
    stated in the script.

## Gaps (why the accuracy is optimistic)

| Not modelled | Effect | In our budget (§19.5, §19.6) |
|---|---|---|
| Tare change: rain, ice, residue (25–150 kg); roof snow 0.7–1.4 t | biases the net weight high | 2.0 % mid; snow flagged |
| Pivot or ground shift between the empty and full readings (pivots are drawn once and shared) | appears as a moment error | 0.8 % mid |
| Sensor span drift with temperature (only in the two-level run) | gain error | 0.48 % mid |
| Sideways tipping on the narrow support; runners frozen to the ground (adhesion reads high) | silent errors | rejection rules, not in budget |

The rail-contact case is the important finding: an undetected contact of up to 5 % drops "within ±5 %" from
99.8 % to 35.6 %. So the two-height check at each end is essential, and the contacts it cannot see (below ~1.5–4 %
of the load, §20.3) remain a risk.

## Cost

The appendix gives a retail total of €1,726–3,450 for two cylinders, two valves, two load-holding valves, one
sensor, lines and durability kits. At 40–50 % of retail (assumed OEM pricing) that becomes €690–1,725. Problems:

- **Missing lines:** labour, calibration, electronics on the SMART modem, tilt sensor, relief valves,
  development/CE (NRE), upkeep and frame reinforcement. Our installed estimate for H7-2 is **capex
  €1,427–3,965**, plus upkeep.
- **Wrong cylinder sizes for the prices:** the cylinder prices are for **63 mm** bore cylinders, one of them a used
  part (S7, resale), but the design uses **80 mm**.
- **Sources:** S4 (Safe-Weigh) returned 404 and S6 (Komatsu) returned 403 when the review checked them.

## What can be cited

- **Safe:**
  - the two-lift method (weight and centre of mass from two lifts);
  - the model result of σ ≈ 1.6 % at full for two-end vs ≈ 3.4 % for one-end, as "Monte Carlo of an untested
    design, seed 42";
  - undetected rail contact as the dominant risk;
  - the two-level result that averaging cannot fix a centre-of-mass bias in the one-end design.
- **Do not cite:** 99.9 % / 95.6 % (the appendix says 99.8 % / 94.0 %), €860–1,725 as the device cost, the ±5 %
  "requirement" as a Europress specification, or 4,360 kg as sourced.

## Suggested fixes for the author

1. Correct the sheet to 99.8 % / 94.0 % (or rerun if the inputs changed).
2. Add a tare-change term and a tare-to-full pivot shift. Report the result with and without them.
3. Use 80 mm cylinder prices, add the missing cost lines (or point to our §20.6 installed cost), and add relief
   valves.
4. Relabel `acc` and `budget` as team targets, and source or relabel `W0`.
5. Replace the two dead links.
