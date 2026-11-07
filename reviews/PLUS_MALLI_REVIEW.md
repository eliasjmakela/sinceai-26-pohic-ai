# Review: "Plus-malli: kestävä versio – yhteenveto" (Mike, 7 Nov 2026)

Independent review for team OpenWeight/FullLoad. Source: the 4-page PDF (Finnish, read with `pdftotext -layout`).
Evidence base: `PRODUCT.md`, `LIMITATIONS.md`, `web/public/data/bundle.json`, Part 1 on branch `weighing-v2`
(`part1/WEIGHING_CONCEPT.md`, `part1/installed_cost.json`), transcripts `Röst 261106_182238.txt` and `Since.AI.2.txt`.
All team numbers are synthetic data / hypothetical prices.

**Note on scope.** The PDF is a **hardware weighing concept with a three-tier product line**, not a business model.
It has no revenue, payer, fee, adoption or payback figures. Sections 3–4 therefore test it against the team's
business model (`bundle.json → business`) to see whether it fits.

## 1. What the PDF proposes

It proposes a "Plus" weighing tier for new mobile CombiMax-type compactors. A single hydraulic cylinder, built into
the rear frame 0.5–1 m from the back and driven by the compactor's own hydraulics, lifts the rear about 10 mm while
the front rests on its runners as a pivot. The unit then stands on three points. Rear lift force is taken from a
pressure sensor and averaged over a slow lift and a slow lowering (15 s each) to cancel cylinder friction. Waste
mass is computed as W = (R − R₀)·L / x_waste. SMART triggers a reading at tare (empty unit returns), at the fill
alarm (pick-up weight) and once a night (trend). The centre-of-mass position x_waste comes from a model that
learns from each pick-up. The PDF claims ±3 % for a full container and ±8–10 % for a half-full one. It prices the
parts at €550–1,100 (OEM estimate, retail minus 50 %) and lists durability measures. Fit: good on new mobile units,
poor on stationary units, none on retrofits. Three tiers: Basic, a virtual scale (€0, ±10–20 %, whole fleet); Plus
(€550–1,100, ±3 % full); Pro, with two more cylinders at the front (±2–3 % always) on reference devices that train
the other two tiers. The PDF lists its own risks: the centre-of-mass model is unvalidated, the price is at the top
of the budget, the dimensions and pressures are assumed, and the system only works on new units.

## 2. Every number checked

| # | PDF claim | Check | Verdict |
|---|---|---|---|
| 1 | W = (R − R₀)·L / x_waste | Moments about the front pivot: R·L = W_m·x_m + W·x. With the empty unit, R₀·L = W_m·x_m. Subtracting gives the formula. It holds only if the pivot is fixed and L and x are measured from the same pivot. | **Consistent** (physics) |
| 2 | Lateral position of the waste does not matter (3-point support) | True if the two front contacts lie on one transverse line, because the cylinder force then depends only on the moment about that line. On uneven ground the runners touch at arbitrary points along their length, so the pivot moves at every placement. Effect: a pivot shift δ changes (L−δ)/(x−δ). Example: 5 cm on L ≈ 5.5 m, x ≈ 3 m gives about +0.8 %. R₀ is re-measured at each return, which limits the problem to one placement. | **Consistent**, small residual error |
| 3 | Averaging lift and lowering pressure cancels friction | Correct to first order for symmetric (Coulomb) seal friction. Stick-slip and asymmetric hysteresis remain. | **Plausible**, untested |
| 4 | Cylinder loaded ~30 s × ~1,000 times/yr | 2 × 15 s = 30 s ✓. Count: 365 nightly readings plus 2 per lift. The fleet averages 18,042 lifts / 447 devices ≈ **40 lifts/yr** (`fleet.fill_by_trigger`), so ≈ **445/yr**. The PDF figure is about 2× high, which is conservative for fatigue. | **Inconsistent** (overstated, harmless) |
| 5 | Stroke 50 mm, foot 30 mm above runner bottom, lift 10 mm | 30 + 10 = 40 mm, which leaves only **10 mm** for ground unevenness. If the unit stands on Europress guide rails or a plinth, the foot may not reach the ground at all. | **Internally consistent, margin thin** |
| 6 | Example "3.1 t ± 0.1 t" (≈ ±3 %) | The synthetic mean load is 92.6 t/device-yr ÷ 40 lifts ≈ **2.3 t/lift** (`business.params.tonnes_per_device_year`). Tommi's maximum is 5 t (Since.AI.2.txt l. 574). | **Consistent** as an example |
| 7 | Accuracy ±3 % full, ±8–10 % half full | No calculation shown. The PDF itself says the centre-of-mass model is unvalidated and the dataset has no centre-of-mass data (open risk 1). A ±3 % result needs x_waste known to about ±3 % (≈ ±10 cm on a ~3 m arm). Pressure resolution also matters for small loads: 1 bar is ≈ 1.3 % of a 5 t reading but ≈ 6 % of a 1 t reading (team estimate, ~63 mm bore at ~200 bar, Tommi: "up to 200 bars"). | **Unsupported** |
| 8 | Parts €400–800 + €150–300 = €550–1,100 | The sum is correct. €550/€20,000 = 2.75 % ✓ and €1,100/€20,000 = 5.5 % ✓. The inputs are uncited, and the 50 % volume discount is an assumption. | **Arithmetic consistent; inputs unsupported** |
| 9 | "At the top of the budget" | Against Tommi's ~€2,000 reference, or ~20 % of a €20–25k machine (`Since.AI.2.txt` l. 581–582, ambiguous), €550–1,100 sits **well below** budget. It is "at the top" only against the business team's **€500** hopper figure (`business.params.h1_cost_eur`). | **Inconsistent** (the budget is never named) |
| 10 | Price is a parts price | It leaves out labour, calibration, frame reinforcement, NRE, safety certification and 6-year maintenance. Part 1 H1 adds factory labour €110–360, calibration €28–90, maintenance €110–283 and NRE €30–200 (`part1/installed_cost.json`). The same add-ons put Plus at **≈ €830–2,030 installed** (team estimate). | **Incomplete** |
| 11 | Basic €0, ±10–20 % | Team virtual scale (`bundle.json → virtual_scale.headline`): **≈ 8.3 % per lift** uncalibrated, **7.6 %** after 5 tickets, **5.5 %** for monthly totals, fill-only ~16 %. This is optimistic because the generator links mass to fill. The PDF is more pessimistic than our simulation and close to Part 1 tier T0 (5/10/20 %, `part1/generated/tiers_table.md`). | **Consistent** (conservative) |
| 12 | Pro ±2–3 % always; trains Plus/Basic | The Pro cost is not given ("+2 cylinders"). Our simulation finds that adding reference devices beyond ~5 % helps little (`virtual_scale.by_reference_share`: 0.05 → 0.3 changes the calibrated error by <1 point). | **Role consistent; cost missing** |
| 13 | SMARTSolar: one lift uses little energy | Mechanical work ≈ 50–60 kN × 0.04 m ≈ 2–2.4 kJ, which is negligible. The real energy cost is starting the pump. | **Plausible** |
| 14 | Fit by product family (stationary DuoMax/EPC poor, retrofit hard) | Consistent with Part 1: platform scale/rails suit stationary units (`WEIGHING_CONCEPT.md` §6–7). Part 1 H1 fits **both COMBI and DUO** with one part, which Plus does not. | **Consistent** |

