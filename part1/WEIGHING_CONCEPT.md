# FullLoad Part 1: weighing concept (v2)

**How the compactor gets its own weight, cheaply enough to give away.** Team FullLoad, Since AI Hackathon 2026,
Europress challenge, Part 1 ("Get the weight"). Version 2, 7 Nov 2026, after the follow-up talk with Tommi Häkkinen
[36]. Everything in this document is **untested**. No hardware was built or measured, and the team has no
mechanical-engineering expertise: every mechanical number is an order-of-magnitude calculation in `part1/calc/`
for an engineer to check. The synthetic dataset cannot show that any weighing design works [1][2]. Every accuracy
figure carries a tag: *estimate* (team reasoning or a simulation with team-estimate inputs), *simulation target*
(the starter kit's assumption) or *literature* (a published vendor or reference value). Every number is traced in
`CLAIMS_LEDGER.md`; the failure modes we tried are in `RED_TEAM.md`; open questions for Europress are in
`ENGINEER_QUESTIONS.md`.

## 0. One page for Tommi

**The problem you named.** Without the weight "we always stop halfway" [36]. Platform scales under the unit exist
but are "almost as expensive" [36]; the weight has to come cheap, it "doesn't need to be very accurate", and an
option around €2,000 on a €20–25k COMBI is what customers would weigh it against [36].

**Our recommendation: H1 hopper-stage weighing + H2 fleet self-calibration.**

1. **Weigh the charge, not the container** (your idea, credited to Europress [36]). A small steel plate in the
   floor of the charging chamber sits on four 500 kg load cells. Each time the door closes, the plate is read
   before and after the ram stroke; the difference is the mass that went into the container. The device adds up the
   charges. The sensor never carries the 3–4.5 t machine [18][36], the up to 5 t of waste [36] or the hook-lift
   forces, so the cells are small and cheap, and the **same part fits COMBI and DUO**.
2. **The fleet calibrates itself** (our software edge). A hopper plate misses the part of each charge that hangs on
   the walls, so the raw sum reads a few percent low (8–10 % RMS error before calibration, *estimate*). That bias is
   stable per device, so every weighbridge ticket an operator shares is a free calibration point, and a new device
   starts from what its sister machines have already learned. On the synthetic lift history the container-total
   error falls from **9.5 % to 4.6 % before the device's first ticket** and to **3.4 % (2.3–5.4 %) after 10
   tickets** (*estimate*, §4, Figure 2).
3. **What it costs, fully installed** (sensors, electronics, mechanics, site work, labour, calibration, 6 years of
   maintenance and development amortised): **€548–2,363 factory-fit** and €1,270–4,923 as a retrofit (team
   estimate on cited part prices, §7). The factory-fit range sits around the ~€2,000 reference [36]; the platform
   scale lands at €7,860–22,160 (team estimate on [27]).
4. **Good enough for what FullLoad needs.** Billing stays on the operator's weighbridge (PRODUCT.md §1). For
   forecasts, weight-triggered pickups and per-site tonnage, a few percent is plenty; summed over a month of lifts the
   per-site tonnage error drops further because the per-container errors are independent.
5. **What we are not sure about** (honest list): whether a plate can live in the charging chamber (impacts up to
   ~12 t from misuse and 7–14 t of floor pressure on every stroke go into overload stops with a gap under 0.5 mm,
   §5.3), how much of a cardboard charge hangs on the walls, and liquids from biowaste. These decide a bench test (§14).
6. **Alternatives we costed.** Weighing guide rails (H5, the team's idea) are 3–5× more accurate (≈1 %, *estimate*)
   but cost €2,382–7,056 even on a new site because of the site work (team estimate, §7). The v1 strain gauges (T1)
   are cheaper, but on a COMBI they measure frame bending, which changes every time the unit is set down (§10).

**Ask:** can a Europress engineer check the charging-chamber questions in `ENGINEER_QUESTIONS.md`, and would
Europress host a bench test of the plate (§14)?

## 1. What changed in v2, and the requirement

| v1 (6 Nov) | v2 (7 Nov, after Tommi [36]) |
|---|---|
| Chosen concept T1 strain gauges on the frame | **H1 hopper-stage plate + H2 self-calibration**; T1 kept as an alternative with a revised (worse) error budget |
| BOM only | **Full installed cost per device** (H6), retrofit and factory-fit, for every candidate |
| T0/T1/T2 | T0, T1, T2 plus **H1, H5 weighing rails, PS platform scale** |
| Accuracy goal: ±100 kg on 3 t | Planning grade: "doesn't need to be very accurate, but it must be cheap" [36]; billing stays on the weighbridge |

Use of the device weight and the accuracy it needs (1σ, *estimate* from §8):

| Use | Accuracy needed | H1 + H2 |
|---|---|---|
| Fill → weight forecast, weight-triggered order | ≈ 5–10 % | yes |
| Per-site tonnage per month for per-kg tender pricing | ≈ 2–5 % | yes (the per-container part of the error averages out over a month of lifts) |
| Flag a +10 % difference on one load against the weighbridge | ≈ 1–3 % | mostly (77 % flagged at mid, §8) |
| Settlement | weighbridge only (Directive 2014/31/EU [15]) | not claimed |

> **TOMMI (Q9):** We assume planning grade means a 1σ of about 5 % or better on a container. If Europress needs
> the device to flag single-load differences reliably, H5 or a platform scale is the better fit (§10).

## 2. Mechanism first: the compactor's feed cycle

From public sources (marked) and our assumptions (marked *assumed*):

1. The user opens the infeed door and drops waste through the hopper. A Europress COMBI has an infeed aperture of
   1,500 × 900 mm at a loading height of 1,480 mm, a 25 t compaction force and a 42 s press cycle (listing [17]).
2. The waste lands in the **charging chamber** in front of the retracted ram, on the chamber floor or partly on the
   ram (Tommi [36]). *Assumed:* the chamber floor is about 0.4–0.6 m above ground, so a charge falls 0.9–1.1 m.
3. The door closes and the cycle starts; the ram pushes the charge into the container and retracts (*assumed*
   from the 42 s cycle [17]; Europress's exact stroke sequence and spill-back protection are ENGINEER_QUESTIONS Q2).
4. Each cycle adds one charge. The kit assumes a median charge of 8–30 kg depending on material [2]; in the
   synthetic data a container collects a median of 78 charges (compaction cycles) between lifts, 10–33 kg each
   (p10–p90), `generated/charge_sum.json`.
5. **COMBI:** the whole unit (machine 3 t per Tommi [36], 4.0–4.4 t in third-party listings of 20 m³ units [18])
   is pulled onto a hook-lift truck and emptied at the treatment site. **DUO:** the compactor stays; only the
   container is detached and exchanged. SMART already logs compaction cycles, fill and a press-load signal [2][3].

## 3. Recommended concept: H1 hopper-stage weighing + H2 self-calibration

![Figure 1: placement of H1 and H5 on COMBI and DUO](figures/placement_v2.svg)

*Figure 1. H1 plate and H5 rails on COMBI and DUO, and the H1 reading sequence. Self-made sketch, not to scale.*

### 3.1 Measurement principle

- **Weighing plate.** A wear-steel plate of about 1.4 × 0.8 m forms part of the charging-chamber floor where the
  charge lands. It rests on four 500 kg C3 load cells (2 t range, 0.017 % combined error [22]) whose signals are
  summed on a 24-bit weighing board connected to the SMART modem [6][10]. Overload stops under the plate limit the
  travel to about 0.24–0.48 mm (`calc/loads.py`), so impacts and compaction pressure go into the chamber floor.
- **Differential reading per stroke.** After the door closes, the firmware waits 2–3 s and takes reading B (before);
  after the ram has retracted and settled it takes reading A (after). The charge that entered the container is
  **B − A**. Material that sticks to the plate or springs back is simply counted when it finally leaves: the sum of
  all differences telescopes to the mass that crossed the plate. Several drops before one stroke are one charge.
- **Why the small range works.** A 9–30 kg charge is 0.4–1.5 % of the plate's range, which the cells resolve to
  about 0.3 kg (`calc/loads.py`). Temperature drift is negligible because B and A are about a minute apart (0.02–
  0.04 kg per charge, `calc/temperature.py`).
- **What it cannot see.** Waste that hangs on the hopper walls or rests on the ram when B is read is not on the plate
  but still goes into the container. This **bridging share** (team estimate: 1 % of a biowaste charge to 6 % of a
  cardboard charge, `calc/h1_params.py`) is the main error and is why H2 exists.
- **Container total.** The device reports the running sum since the last lift and its own 1σ, i.e. the dataset's
  `mass_kg` and `mass_uncertainty_kg` [2]. The sum resets when the emptied COMBI returns or an empty DUO container docks.

### 3.2 Firmware rules

1. Read only with the door closed, the ram retracted and the hydraulic pump idle, as a 2–3 s average.
2. Delay the automatic press start by 2–3 s so that reading B exists (TOMMI Q8: door-to-start timing).
3. Count every compaction cycle (SMART already does [2]). Ten strokes in a row with no weight change while the
   cycle counter runs = plate jammed or bridged: raise a fault. In the synthetic data that fires within 12–78 h
   depending on the material (`generated/fusion.md`).
4. Reject a difference above the plate's range or below −2 kg (team estimate) as an invalid pair.

## 4. Our edge: the fleet calibrates itself (H2)

**The idea.** Random errors of single charges average out over a container (√N), but the bridging share does not.
It is roughly constant for one device and one material, so it acts as a **gain error**. Every weighbridge ticket an
operator shares (single load, weighed tare) gives the ratio *device sum / ticket* for one container: a free
measurement of that gain. A Kalman filter per device tracks the gain (with a random walk for drift), and its
starting value is the average learned so far from **other devices of the same material and machine type**, so a
new device or a device whose operator shares nothing still starts from the fleet's knowledge (empirical Bayes).

**The measurement** (`scripts/self_calibration.py`, synthetic data, fixed seed). We replayed all 5,627 reference
lifts of 368 devices in time order. Each container was split into as many charges as the device ran compaction
cycles, each charge was weighed with the H1 error model (`calc/h1_params.py`, team estimates), and each device's
corrected weight was scored against the ticket **before** that ticket was used (one step ahead, out of sample):

| H1 container-total RMS error (low / mid / high) | no calibration | device's own tickets only | fleet self-calibration (H2) |
|---|---|---|---|
| before the device's first ticket (n = 0) | 6.8 / 9.5 / 13.8 % | 6.8 / 9.5 / 13.8 % | 3.0 / 4.6 / 6.6 % |
| after 1–3 tickets | 6.9 / 9.4 / 14.0 % | 2.9 / 4.4 / 6.7 % | 2.6 / 4.0 / 6.1 % |
| after 10 or more tickets | 6.9 / 9.6 / 14.3 % | 2.3 / 3.4 / 5.4 % | 2.3 / 3.4 / 5.4 % |

![Figure 2: learning curve](figures/learning_curve.svg)

*Figure 2. RMS error of the container total vs the number of weighbridge tickets the device has seen (mid
parameters; band = H2 with low and high parameters).*

**What this shows, and what it does not.** With the stated assumptions, H2 halves the error of a brand-new device
(9.5 % → 4.6 % at mid) and reaches the floor of about 3.4 % after a few tickets; a device's own tickets alone need
1–3 tickets to catch up. In the synthetic data 78 devices belong to an operator that never shares tickets [2]: with
H2 they get the n = 0 figure instead of the raw 9.5 %. The analysis assumes that the bridging share is similar
within a material and machine type, that tickets arrive before the next lift, and that the synthetic ticket mass is
the truth. It measures the **method**, not the hardware.

**Who gets credit.** Weighing at the hopper is Europress's idea (Tommi, 7 Nov [36]). The differential
before/after reading, the fleet self-calibration and its analysis are the team's contribution. We make no novelty
claim beyond §11.

## 5. Placement and mechanics

### 5.1 COMBI (compactor and container joined; the whole unit is lifted and transported)

- **H1:** the plate sits in the floor of the unit's charging chamber. It **travels with the unit**, but it carries
  only its own mass and the charge: lifting and road loads on the plate are its own inertia (≈100–150 kg plate ×
  a few g, team estimate), well inside the stops. The cells see none of the 8–9.5 t unit load (`calc/loads.py`).
- **When the unit is tipped for emptying** at the treatment site, waste and liquid can run back into the chamber
  and over the plate (RED_TEAM R6). The seal and stops must survive that; the sum resets anyway when the unit
  returns, and the first stable reading becomes the plate's new zero.
- **Cabling** stays inside the unit to the existing electrics cabinet and SMART modem; no connector to the truck.

### 5.2 DUO (compactor stays on site; only the container is emptied)

- **H1:** the identical plate sits in the stationary compactor's charging chamber. Container exchange does not
  disturb it: the sum restarts at zero when the empty container docks (SMART exchange signal [2]); a different
  container's tare never enters the result, because the container is never weighed.
- The plate does not travel, so DUO is the easier case for H1. Sensors, part number and firmware are the same as on
  the COMBI (TOMMI: is the charging chamber the same design on both? ENGINEER_QUESTIONS Q2).

### 5.3 Loads the H1 plate must survive (`calc/loads.py`, order of magnitude)

#### H1: impact of a thrown charge on the weighing plate

Energy E = m(g·h + v0²/2), h = 0.9–1.1 m, v0 = 1.5 m/s; peak force of a linear spring F = 2E/d + mg. Plate range 4 × 500 kg = 2 t, safe limit 150% = 3 t.

| charge | kg | stop distance mm | peak force kN | × static weight | seen as t |
|---|---|---|---|---|---|
| plastic film bag, 9 kg (kit median charge) | 9 | 80 | 2.3–2.8 | 26–31× | 0.24–0.28 |
| cardboard charge, 18 kg (kit median) | 18 | 50 | 7.3–8.8 | 42–50× | 0.75–0.89 |
| biowaste bag, 30 kg (kit median) | 30 | 30 | 20.2–24.1 | 69–82× | 2.06–2.46 |
| dense item thrown hard, 25 kg (misuse) | 25 | 5 | 99.8–119.4 | 407–487× | 10.17–12.17 |


Worst case ≈ 12.2 t against a 3 t safe limit: **overload stops are required**; a cardboard charge (0.89 t) stays inside the cell range and a biowaste bag (2.5 t) inside the safe limit.


#### H1: vertical load on the plate during the compaction stroke

Ram pressure p = 25 t / 1.20 m² = 204 kPa; vertical floor pressure K·p with K = 0.3–0.6; plate 1.12 m² → **7–14 t** on the plate on every stroke, 3–7× the cell range. The stops carry this; the cells see only what the stop gap lets through. Readings are valid only with the ram retracted.


Stop gap: set at ~120 % of rated deflection, i.e. **0.24–0.48 mm** (cells deflect 0.2–0.4 mm at rated load [19]). A gap this small jams with grit or ice unless sealed (RED_TEAM R3). An elastomer layer would allow a few mm of travel but adds creep and hysteresis (team estimate).


Signal-to-range: a 9–30 kg charge is 0.4%–1.5% of the 2 t range. C3 cells have 0.017 % combined error [8][22] (≈0.3 kg on 2 t), so a charge reads to about ±1–3 % electrically; mechanics (bridging, friction) dominate (calc/error_accumulation.py).

## 6. Co-lead: H5 weighing guide rails (team idea)

**Principle.** Europress sells guide rails as an accessory (brief, unverified). Put two shear-beam load cells under
each rail so that the unit (COMBI) or the container (DUO) rests **only** on the rails. The weight is the sum of four
cells. The system zeros when the rails are empty, tares when the emptied unit or an empty container returns, and
reads before pick-up. The cells stay on the ground: no transport, no tipping.

- **COMBI:** the rails carry machine + waste, 8.0–9.5 t; a 1 t load is 18–25 % of the reading, and the machine tare
  is removed by re-taring (`calc/loads.py`).
- **DUO:** the rails carry the container only (2–3 t + up to ~8 t), *if* the coupling to the compactor does not
  carry part of its weight (load bypass, RED_TEAM R10).
- **Accuracy.** C3 cells are far better than needed [8][20]; temperature adds 0.3–0.7 % between tare and reading
  (`calc/temperature.py`); the installed error is set by mechanics: side restraint, friction, levelling, ice and
  debris. We estimate 0.6–2 % (mid 1 %, *estimate*), in line with vendor claims of ≤ 1 % for container weighing on
  hook-lift trucks [12][13].

#### H5: loads on the four rail cells

| case | total t | per cell, even t | heavier pair, per cell t | × dynamic 1.5 | cell rated / safe limit |
|---|---|---|---|---|---|
| COMBI full (machine + waste) | 8.0–9.5 | 2.0–2.4 | 2.2–3.3 | 3.3–5.0 | 5 t / 10 t |
| DUO full (container + waste) | 10.0–11.0 | 2.5–2.8 | 2.8–3.8 | 4.1–5.8 | 5 t / 10 t |


Pick-up of a full COMBI: when the hook lifts the front, the rear pair carries up to ~80% of 9.5 t → **5.7 t per rear cell** with the dynamic factor: inside a 5 t cell's 200 % safe limit [20] but with little margin. Overload stops under the rear pair give that margin; 10 t cells would too but double the zero drift (calc/temperature.py), so the design keeps 5 t cells + stops (team estimate).


#### H5: set-down impact of an empty COMBI (front half on the front pair of cells)

Peak force F = √(2E·k_eff) + mg, cell stiffness 1.6e+08 N/m each (0.3 mm at 5 t [19]).


| set-down speed m/s | rail stiffness N/m | energy J | peak per front cell t |
|---|---|---|---|
| 0.05 | 2.5e+07 | 3 | 1.7 |
| 0.05 | 5.0e+07 | 3 | 1.9 |
| 0.05 | rigid rail | 3 | 3.3 |
| 0.20 | 2.5e+07 | 45 | 3.5 |
| 0.20 | 5.0e+07 | 45 | 4.3 |
| 0.20 | rigid rail | 45 | 9.9 |


At the higher set-down speed on a stiff rail the peak reaches the 10 t safe limit of a 5 t cell (no margin for a faster or uneven drop): **overload stops (or 10 t cells plus a compliant pad) are required**; slow set-down on a flexible rail stays inside it.


#### H5: horizontal force when the hook-lift pulls the unit on or off

Rolling rollers μ ≈ 0.05 → 0.5 t; sliding steel skids μ = 0.4–0.8 [21] → **3.8–7.6 t horizontal** on a 9.5 t unit. Shear-beam cells must not carry this: longitudinal and lateral check rods (stay rods) anchored to the base take it, as in tank weighing modules with lift-off and side restraint [23].


Signal-to-range: on a COMBI the cells carry the machine too, so a 1 t load is 18%–25% of the reading; the machine tare is removed by re-taring when the emptied unit returns.

**Why H5 is cheaper than a platform scale, and why not by much.** A platform needs a deck or beams with ramps sized
for the whole unit plus a foundation (a 15 t container scale with beams and ramps lists at €4,800–5,620 before
installation [27]). H5 reuses the rails as the "deck" and adds only cells, stops and restraint, but it still needs a
level, anchored base and two technicians for a day or more. In our cost model H5 is about a third of the platform
scale and **above the ~€2,000 reference** even when the site is new (§7, team estimate).

## 7. Full installed cost per device (H6)

All lines per device, 6-year lease, ex VAT, labour at €55–90/h ([24] + team estimate), part prices cited, everything
else a team estimate (`calc/installed_cost.py`; line-by-line tables for every candidate in Appendix A):

| id | candidate | hardware (factory) | installed, retrofit | installed, factory-fit | factory-fit within ~€2,000? [36] | basis |
|---|---|---|---|---|---|---|
| T0 | Virtual weight from existing pressure + fill (v1) | €0–50 | €10–215 | €10–125 | yes | team estimate |
| T1 | Strain gauges on frame / container rails (v1 choice) | €95–480 | €419–1,674 | €226–1,179 | yes | [4][5][6][7][24] + team estimate |
| H1 | Hopper-stage weighing plate (idea: Europress / Tommi) | €270–1,430 | €1,270–4,923 | €548–2,363 | partly | [6][9][10][22][24][25] + team estimate |
| H5 | Weighing guide rails (idea: team) | €1,310–3,100 | €3,412–10,136 | €2,382–7,056 | no | [8][9][10][11][23][24][26] + team estimate |
| T2 | Load cells under the unit's own frame (v1) | €1,160–2,600 | €1,960–5,438 | €1,635–4,338 | partly | [8][9][10][11][24][26] + team estimate |
| PS | Platform scale under the whole unit (Europress's existing option) | €4,800–12,000 | €8,580–23,880 | €7,860–22,160 | no | [24][27] + team estimate |

![Figure 3: installed cost and accuracy](figures/installed_cost.svg)

*Figure 3. Left: full installed cost per device (dark = factory-fit, light = retrofit) against the ~€2,000 reference
[36]. Right: factory-fit cost against the 1σ error after calibration (`scripts/cost_figure.py`).*

Reading the table:

- **H1 factory-fit (€548–2,363, team estimate)** is the only physical weighing option whose whole range is near the
  ~€2,000 reference [36]. Its largest lines are the cells (€100–880 for four, [22][25]) and development amortised
  over 2,000–5,000 units (€30–200 per unit, team estimate). With volume-priced cells the hardware is a few hundred euros.
- **H1 retrofit (€1,270–4,923, team estimate)** is expensive: the chamber floor must be cut and a sub-frame welded in.
  For the installed base, T0 (software, €10–215, team estimate) is the realistic first step.
- **The platform scale (€7,860–22,160 factory-fit, team estimate on [27])** matches Tommi's "almost as expensive"
  [36] if he meant the machine price: the scale itself is the smaller part; foundation, labour and calibration
  double it.
- Payback belongs to the business case (PRODUCT.md §1). `part1/installed_cost.json` carries every line for it.

> **TOMMI (Q10):** We assume Europress funds the hardware (free to the customer) and that a factory-fit option cost
> near €2,000 per unit [36] is acceptable when the per-tonne fees pay it back (team estimate). Tommi's own point: a customer who saves
> the €2,000 by choosing a unit without weighing makes the network less valuable [36].

## 8. Accuracy

### 8.1 Error accumulation over a container fill (H1)

Closed form (`calc/error_accumulation.py`) and Monte Carlo on the real synthetic lift sequence
(`scripts/charge_sum.py`, mid parameters):

| material | reference lifts | RMS error before calibration (sim / closed form) | floor after calibration (sim / closed form) |
|---|---|---|---|
| biowaste | 1206 | 6.8 % / 5.4 % | 3.3 % / 3.9 % |
| cardboard | 1864 | 8.9 % / 8.9 % | 2.8 % / 3.3 % |
| mixed_plastic | 172 | 8.9 % / 8.1 % | 3.0 % / 3.6 % |
| mixed_waste | 1470 | 5.8 % / 6.3 % | 2.4 % / 3.4 % |
| paper | 144 | 10.1 % / 6.5 % | 3.2 % / 3.7 % |
| plastic_film | 771 | 11.1 % / 8.0 % | 3.1 % / 3.5 % |
| **all (low / mid / high)** | 5627 | 6.3 / 8.2 / 13.3 % | 2.1 / 2.9 / 4.9 % |

![Figure 4: charge summing](figures/charge_sum.svg)

*Figure 4. H1 container-total error per material, before calibration and after an ideal per-device correction.*

The random part shrinks with the number of charges and is about 1–4.5 % of the container. The bridging bias stays;
it is removed by calibration (§4). The floor after calibration, about 3 %, comes from how much the bridging share
changes from one container to the next (team estimate 2–5 %), and it is the number to measure in the pilot.

### 8.2 H1 error budget (per charge, 1σ, team estimate; `calc/h1_params.py`)

| Source | low / mid / high | Effect on the container total | Mitigation |
|---|---|---|---|
| Reading noise per reading | 0.3 / 0.5 / 1.0 kg | √N, ~5–15 kg per container | 2–3 s average at rest |
| Bridging share, mean per material | 1–6 % (by material), our guess off by 30–100 % | bias | H2 calibration |
| Bridging share, device to device | 2 / 3 / 5 % | bias per device | H2 calibration |
| Bridging share, charge to charge | 5 / 10 / 20 % of the charge | √N | averages out |
| Bridging share, container to container | 2 / 3 / 5 % | **floor after calibration** | none (measure in pilot) |
| Gain after test-weight commissioning | 0.5 / 1 / 2 % | bias | H2 calibration |
| Strokes without a valid reading pair | 0.5 / 1 / 3 % | bias + small random | firmware delay, H2 |
| Gain drift (debris, wear) | 0.3 / 0.5 / 1 % per month | slow bias | Kalman random walk, jam alarm |
| Temperature (B and A 1 min apart) | 0.02–0.04 kg per charge | negligible | differential reading |

The v1 T1 strain-gauge budget, now with the support-position line added by the red team (RED_TEAM R9):

| Error source (1σ, % of a ~3 t load) | low | mid | high | Mitigation |
|---|---|---|---|---|
| Reading noise (bridge + 24-bit ADC, averaged) | 0.2 | 0.3 | 0.5 | average 10-30 s of samples at rest [7] |
| Temperature drift (-30..+35 C) | 0.5 | 1.0 | 1.5 | full bridges + board temperature model [14] |
| Calibration gain/offset residual | 0.5 | 0.8 | 1.5 | reference weights + ticket cross-check |
| Off-centre load / load path | 0.5 | 1.0 | 2.0 | 4 points, sum of bridges |
| Friction / hysteresis at supports | 0.5 | 0.8 | 1.5 | read after settling, ram retracted |
| Residue + press-cycle disturbance | 0.3 | 0.5 | 1.0 | auto-zero after each lift; read only at rest |
| Support position after each set-down (mainly COMBI; v2) | 0.5 | 2.0 | 4.0 | frame strain measures bending, not reactions: ticket cross-check |
| **Combined (root-sum-square)** | **1.2** | **2.8** | **5.3** | estimate |

### 8.3 What the accuracy is worth (data-backed, v1 method)

`scripts/accuracy_value.py` re-measures 5,787 shared single-load, weighed-tare tickets with each tier's mid error
model [16]:

| Tier (mid σ) | 2.5–3.5 t loads within ±100 kg | median cost-per-tonne error | +10 % over-billing flagged on one load | false alarms | loads to see a 3 % difference |
|---|---|---|---|---|---|
| T0 (10 %, 150 kg) | 25% | 8.6 % | 13% | 2.2 % | 45 |
| T1 (2.8 %, 30 kg) | 77% | 2.1 % | 81% | 1.9 % | 4 |
| T2 (0.6 %, 15 kg) | 100% | 0.7 % | 94% | 0.8 % | 1 |
| **H1 (3.4 %, 10 kg)** | **70%** | **2.3 %** | **77%** | **1.8 %** | **6** |
| H5 (1 %, 20 kg) | 100% | 1.0 % | 92% | 1.3 % | 1 |
| PS (0.5 %, 20 kg) | 100% | 0.8 % | 92% | 1.2 % | 1 |

The ±100 kg on a 3 t load is **the dataset's simulation target, not a Europress specification** [2]. H1 at mid
lands 70 % of 2.5–3.5 t loads within it, which is not settlement grade and is not meant to be.

## 9. Fusion with what the compactor already measures (H3)

`scripts/fusion.py` on the synthetic data:

| Signal | What it gives (synthetic data) |
|---|---|
| T0: fill × volume × learned density (fill only) | median abs error 5.8 %, robust σ 8.6 %, p90 20.0 %, but RMS 89.5 % (heavy outliers) over 3741 lifts |
| T0 + press load index | median abs error 7.7 % vs 5.7 % fill-only on the same 1835 lifts (second half of the year) |
| H1 + H2 fused with T0 (inverse variance) | RMS 3.38 % → 3.25 % (weight on H1 0.881, T0 used on 94% of lifts after an agreement gate) |
| Compaction-cycle counter → plate-jam alarm (10 strokes with no weight change) | biowaste 25.3 h, cardboard 12.0 h, mixed plastic 29.3 h, mixed waste 22.1 h, paper 78.4 h, plastic film 29.5 h |

- **T0 alone** (fill × volume × learned density) is surprisingly good on the median in the synthetic world (5.8 %)
  but has heavy outliers (fill faults, residue, biowaste), so it is a fallback, not a primary weight. The kit's
  press-load index made it worse, not better; real pressure curves were not available (TOMMI Q8).
- **Fused with H1 + H2**, T0 adds little (3.38 % → 3.25 % RMS) because H1 is already much better. Its value is
  **redundancy**: when the plate is faulted, T0 keeps the weight flowing at T0 accuracy, and a large H1–T0
  disagreement is itself a fault signal.
- **The cycle counter is the most useful existing signal**: it tells H1 how many charges it should have weighed, so
  a jammed or bridged plate is found within about a day (12–78 h by material).

## 10. Comparison of the candidates (H4)

Interface values (`sigma_tiers.json`, generated by `scripts/tiers.py`; σ after calibration, BOM = factory-fit
hardware lines of §7):

| Tier | Name | σ rel % (low / mid / high) | σ abs kg floor (low / mid / high) | BOM EUR per device | Install h | Weak for | Evidence | Sources |
|---|---|---|---|---|---|---|---|---|
| T0 | Virtual weight (existing hydraulic pressure + fill) | 5.0 / 10.0 / 20.0 | 100 / 150 / 300 | €0–50 team estimate (software only) | 0–1 | BIOWASTE, WET_CARDBOARD, MIXED_WASTE | estimate | [1] [3] [13] |
| T1 | Cheap strain gauges on frame / container rails | 1.2 / 2.8 / 5.3 | 20 / 30 / 50 | €100–480 [4][5][6][7] + team estimate | 4–8 | LOADS_UNDER_0.5T, COMBI_SUPPORT_CHANGES | estimate | [4] [5] [6] [7] [14] |
| T2 | Shear-beam load cells under the frame | 0.3 / 0.6 / 1.0 | 10 / 15 / 25 | €1,160–2,600 [8][9][10][11][26] + team estimate | 8–16 | – | literature | [8] [9] [10] [11] [12] [13] [26] |
| H1 | Hopper-stage weighing plate + fleet self-calibration (hopper idea: Europress) | 2.3 / 3.4 / 5.4 | 5 / 10 / 20 | €270–1,430 [6][9][10][22][25] + team estimate | 10–20 | RETROFIT_UNITS, BIOWASTE_LIQUIDS, NEW_DEVICE_BEFORE_TICKETS | estimate | [22] [25] [28] [29] [36] |
| H5 | Weighing guide rails (team idea) | 0.6 / 1.0 / 2.0 | 10 / 20 / 40 | €1,310–3,100 [8][9][10][11][23][26] + team estimate | 12–24 | SITES_WITHOUT_RAILS, ICE_AND_DEBRIS | estimate | [8] [12] [13] [20] [26] [27] |
| PS | Platform scale under the whole unit (Europress's existing option) | 0.2 / 0.5 / 1.0 | 10 / 20 / 40 | €4,800–12,000 [27] + team estimate | 16–32 | COST | estimate | [27] [36] |

| | T0 virtual | T1 strain gauges | **H1 hopper plate + H2** | H5 weighing rails | T2 cells in frame | PS platform scale |
|---|---|---|---|---|---|---|
| Installed, factory-fit (§7, team estimate) | €10–125 | €226–1,179 | **€548–2,363** | €2,382–7,056 | €1,635–4,338 | €7,860–22,160 |
| 1σ after calibration (*estimate*) | 5–20 % | 1.2–5.3 % | **2.3–5.4 %** | 0.6–2 % | 0.3–1 % | 0.2–1 % |
| COMBI | yes | gauges travel, frame bending changes per set-down | **yes, isolated from unit load** | yes, ground side, 8–9.5 t range | cells travel with the unit | yes |
| DUO | yes | yes (stationary rails) | **yes, same part** | yes, coupling bypass risk | per container, impractical | yes |
| Retrofit | remote | 4–8 h on site | hard (floor cut) | site work | hard | site work |
| Durability risk | none | gauges in the main load path | stops, seal, liquids | ice, debris, set-down | transport shocks | low |
| Main weakness | outliers, biowaste | support changes on COMBI | bridging bias (needs H2) | cost, site work | cost, transport | cost |

**Why H1 and not the others.**
- Against **PS** (the prior attempt [36]) and **H5**: both weigh the whole unit or container, so they need heavy
  cells, restraint and site work, and they cost more than the ~€2,000 reference [36] in our model (team estimate, §7); they are far more
  accurate than planning needs. H5 is the right choice where a site needs near-settlement accuracy (§14 fallbacks).
- Against **T1**: T1 is cheaper, but on a COMBI frame strain measures bending, which depends on where the unit
  stands after each set-down, and the gauges carry the full lifting loads [36]; H1 answers Tommi's "where would the
  sensor be?" by taking the sensor out of that load path. If the bench test (§14) fails, T1 on DUO rails is the
  fallback.
- Against **T0**: T0 needs no hardware and should ship first as software for the installed base, but it is weak for
  biowaste [3] and has heavy outliers (§9).

## 11. Prior art (WG5) and what is new

Search on 7 Nov 2026 (Google Patents, vendor sites; not a freedom-to-operate search):

| # | Prior art | What it does | How ours differs |
|---|---|---|---|
| [28] | US 6,427,585 B1 / US 6,138,557 (Marathon Equipment, priority 1999, expired) | Transfer-station compactor on load cells; records the weight increase after each addition of waste before compaction and keeps a running total | Same per-charge running-total idea, but the whole apparatus is weighed. H1 weighs only a plate in the charging zone, so the cells are 10–20× smaller |
| [29] | US 2023/0219317 A1 (vertical refuse baler) | Floating bed on a load cell under the compaction chamber floor, mechanical stop to protect the cell | Very close to the H1 plate hardware (floating floor + stop). Ours is in a horizontal container compactor and reads before/after each stroke. **FTO check needed** |
| [30] | US 11,148,383 B2 (BACE, active) | Retrofit shear-beam load cells under a baler frame, weighs material independently of the press force, tags each bale | Weighs the whole machine; H1 weighs the charge |
| [31] | US 12,379,240 B1 (Canalytics, active, granted 2025) | Hydraulic piston scales on the ground under the casters of a detachable compactor container; rails only guide | Close to **H5 on a DUO**. H5 puts cells under the rails; **FTO check needed before H5** |
| [32] | US 4,729,304 (refuse compactor and transfer chamber) | Weight sensors under the chamber stop charging at a set weight | Whole-chamber weighing, transfer stations |
| [27] | WEDI container scale (product) | 15 t weighing beams with ramps on 4 × 5 t cells for roll-off containers | Same physics as H5; H5 integrates it into Europress's guide rails |
| [35] | Avermann MPC press containers (product) | "Weighing system for exact cost calculation" offered as an option | Construction not published; shows the market exists |
| [12][13][38] | Hyva hook-loader weighing, Vulcan roll-off scale, Pfreundt roll-off scale (products) | Weigh the container on the truck, ≤ 1 % claimed | Truck-side, owned by the operator; FullLoad needs the weight at the source |
| [33][34] | Enviroweigh bin-lift weighing; EP2544968B1 bin with load cells per deposit | Weigh each bin or deposit (pay-as-you-throw) | Per-deposit weighing exists for bins; H1 does it inside a compactor |

**Novelty (WG6).** Weighing each charge and keeping a running total is **not new** [28]; a floating floor on load
cells with a stop is **not new** [29]. The hopper-stage direction for Europress's compactors is Europress's own
idea [36]. What we did not find in this limited search is the combination of a charging-zone plate read before and
after each stroke **with** fleet-level self-calibration from shared weighbridge tickets; we did not search the
calibration side in depth, so we claim **no novelty**, only a product combination worth an FTO search.

## 12. Installation and retrofit

**H1 factory-fit (2–4 h on the line, team estimate):** fit the plate sub-frame when the chamber floor is welded,
mount cells, stops, side stays and seal, wire the weighing board to the SMART modem, end-of-line check with four
25 kg test weights at two positions (0.5–1 h).

**H1 retrofit (10–20 h, team estimate):** COMBI to a workshop (hook-lift round trip, operator's truck), DUO on site;
cut the floor opening, weld the sub-frame, fit plate and cells, wire, commission with test weights. Needs a
structural check of the chamber floor per machine family (ENGINEER_QUESTIONS Q1).

**H5 (retrofit 12–24 h, team estimate):** level and anchor two rail bases, fit cells, stops and check rods, run the
cable to the unit, calibrate with a known load. On a new site the base is built anyway (6–12 h extra).

**T0:** firmware and back-end update; calibration comes from tickets (H2).

## 13. Calibration

1. **Factory / end of line (H1):** test weights on the plate set the cell gain (residual 0.5–2 %, team estimate).
2. **Every stroke (H1):** the differential reading is its own zero; drift between strokes is negligible.
3. **Every lift:** the sum resets when the emptied COMBI returns or an empty DUO container docks; H5 re-tares.
4. **Every shared ticket (H2):** updates the device's gain; a new device starts from its sister machines (§4).
5. **Drift watch (v1 method):** a rolling device/ticket ratio outside ±5 % proposes a recalibration for a person to
   approve (`scripts/drift_watch.py`, `figures/drift_watch.svg`); the cycle-count jam alarm catches hard faults (§3.2).
6. **No tickets:** devices whose operator never shares get the fleet prior plus an annual test-weight check.

## 14. Validation experiment (plan, untested)

| Stage | What | Pass criterion (proposal) | Time |
|---|---|---|---|
| A. Bench, plate | One charging chamber with the plate, on a rig. Drop tests (9–30 kg bags, 25 kg dense item, 1.1 m), 10,000 ram cycles, grit, ice and leachate in the gap | No cell damage; zero shift < 0.5 kg after 10,000 cycles; differential error < 0.5 kg per charge | 3–4 weeks (team estimate) |
| B. Bench, bridging | Real cardboard, film, mixed and bio charges, weighed separately, then through the chamber | Bridging share per material measured (replaces our 1–6 % guess) | 1–2 weeks |
| C. Field pilot | 10 COMBI + 10 DUO, operators that share tickets, every lift paired with a single-load weighed-tare ticket | After 10 tickets, 1σ of the container total ≤ 5 % per device (planning grade, TOMMI Q9); H2 n = 0 error ≤ 6 % on held-out devices | 3 months |
| D. Durability | Count strokes, COMBI tipping cycles and jam alarms | No plate seizure that the cycle-count alarm does not catch within 24 h | during C |

If stage A fails, fall back to T1 on DUO rails and T0 on COMBI; if C misses only on cardboard, accept a higher σ
there or use H5 at cardboard-heavy sites.

## 15. Limitations

- **Untested.** No hardware was built or measured; every σ and euro is an *estimate*, a *simulation target* or
  *literature*; the dataset's masses are synthetic [1][2]; the team has no mechanical-engineering expertise.
- **Bridging and partial charges (H1).** The share of a charge carried by the walls or the ram is our guess (1–6 %).
  Its container-to-container variation sets the floor after calibration.
- **Biowaste.** For H1: liquids in the plate gap, corrosion and sticking (RED_TEAM R4); for T0: little
  back-pressure, so the pressure fingerprint says little [3].
- **Humidity and moisture change the real weight.** Wet cardboard is heavier and its weight changes during the week
  [3]; every weighing option measures that water, and the weighbridge does too.
- **Temperature drift.** Negligible for H1 (differential), 0.3–0.7 % for H5, large for T1 strain gauges (§8.2);
  below −10 °C the cells' datasheet gives no figure [20].
- **Off-centre loads.** H1: a charge landing half on the ram is partly unweighed (bridging share). H5/PS: summing
  four cells handles it. T1: off-centre load and support position change the reading.
- **The press cycle disturbs readings.** Ram and floor forces are hundreds of times the charge; readings are valid
  only with the ram retracted and settled, and the press start must wait 2–3 s.
- **Overloads.** Misuse impacts up to ~12 t and 7–14 t on every stroke depend on overload stops with a sub-millimetre
  gap that grit or ice can block (RED_TEAM R3).
- **Tickets.** H2 needs shared tickets; some operators share none [2]. Ticket errors and lags are not modelled.
- **Retrofit.** H1 is a factory-fit design; retrofit costs €1,270–4,923 (team estimate).
- **Not legal for trade** [15]. Billing stays on the operator's weighbridge (PRODUCT.md §1).
- **Freedom to operate** is not checked ([29][31]).

## 16. Brief coverage (QG1)

| Item in the challenge brief [1] and the v2 brief | Section |
|---|---|
| Sensor / measurement principle | §3.1 (H1), §6 (H5), §10 (others) |
| Placement | §5.1 COMBI, §5.2 DUO, §6, Figure 1 |
| Indicative bill of materials and cost | §7, Appendix A |
| Installation | §12 |
| Retrofit potential | §7, §12 |
| Calibration | §13, §4 |
| Error sources | §8.2, §15 |
| Accuracy reasoning / accuracy target | §1, §8, Figures 2–4 |
| Limitations | §15 |
| Validation plan / experiment | §14 |
| Comparison of sensing options | §10, Figure 3 |
| v2: our edge (H1 + H2), prior art, pitch summary | §4, §11, §0 |
| Third-party sources and licences | `THIRD_PARTY_part1.md` |

## 17. How this feeds FullLoad

The app reads `sigma_tiers.json` (same shape as v1; six tiers; `chosen_tier` = H1). The accuracy slider moves σ
between a tier's low, mid and high values. `installed_cost.json` gives the business case the full installed cost per
device, retrofit and factory-fit. Beat 1 shows Figure 1, the cost row of §7 and the learning curve (Figure 2).
Europress measures and verifies, and never transports; FullLoad is the product name.

## References

Web sources accessed 6–7 Nov 2026; prices ex VAT unless stated. Some pages block automated fetches; for those the
figure comes from the search listing, as marked.

- [1] Europress Group Oy / Since AI: *SMART Material Value Engine — Weigh at Source, Create Value*, challenge brief
  (local file `resources/Europress_SinceAI_2026_Challenge_Brief_BUILDER_FINAL (1).pdf`).
- [2] Europress × Since AI starter kit v1.0.1: `docs/ASSUMPTIONS_AND_LIMITATIONS.md`, `configs/assumptions.yaml`,
  `docs/EUROPRESS_REVIEW.md` point 1.7, `docs/DATA_DICTIONARY.md` (local files, synthetic data).
- [3] Europress kickoff, Tommi Häkkinen, 6 Nov 2026. Whisper transcript `Röst 261106_182238.txt` (local, imperfect).
- [4] DigiKey UK, Micro-Measurements CEA-06-250UWA-350 strain gauge, £60.29–72.87 per 5.
  https://www.digikey.co.uk/en/products/detail/micro-measurements-division-of-vishay-precision-group/CEA-06-250UWA-350/10414998
- [5] Newegg, 10 pcs BF350-3AA foil strain gauges, $18.40 (search listing). https://www.newegg.com/p/1W7-00WA-035U7
- [6] Electrokit, HX711 load-cell amplifier board, 45 SEK incl. VAT.
  https://www.electrokit.com/en/hx711-lastcellsforstarkare-monterad-pa-kort
- [7] Texas Instruments ADS1232 24-bit bridge ADC. https://www.ti.com/product/ADS1232
- [8] KERN & SOHN, load cell CT 5000-3Q1, 5 t shear beam, C3 (0.017 %), IP68, €435 net.
  https://kern-sohn.com/shop/en/products/measuring-technology-components/measuring-cells/CT-5000-3Q1
- [9] KERN & SOHN, junction box CJ X468, 4 channels, IP68, €130 net.
  https://kern-sohn.com/shop/en/products/measuring-technology-components/junction-boxes/CJ-X468
- [10] Fruugo IE, DIN-rail weighing transmitter 4–20 mA / RS485, €51.95 (search listing).
  https://www.fruugo.ie/din-rail-force-gauge-4-20ma-output-rs485-controller-high-precision-weighing-display-module-basic-style/p-460908759
- [11] WeighTech USA, Laumas TLB4 4-channel transmitter, $350 (search listing).
  https://weightechusa.com/laumas-digital-weight-transmitter-tlb4-multi-channel
- [12] Hyva, Titan hookloader weighing system, ≤ 1 % (vendor claim).
  https://hyva.com/en/news/vertical-stabilizer-and-weighing-system-add-to-the-power-of-titan-hookloaders
- [13] Recycling Product News, "On-board weighing systems" (Vulcan roll-off scale, ~1 %, vendor claim).
  https://www.recyclingproductnews.com/article/7414/on-board-weighing-systems
- [14] Micro-Measurements Tech Note TN-504-1 (mirror https://docs.ampnuts.ru/eevblog.docs/VPG/tn504.pdf); HBK LS31HT
  weldable gauges https://www.hbkworld.com/en/products/transducers/strain/experimental-testing/special-applications/ls31
- [15] Directive 2014/31/EU on non-automatic weighing instruments. https://eur-lex.europa.eu/eli/dir/2014/31/oj
- [16] Starter kit v1.0.1 `examples/weighing_accuracy_value.py` (adapted with attribution in `scripts/accuracy_value.py`).
- [17] machinetools.com, Europress COMBI model page: infeed 1,500 × 900 mm, infeed height 1,480 mm, compaction force
  25 t, press cycle 42 s (search listing).
  https://www.machinetools.com/en/models/europress-combi
- [18] Third-party listings of used 20 m³ Europress units: "Combio 20", 4,010 kg (https://www.finn.no/434718104);
  CMAX 20 m³, 4,435 kg empty (https://www.werktuigen.com/europress-cmax/wt-181-00081) (search listings).
- [19] Shear-beam deflection at rated load: Applied Measurement SBR 0.2–0.4 mm (https://appliedmeasurement.com.au/product/sbr/);
  Lahti Precision BC5 < 0.4 mm (https://lahtiprecision.fi-p.seravo.com/wp-content/uploads/2019/08/Lahti_Precision_Load-Cell_BC5_EN.pdf)
  (search listings).
- [20] Flintec SSB5 datasheet: safe load 200 %, ultimate 300 %, TC0 0.04 %/10 °C, TC span 0.02 %/10 °C, compensated
  −10…+40 °C, IP68. https://res.cloudinary.com/flintec/image/upload/v1778856507/strapiDev/ssb5_datasheet_en_44120d30ad.pdf
- [21] Engineering ToolBox, friction coefficients (steel on steel dry 0.5–0.8 static, 0.42 kinetic).
  https://www.engineeringtoolbox.com/friction-coefficients-d_778.html
- [22] KERN & SOHN, load cell CT 500-3Q1, 500 kg, C3, IP68/IP69K, €220 net.
  https://kern-sohn.com/shop/en/products/measuring-technology-components/measuring-cells/CT-500-3Q1
- [23] Central Carolina Scale, weigh module catalog: 5,000 kg module with lift-off / tip-over protection, $1,225
  (search listing). https://www.centralcarolinascale.com/Weigh-Module-Catalog.pdf
- [24] City of Turku, contract rates for additional work 2024: fitter €55/h ex VAT (search listing).
  https://ah.turku.fi/kh/2024/1028025p/Images/2337276.pdf
- [25] IndiaMART, ADI Controls ASP-631 single-point load cell, IP67, ₹1,200 (search listing).
  https://m.indiamart.com/proddetail/adi-controls-asp-631-single-point-platform-load-cell-2854775790591.html
- [26] San Diego Scale, Zemic BM8H 10 klb stainless shear-beam load cell, IP68, $262.50.
  https://sandiegoscale.com/products/zemic-bm8h-10klb-stainless-steel-shear-beam-load-cell-oiml-approved
- [27] Werktuigen.com, WEDI container scale for roll-off containers: 15 t, 4 × 5 t cells, weighing beams and ramps,
  €4,800 (description: €5,620) + VAT, new. https://www.werktuigen.com/firma+wedi+gmbh-containerwaage/wt-591-0742
- [28] US 6,427,585 B1, Marathon Equipment, *Method and apparatus for measuring the length of a waste log and/or weight
  of waste log…* (continuation of US 6,138,557). https://patents.google.com/patent/US6427585B1/en
- [29] US 2023/0219317 A1, vertical refuse baler with floating bed on a load cell and mechanical stop.
  https://ipiq.io/patents/386072
- [30] US 11,148,383 B2, BACE LLC, *Weight-measurement retrofitting for recyclable-waste balers*.
  https://patents.google.com/patent/US11148383B2/en
- [31] US 12,379,240 B1, Canalytics Technologies, *Method and apparatus for measuring the weight of a container using
  load cells*. https://patents.google.com/patent/US12379240B1/en
- [32] US 4,729,304, *Refuse compactor and transfer chamber* (search listing).
  https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4729304
- [33] Transport Engineer, "Weigh for pay" (Enviroweigh bin-lift weighing, search listing).
  https://www.transportengineer.org.uk/content/features/weigh-for-pay
- [34] EP2544968B1, *Bin for collecting solid waste* (load cells per deposit, search listing).
  https://patents.google.com/patent/EP2544968B1/it
- [35] Avermann MPC 10 P/E press container brochure, weighing system option (search listing).
  https://machines.interzero.at/files/products/avermann/MPC%2010%20P_E.pdf
- [36] Europress follow-up talk, Tommi Häkkinen, 7 Nov 2026. Whisper transcript `Since.AI.2.txt` (local, Finnish,
  noisy): hopper-stage idea, ~3 t machine and ~5 t waste, platform scales "almost as expensive", basic COMBI
  €20–25k, ~€2,000 option reference.
- [37] OptiCare Expert service price list: maintenance on site €152/h ex VAT (search listing; upper bound only).
  https://www.optiscangroup.com/wp-content/uploads/2024/03/OptiCare-Expert-Palveluhinnasto.pdf
- [38] Pfreundt roll-off dumper scale catalogue (search listing).
  https://pdf.directindustry.com/pdf/pfreundt-gmbh/roll-off-dumper-scale/91271-656882.html

## Appendix A. Installed cost, line by line (`generated/calc_installed_cost.md`)

### T0: Virtual weight from existing pressure + fill (v1)

| H6 line | what | retrofit | factory-fit | source |
|---|---|---|---|---|
| sensors | none (existing pressure, ram position, fill) | €0–0 | €0–0 | [3] existing sensors |
| electronics | none, or a faster pressure log | €0–50 | €0–50 | team estimate |
| mechanical | none | €0–0 | €0–0 | team estimate (none needed) |
| site work | none | €0–0 | €0–0 | team estimate (none needed) |
| labour | remote firmware update; 0–1 h on site | €0–90 | €0–0 | team estimate × rate [24] |
| calibration | learned from shared weighbridge tickets (H2) | €0–0 | €0–0 | scripts/self_calibration.py |
| maintenance (6 y) | none beyond software | €0–0 | €0–0 | team estimate |
| development (NRE) | model, firmware, back end: €50–150k | €10–75 | €10–75 | team estimate |
| **total** |  | **€10–215** | **€10–125** | sum of lines |


### T1: Strain gauges on frame / container rails (v1 choice)

| H6 line | what | retrofit | factory-fit | source |
|---|---|---|---|---|
| sensors | 16 foil gauges for 4 full bridges | €25–280 | €25–280 | [4][5] |
| electronics | 24-bit bridge board, temperature sensor, connector | €10–60 | €10–60 | [6][7] + team estimate |
| mechanical | gauge covers, coating, cable, glands, enclosure | €60–140 | €60–140 | team estimate (v1 §4) |
| site work | none | €0–0 | €0–0 | team estimate (none needed) |
| labour | retrofit 4–8 h; factory 1–3 h | €220–720 | €55–270 | v1 §5 hours × rate [24] |
| calibration | water IBC (~1 t) at two positions, 1–1.5 h | €55–135 | €28–90 | v1 §6 × rate [24] |
| maintenance (6 y) | 30–60 % chance of re-gauging one point (2–4 h + parts) | €39–264 | €39–264 | team estimate |
| development (NRE) | gauge layout per family, test rig, firmware: €50–150k | €10–75 | €10–75 | team estimate |
| **total** |  | **€419–1,674** | **€226–1,179** | sum of lines |


### H1: Hopper-stage weighing plate (idea: Europress / Tommi)

| H6 line | what | retrofit | factory-fit | source |
|---|---|---|---|---|
| sensors | 4 × 500 kg C3 IP68 cells under the plate | €100–880 | €100–880 | [22] €220 each list; low end [25] ≈€12 per cell + team estimate for volume C3 |
| electronics | 4-channel 24-bit ADC / weighing board on the SMART modem, junction | €25–180 | €20–150 | [6] HX711 board, [10] €51.95 transmitter, [9] €130 junction box; team estimate |
| mechanical | plate 1.4 × 0.8 m wear steel, cell mounts, overload stops, side stays, perimeter seal | €400–1,000 | €150–400 | team estimate (retrofit: cut the chamber floor and weld a sub-frame) |
| site work | none on site; COMBI retrofit: hook-lift round trip to a workshop | €0–400 | €0–0 | team estimate |
| labour | retrofit 10–20 h (cut, weld, fit, wire); factory 2–4 h on the line | €550–1,800 | €110–360 | hours team estimate × rate [24] |
| calibration | test weights (4 × 25 kg) on the plate, firmware set-up | €55–180 | €28–90 | team estimate × rate [24] |
| maintenance (6 y) | clean the seal gap at each service (0.25 h/yr), new seal, 30–40 % chance of one cell | €110–283 | €110–283 | team estimate |
| development (NRE) | plate design per machine family, firmware gating, field test: €150–400k | €30–200 | €30–200 | team estimate |
| **total** |  | **€1,270–4,923** | **€548–2,363** | sum of lines |


### H5: Weighing guide rails (idea: team)

| H6 line | what | retrofit | factory-fit | source |
|---|---|---|---|---|
| sensors | 4 × 5 t shear-beam C3 IP68 cells | €900–1,740 | €900–1,740 | [26] Zemic BM8H $262.50 ≈ €225–250; [8] KERN CT 5000 €435 |
| electronics | IP68 summing box + weighing transmitter to the SMART modem | €110–460 | €110–460 | [9] €130 box (low: board-level summing, team estimate), [10] €51.95–[11] $350 transmitter |
| mechanical | rail modification and cell seats, overload stops, lift-off and side restraint (check rods) | €500–1,400 | €300–900 | team estimate; [23] a 5 t weigh module with lift-off/tip protection lists $1,225 |
| site work | level and anchor two rail bases (concrete pads), cable conduit to the unit | €800–2,500 | €300–1,000 | team estimate (factory-fit = new site where the base is being built anyway) |
| labour | retrofit 12–24 h (2 technicians); new installation 6–12 h extra | €660–2,160 | €330–1,080 | hours team estimate × rate [24] |
| calibration | known load on the rails (water IBCs or hired test weights), commissioning | €150–800 | €150–800 | team estimate |
| maintenance (6 y) | clean under the rails, ice and debris checks 0.5–1 h/yr; 30–60 % chance of one cell; cable repair | €282–1,001 | €282–1,001 | team estimate |
| development (NRE) | rail design, restraint, firmware: €50–150k | €10–75 | €10–75 | team estimate |
| **total** |  | **€3,412–10,136** | **€2,382–7,056** | sum of lines |


### T2: Load cells under the unit's own frame (v1)

| H6 line | what | retrofit | factory-fit | source |
|---|---|---|---|---|
| sensors | 4 × 5 t shear-beam C3 cells | €900–1,740 | €900–1,740 | [26][8] |
| electronics | summing box + transmitter | €110–460 | €110–460 | [9][10][11] |
| mechanical | cell mounts in the frame, frame adaptation, stops | €200–600 | €150–400 | team estimate (v1 §4) |
| site work | none (cells travel with a COMBI) | €0–0 | €0–0 | team estimate (none needed) |
| labour | retrofit 8–16 h; factory 3–6 h | €440–1,440 | €165–540 | v1 §5 hours × rate [24] |
| calibration | known load, commissioning | €150–500 | €150–500 | team estimate |
| maintenance (6 y) | cells travel with a COMBI: 40–80 % chance of one cell, cable | €140–548 | €140–548 | team estimate |
| development (NRE) | frame redesign per family, structural review: €100–300k | €20–150 | €20–150 | team estimate |
| **total** |  | **€1,960–5,438** | **€1,635–4,338** | sum of lines |


### PS: Platform scale under the whole unit (Europress's existing option)

| H6 line | what | retrofit | factory-fit | source |
|---|---|---|---|---|
| sensors | 4–6 heavy cells (included in the platform price) | €0–0 | €0–0 | [27] (in the platform price) |
| electronics | indicator / transmitter (included) | €0–0 | €0–0 | [27] (in the platform price) |
| mechanical | steel weighing platform or beams with ramps, ~15 t | €4,800–12,000 | €4,800–12,000 | [27] container scale €4,800–5,620 (beams + ramps, 15 t); full deck high end team estimate |
| site work | foundation or pit, ramps, anchoring, drainage | €2,000–6,000 | €1,500–5,000 | team estimate |
| labour | 16–32 h retrofit; 12–24 h new site | €880–2,880 | €660–2,160 | team estimate × rate [24] |
| calibration | test weights by a scale service | €400–1,500 | €400–1,500 | team estimate |
| maintenance (6 y) | annual check, cleaning, one cell | €500–1,500 | €500–1,500 | team estimate |
| development (NRE) | exists today | €0–0 | €0–0 | [36] |
| **total** |  | **€8,580–23,880** | **€7,860–22,160** | sum of lines |

## 18. Human-review list (QG11)

A person with machine knowledge must confirm these before the concept is shown as feasible (the same questions,
phrased for Discord, are in `ENGINEER_QUESTIONS.md`):

1. A 1.4 × 0.8 m section of the **charging-chamber floor** can be a separate plate on load cells without weakening
   the chamber, on COMBI and DUO alike.
2. The **ram rides on side guides or wear strips**, not on the floor area where the plate would sit.
3. Overload stops with a **0.24–0.48 mm gap** can carry 7–14 t of floor pressure every stroke and misuse impacts up
   to ~12 t, and a seal can keep grit, ice and leachate out of the gap.
4. The automatic press start can wait **2–3 s** after the door closes so the plate can be read.
5. Our guess of the **bridging share** (1 % biowaste to 6 % cardboard of a charge hanging on walls or ram) is
   plausible for Europress hoppers.
6. Liquids that run back into the chamber when a COMBI is **tipped for emptying** do not flood the plate's cells.
7. The SMART modem has a free port and power for a 4-channel weighing board, and logs **door and cycle events**.
8. For H5: guide rails can carry the **whole** weight of a COMBI (8–9.5 t) or a DUO container, and a DUO coupling
   does not carry part of the container's weight.
9. For H5: the hook-lift **set-down speed** and the horizontal pull force (our 3.8–7.6 t on dry skids) are in the
   right range.
10. Why the existing **platform scales** are expensive, so that our cost model for PS and H5 can be checked.

### Review of this list (lead developer with Claude, 7 Nov; no mechanical-engineering expertise on the team)

| # | Verdict | Reasoning |
|---|---|---|
| 1 | Plausible, needs Europress | A floor insert is a common way to weigh in a hopper, but stiffness of the chamber around a cut-out is a structural question only Europress can answer. |
| 2 | **Doubtful** | In many compactors the ram slides on the chamber floor or on wear strips set into it. If so, the plate sits in the ram's path and must survive the ram scraping over it every stroke. This is the biggest open risk for H1. |
| 3 | **Doubtful** | A sub-millimetre stop gap in a waste chamber (grit, ice, leachate) is fragile. A wider gap needs stiffer cells and loses resolution. Second biggest risk. |
| 4 | Likely | A short delay before the press start is a firmware change. |
| 5 | Unknown, order of magnitude plausible | Only a bench test (§14 B) settles it. |
| 6 | Needs Europress | COMBI tipping drains the chamber; the cells need drainage and IP68 sealing. |
| 7 | Needs Europress | Engineer question 10. |
| 8 | Unknown | Decides whether H5 is cheap; engineer question 8. |
| 9 | Plausible order of magnitude | From the load calculations in `calc/loads.py`. |
| 10 | Partly answered | Tommi: existing scale platforms are "almost as expensive"; the team document names Scaletipper X1 as expensive and limited to bin-fed sites. |

Consequence: H1 has two doubtful mechanical points (2, 3). It stays the factory-fit reference credited to Europress,
and the hydraulic self-lift (H7) is added as the team's new idea to explore (§19).
