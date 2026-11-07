# calc/installed_cost.py output: full installed cost per device (EUR, ex VAT, 6-year lease)

Labour at €55–90/h [24]. Reference: ~€2,000 weighing option on a €20,000–25,000 COMBI [36]. Lines summed low-with-low, high-with-high.


## Summary

| id | candidate | hardware (factory) | installed, retrofit | installed, factory-fit | factory-fit within ~€2,000? [36] | basis |
|---|---|---|---|---|---|---|
| T0 | Virtual weight from existing pressure + fill (v1) | €0–50 | €10–215 | €10–125 | yes | team estimate |
| T1 | Strain gauges on frame / container rails (v1 choice) | €95–480 | €419–1,674 | €226–1,179 | yes | [4][5][6][7][24] + team estimate |
| H1 | Hopper-stage weighing plate (idea: Europress / Tommi) | €270–1,430 | €1,270–4,923 | €548–2,363 | partly | [6][9][10][22][24][25] + team estimate |
| H7 | Hydraulic self-lift on the compactor's own power pack (idea: team) | €550–1,300 | €1,994–6,168 | €1,034–3,008 | partly | [24][39][48] + team estimate |
| H5 | Weighing guide rails (idea: team) | €1,310–3,100 | €3,412–10,136 | €2,382–7,056 | no | [8][9][10][11][23][24][26] + team estimate |
| T2 | Load cells under the unit's own frame (v1) | €1,160–2,600 | €1,960–5,438 | €1,635–4,338 | partly | [8][9][10][11][24][26] + team estimate |
| PS | Platform scale under the whole unit (Europress's existing option) | €4,800–12,000 | €8,580–23,880 | €7,860–22,160 | no | [24][27] + team estimate |


## T0: Virtual weight from existing pressure + fill (v1)

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


## T1: Strain gauges on frame / container rails (v1 choice)

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


## H1: Hopper-stage weighing plate (idea: Europress / Tommi)

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


## H7: Hydraulic self-lift on the compactor's own power pack (idea: team)

| H6 line | what | retrofit | factory-fit | source |
|---|---|---|---|---|
| sensors | 0–250 bar pressure transducer, rod position switch, oil temperature | €60–200 | €60–200 | team estimate (no supplier quote yet; [39] lists the sensor inside its €400–800 base system) |
| electronics | valve coil driver + inputs on the SMART modem, motion sensor, door / hook interlock | €50–200 | €40–150 | team estimate |
| mechanical | 80 mm single-acting cylinder with spring return, ball-joint 300 mm foot, steel housing, bellows, scraper; valve section (solenoid, pressure-compensated throttle, load-holding, relief), steel pipe, shear pin; local frame reinforcement | €800–1,800 | €450–950 | [39] parts €550–1,100 (retail −50 %, team estimate) + team estimate for reinforcement; retrofit: cut and weld the rear frame, extend the valve block |
| site work | steel or concrete pad under the foot on gravel / hot asphalt sites; COMBI retrofit: hook-lift round trip to a workshop | €0–550 | €0–150 | team estimate (calc/h7_hydraulic.py ground table) |
| labour | retrofit 12–24 h (frame, hydraulics, wiring); factory 3–6 h on the line | €660–2,160 | €165–540 | hours team estimate × rate [24] |
| calibration | tare lift, known load (water IBCs) at two positions to fix L / x, firmware set-up | €160–420 | €55–180 | team estimate × rate [24] |
| maintenance (6 y) | bellows, foot and seal check 0.5 h/yr; 30–60 % chance of a seal kit (€80–300 + 2 h); 20–40 % chance of a new pressure sensor | €234–638 | €234–638 | team estimate |
| development (NRE) | frame FEA per family, hydraulic circuit, machinery risk assessment and CE file update [48], firmware, field test: €150–400k | €30–200 | €30–200 | team estimate |
| **total** |  | **€1,994–6,168** | **€1,034–3,008** | sum of lines |


## H5: Weighing guide rails (idea: team)

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


## T2: Load cells under the unit's own frame (v1)

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


## PS: Platform scale under the whole unit (Europress's existing option)

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