## 3. Viability from the domain

**Mechanism.** The physics is sound and the trigger points are well chosen. Reading at the fill alarm gives the
weight exactly when a pick-up decision is made. Re-taring after each emptying removes residual waste and placement
effects. Learning x_waste from shared weighbridge tickets is the same self-calibration idea as Part 1 H2, which
cut H1 error from 9.5 % to 3.4 % on synthetic data (`WEIGHING_CONCEPT.md` §4). The PDF misses some real hazards:

- **Ground and rails.** The 10 mm margin (row 5) fails on units that stand on guide rails, plinths or soft or
  frozen ground. On a 300 × 300 mm foot, 5–6 t is ≈ 0.6 MPa, which is fine on concrete and marginal on hot asphalt
  or gravel (team estimate).
- **Frame.** The rear frame gets a concentrated 50–60 kN point load that it does not carry today. That means new
  structural design (NRE) and probably reinforcement, neither of which is in the BOM.
- **Safety and conformity.** A 9 t machine that lifts itself unattended at night is a new crush hazard. It needs a
  machinery risk assessment and CE re-documentation (Machinery Regulation (EU) 2023/1230 applies from Jan 2027).
  Night-time pump noise in residential yards is a second issue. The fill-alarm reading happens during opening
  hours, so it needs a door/loading interlock.
- **Dependence on SMART.** Plus needs SMART to trigger readings. Tommi put SMART Insights at only ~15 % of the base
  (task brief, 7 Nov call).

**Incentives and cash flows.** The PDF never says who pays. Under the team's model:

- **Customer:** uses the service free, so a hardware add-on to the machine price clashes with "customers are not
  willing to pay almost anything" (`Röst…txt` l. 70).
- **Europress:** if Plus is standard on new units, Europress pays for it. €550–1,100 is **10–20 % of the €5,625
  margin** per machine (25 % × €22,500, `business.params`). Tommi's point that a customer who saves €2,000 by skipping
  weighing makes the network worth less (`Since.AI.2.txt` l. 590) argues for standard-fit funded by Europress.
- **Incumbent operator:** gains planning weights (fewer lifts, 6–18 %: `LIMITATIONS.md` §3). It loses its moat only
  if the customer consents to share the data. Plus makes the weight more accurate but does not change that.
- **Challenger:** benefits only through customer-consented history. Plus versus Basic changes its risk premium by a
  few percentage points of σ, not by the 10 % vs 37 % gap between own and peer history.
- **Europress's limits:** Plus respects "no transport" (Tommi, `Röst…txt` l. 142–145) and does not touch billing.

**The decisive gap: Plus adds cost but no revenue.** The fee is per device per month (€20,
`business.params.fee_mode`), and Basic already delivers the service on every unit. Every euro of Plus hardware is
pure cost unless it buys a higher fee, more coverage or more machine sales. **Billing:** the PDF does not claim
legal-for-trade status. The pitch must keep the rule that billing stays on the certified weighbridge (Directive
2014/31/EU). **Data ownership:** the PDF does not cover it, and the team's consent model applies unchanged.

**Adoption.** Plus reaches only new mobile units. With 6-year renewal (`business.params.renewal_years`) that is at
most ~1,670 units/yr fleet-wide, and only the mobile share of those. The model's "30 % of 10,000 with hardware"
takes years to reach with Plus.

## 4. Contradictions, risks, break-even

**Contradictions:**

- **With the team's decision.** Part 1 chose H1 hopper plate + H2 self-calibration, with weighing rails as
  co-lead (`PRODUCT.md` §1, `WEIGHING_CONCEPT.md` §0). Plus is a third concept that is absent from the claims ledger,
  the red team and `installed_cost.json`. Presenting both splits the 25 % weighing score.
- **With the business model.** The model prices hardware at €500 (`h1_cost_eur`). Plus is 1.1–2.2× that in parts
  alone, and ~1.7–4× installed.
- **Internal.** The PDF says "at the top of the budget" while sitting under Tommi's reference (row 9). It says
  "~1,000 loads/yr" against ≈ 445 (row 4). Pro's cost is missing, but Pro is the tier that trains the others.

**Break-even** (on the business team's assumptions: 3,000 hardware devices, net €928,750/yr, from
`bundle.json → business.default`):

| Plus cost per device | Investment | Payback |
|---|---|---|
| €550 (parts, low) | €1.65 M | **1.8 yr** |
| €1,100 (parts, high) | €3.3 M | **3.6 yr** |
| ≈ €830–2,030 (installed, est.) | €2.5–6.1 M | **2.7–6.6 yr** (high end beyond the 6-yr lease) |

- Maximum cost per device for payback within 6 years: **≈ €1,860**, including the extra-sales lever. On service
  margin alone (€1.2 M − €0.74 M = €0.46 M/yr) the maximum is **≈ €920**.
- The extra-sales lever (+5 % sales, €0.47 M/yr) is the most uncertain input (`LIMITATIONS.md` §8). Without it,
  Plus only works at the low end.
- To pay back Plus alone over 6 years, each Plus device needs an extra fee of **+€7.6 to +€15.3/month** if every
  Plus device pays. At 50 % paying coverage that doubles to **+€15 to +€31/month**, against today's €20.

**Main risks, in order:**

1. The centre-of-mass model fails at partial fill. The PDF itself says no data supports it.
2. Ground, rail and frame integration on real sites.
3. Safety and conformity of an automatic self-lift.
4. No incremental revenue.
5. Slow reach, because Plus only goes on new mobile units.

## 5. Verdict: viable with changes, as an option; not as the lead concept

The mechanism is physically sound, cheap in parts and well integrated with SMART. As a stand-alone product it is
not yet viable: accuracy is unsupported, the installed cost is incomplete, it adds no revenue in the current fee
model, and it reaches only new mobile units. It also competes with the team's chosen H1 + H2 rather than
complementing it.

**Recommended changes:**

1. **Do not make it a fourth lead concept.** Present Plus as the mobile-unit variant of "weigh cheaply and
   self-calibrate from tickets", or as an alternative in the Part 1 table. Add it to `installed_cost.json` with full
   installed cost (labour, frame NRE, CE/safety, maintenance), not parts only.
2. **Tie it to revenue.** Either a higher Plus fee (≥ +€8–15/device/month to pay back in 6 years at the parts
   price), or show that it raises paying coverage or machine sales. Otherwise Basic (€0) is the rational choice.
3. **Make the weighbridge ticket the reference, not Pro.** Our virtual-scale result shows that 5 shared tickets
   already cut the error (8.3 → 7.6 %, monthly 5.5 %). Limit Pro to a 20–50 unit pilot that validates x_waste, and
   give its cost.
4. **Write a ground and safety spec:** minimum stroke margin, guide-rail and plinth cases, foot bearing pressure,
   unattended-lift interlocks and noise. Turn the four "questions for Tommi" into an engineer's checklist.
5. **Restate accuracy as targets:** "±3 % target at pick-up after calibration, untested". Drop the half-full
   figure, or show how it was calculated.

**What to say honestly in the pitch:** "For new mobile units, the machine can weigh itself with its own hydraulics
for an estimated €550–1,100 in parts (≈ €0.8–2k installed, untested). It is planning data, not a billing weight:
the bill stays on the certified weighbridge. The software virtual scale already gives ~8 % per lift at zero
hardware cost on synthetic data. Plus is the upgrade path if operators pay for better weights, and it pays back
within the lease only if it costs under ≈ €1,900 installed on our business team's assumptions."
