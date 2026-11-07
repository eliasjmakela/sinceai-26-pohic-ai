# Draft for WEIGHING_CONCEPT.md: §20, RED_TEAM rows, ENGINEER_QUESTIONS, cost lines

Status: draft, not merged. Source review: `reviews/DUO_MECHANISM_REVIEW.md`. Numbers come from
`/tmp/duo_scripts/check.py` and `/tmp/duo_scripts/cost.py` (outside the repo; port into `calc/h7_hydraulic.py` and
`calc/installed_cost.py` before merging if the numbers should be generated). New reference to add:

- [49] Team sheet *Duo: lift each end once, solve for weight and centre of gravity* (7 Nov 2026, 1 page, English,
  author not stated; local file `duo_mechanism.pdf`). Refers to a technical appendix that we have not seen.

Naming note for the merge: the sheet is called "Duo" because it uses **two cylinders**. It shows a CombiMax, not
a DUO compactor. We call it **H7-2** below, so "DUO" keeps meaning the Europress product line. The section title
says both, so a reader who looks for "DUO" finds the answer.

---

## 20. H7-2: two-end lift, and the DUO product (team idea)

**Status: an idea to explore, not a design.** H7-2 comes from a one-page team sheet [49]. It was reviewed
independently (`reviews/DUO_MECHANISM_REVIEW.md`). Despite its title, the sheet is about a **COMBI**, not a DUO
compactor. It gives a layout and a price for the two-end lift that §19.5 calls case C. The DUO product is still
open (§20.5).

### 20.1 Principle

H7-2 is H7 (§19.1) with a second cylinder at the other end [49]:

- a **front cylinder** under the press unit, about 0.8 m from the front;
- a **rear cylinder** about 6.2 m from the front, clear of the door's impact zone;
- **one shared pressure sensor** and the valves in the power-unit cabinet, with steel lines inside the frame;
- both feet retracted at least 30 mm above the runner underside in transport.

A reading lifts one end, then the other. In each lift the unit pivots on the runners at the far end. Two lifts
give two moment equations. Together they give the total weight W **and** its centre of mass x. No fill model is
needed for x [49].

### 20.2 Statics (`/tmp/duo_scripts/check.py`, to port into `calc/h7_hydraulic.py`)

Positions are measured from the front. a and c are the cylinders; bf and br are the front and rear pivots (the
ends of the runner contact). Rf and Rr are the cylinder forces.

- Step 1, lift the front, rear pivot: Rf·(br − a) = W·(br − x)
- Step 2, lift the rear, front pivot: Rr·(c − bf) = W·(x − bf)
- Add them: **W = [Rf·(br − a) + Rr·(c − bf)] / (br − bf)**, then **x = bf + Rr·(c − bf) / W** [49]
- Same two lifts on the emptied unit give W_empty. Net waste = W − W_empty.

The algebra is correct. It needs a < br and c > bf, which the layout meets.

Forces (team estimate: machine 3–4.5 t, press-end share 0.55–0.70 from `calc/loads.py`, waste 0–5 t, bf 0.3–0.5 m,
br 6.5–6.7 m; the sheet gives neither bore nor pivots):

| case | front cylinder kN | front bar, 80 mm bore | rear cylinder kN | rear bar, 80 mm bore |
|---|---|---|---|---|
| empty unit | 17–34 | 34–67 | 14 | 28–29 |
| full, 5 t waste | 36–64 | 71–128 | 36–49 | 71–98 |

The front peak (64 kN, 128 bar) is above H7's 57 kN design case but well under the ~200 bar on board [36]. The
80 mm bore stays the design choice. The front relief valve must be set higher than the rear one.

**Stroke.** The feet sit ≥ 30 mm above the runner underside, and the sheet lifts up to 30 mm. That is **60 mm before
any uneven ground**, and the sheet gives no stroke. We assume 80–100 mm.

### 20.3 What the second lift buys, and what it does not

It removes the largest one-end term: the waste's centre of mass x_w (2–5 % after tickets, §19.5). The rest stays.

| term | one-end H7 (§19.5) | two-end H7-2 | note |
|---|---|---|---|
| Centre of mass x_w | 2–5 % after tickets | removed | the point of H7-2 |
| Pressure sensor (shared, 0.10–0.25 % FS, 4 readings) | 1.2–3.0 % | 1.0–2.4 % of 2.5 t | 1 bar = 0.50 kN at 80 mm |
| Pivot moves 5 cm between tare and reading | ≈ 2 % | ≈ 0.9–1.1 % per pivot, ≈ 2 % if both move | not better |
| Pivot position wrong by 5 cm, but constant | absorbed by tickets | ≈ 0.3 % | cancels in W − W_empty |
| CoG height in the tilt (h = 1.5 m) | ≈ 0.07 % | 0.08 % at 10 mm, 0.25 % at 30 mm lifts | negligible |
| Seal friction, span drift, tare change, snow | as §19.5 | as §19.5, at two cylinders | unchanged |

**Accuracy (untested).** Our case C budget (§19.5) is 1.7 / 3.2 / 8.4 % at 2.5 t and 0.9 / 1.9 / 4.8 % at 5 t
(low / mid / high, 1σ, after H2 tickets). The sheet's "±5 % in 99.9 % of readings at full, 95.6 % at half fill"
implies σ ≈ 1.5 % and ≈ 2.5 % [49]. That lies between our low and mid sets. We keep our target from §19.5: **≤ 3 %
1σ at ≥ 2.5 t** after tickets. The sheet's percentages come from a simulation whose appendix we have not seen, so
they are not results.

**Contact check.** Each end is lifted at two heights (20 and 30 mm) [49]. Without contact, the force changes by only
0.06–0.09 % between them (tilt). With contact, the touching runner unloads as the lift grows, so the force rises.
A 3σ threshold on the sensor is 0.75–1.9 bar, or 38–95 kgf. So a contact that carries less than **about 1.5–4 % of a
2.5 t load** is not seen. The 30 mm lift also helps near the pivot: a point 1 m from the pivot rises 5.2 mm, not
1.7 mm (R30).

**The centre of mass as a signal.** The sheet says a sudden shift in x reveals wet or wrong material [49]. We do not
think x tells density; fill % and W do that better. Its real use is different: **x gives x_w(fill) directly**. A few
H7-2 units therefore measure the fill model that the one-end fleet needs (§19.5 mitigation 1, ENGINEER_QUESTIONS 14).

### 20.4 Safety, CE and practical limits

Everything in §19.6 applies, at both ends. New for H7-2:

- **CE.** Two automatic lifts per reading. Risk assessment and CE file under 2006/42/EC, and under Regulation (EU)
  2023/1230 from 20 Jan 2027 [48]. Hold and controlled lowering are safety functions with a performance level
  (EN ISO 13849-1).
- **The front lift moves the press end.** That end has the charging opening. Where a COMBI docks to a wall chute,
  hood or bin lifter, a 10–30 mm lift can crush against it. The fixed part can also carry load, which is a new load
  bypass. Measures: no front lift with the charging door open or the bin lifter running; a site flag for docked
  units, with only the rear lift (one-end H7) used there.
- **The front foot is in the pick-up path.** The hook lifts the front first. A front rod that is not retracted is
  dragged at once. The R26 measures (spring return, position switch, pick-up interlock) must cover both rods.
- **One sensor, two cylinders.** Isolation valves choose the cylinder. Each cylinder still needs its own
  load-holding valve, and each end its own relief setting. The sheet shows neither. A leaking isolation valve is
  detected by a pressure change while the other cylinder is idle.
- **Side tipping (R29) at both ends.** With runners 1 m apart (assumption), the support triangle is ±0.22 m wide
  at the CoG in the front lift and ±0.25 m in the rear lift. Tilt sensors (roll) reject a reading.
- **Frame.** Up to 64 kN under the press unit, which already carries the press. FEA and reinforcement (NRE line).
- **Time and energy.** About 2 minutes per reading with the press idle [49]; two pump starts. About 445 strokes a year
  per cylinder, so fatigue is not a concern on paper.

### 20.5 The DUO product: still open

A DUO is a stationary press. The truck swaps the container. The container has no hydraulics. H7-2 does not change
this. The idea of §19.3 stays: a cylinder in the compactor's docking frame lifts the coupled end of the container
~10 mm, on the press's power pack, with the container's rear rollers as the pivot. What we now know about it:

- **Load bypass.** The coupling ties container and press (R10). A reading is valid only with the coupling released.
  So it can only be taken in a defined state: for example, just before pick-up, when the coupling is opened anyway.
  That gives one reading per pick-up. There is no nightly trend, but the ram's pressure already gives fill.
- **Each container is different.** One DUO site rotates several containers. A tare lift at docking handles the tare.
  It does not handle L and x_w, which differ per container model. Each container needs an ID (RFID tag) and its own
  geometry. A two-end DUO lift would need a second jack under the container's rear rollers: a ground fixture, which
  is H5 (weighing rails) by another name.
- **Exchange path.** The jack sits where the container is pushed in and pulled out. It must be flush or retracted
  below the rails, and interlocked with the truck.
- **Prior art.** Hydraulic piston scales under the casters of a detachable compactor container are claimed in [31].
  A hydraulic DUO variant is close to it. FTO check first.

Order-of-magnitude installed cost: **€1,970–6,990 factory-fit** (new DUO with the frame), €2,610–9,160 on an
existing site (team estimate, table below). Site work dominates. That is no cheaper than H5, and H5 also solves the
geometry. **For DUO we keep H1 (same part) or H5 (§19.3). The docking-frame jack is not costed into any totals.**

| line (team estimate) | DUO docking jack, factory | DUO docking jack, existing site |
|---|---|---|
| sensors | 80–250 | 80–250 |
| electronics (incl. RFID reader, tags) | 100–350 | 120–400 |
| mechanical | 700–1,800 | 900–2,200 |
| site work (pad or pit at the dock) | 300–1,500 | 500–2,500 |
| labour (6–16 h / 10–24 h) | 330–1,440 | 550–2,160 |
| calibration (per container model) | 110–450 | 110–450 |
| maintenance (6 y) | 300–900 | 300–900 |
| development (NRE) | 50–300 | 50–300 |
| **total** | **1,970–6,990** | **2,610–9,160** |

### 20.6 Installed cost of H7-2 (team estimate)

Same eight lines as H7 (Appendix A, `installed_cost.json`). Lines summed low-with-low, high-with-high. Labour at
€55–90/h [24]. The extra over H7 is the second cylinder set, more labour and a second seal to maintain.

| line | H7 factory | H7-2 factory | basis |
|---|---|---|---|
| sensors | 60–200 | 80–270 | one shared transducer [49] + 2nd position switch + 2-axis tilt sensor |
| electronics | 40–150 | 50–190 | 2nd valve driver and inputs |
| mechanical | 450–950 | 900–1,900 | 2nd cylinder, foot, housing, valve section, front reinforcement |
| site work | 0–150 | 0–250 | pads under two feet |
| labour | 165–540 | 275–810 | 5–9 h on the line |
| calibration | 55–180 | 82–270 | 1.5–3 h; known load at two positions, both ends |
| maintenance (6 y) | 234–638 | 374–1,061 | 0.75 h/yr; two seal kits at 30–60 %; one sensor at 20–40 % |
| development (NRE) | 30–200 | 40–275 | €200–550k over 5,000–2,000 units |
| **total incl. 6 y upkeep** | **1,034–3,008** | **1,801–5,026** | |
| **capex without upkeep** | **800–2,370** | **1,427–3,965** | 7.1–19.8 % of a €20k unit [36] |

- The H7-2 hardware (sensors + electronics + mechanical) is €1,030–2,360. The sheet's OEM figure is €860–1,725 [49]
  with no line items. Ours is higher because of the tilt sensor, front reinforcement and a second valve section.
- The extra hardware over H7 is €480–1,060. That matches the €510–1,150 front-cylinder estimate in §19.5.
- Retrofit is not recommended: €3,354–9,676 (team estimate; both frame ends cut).

### 20.7 Where H7-2 fits

- **Not on every unit.** One-end H7 plus tickets (case B, 4.4 % mid at 2.5 t) is enough for planning. H7-2 costs
  €627–1,595 more capex per unit.
- **On the reference subset.** The pipeline shows that ~5 % of devices with a real scale is enough
  (`virtual_scale.by_reference_share`, §19.8). H7-2 units there give W without a fill model and measure x_w(fill)
  for the whole one-end fleet. They also give a second check on weighbridge tickets.
- **Not at docked sites** (wall chute, bin lifter) until the press-end hazard is cleared; one-end H7 there.
- Billing stays on the certified weighbridge (2014/31/EU). H7-2 is for planning, forecasts and ticket cross-checks.

### 20.8 What we changed or flagged in the sheet [49]

| Sheet claim | Our finding | Where |
|---|---|---|
| Title "Duo" | Two cylinders on a COMBI, not the DUO product; renamed H7-2 | §20, §20.5 |
| W and x from two lifts, no CoG model | Algebra correct; x_w term removed; tare, snow, friction, span and pivot shift remain | §20.2, §20.3 |
| One shared sensor | Fine; 1.0–2.4 % of 2.5 t; needs a load-holding valve per cylinder and two relief settings | §20.3, §20.4 |
| Feet ≥ 30 mm up, 20/30 mm lift check | 60 mm before uneven ground; no stroke given; assume 80–100 mm. Check floor ≈ 1.5–4 % of 2.5 t | §20.2, §20.3 |
| ±5 % in 99.9 % (full) / 95.6 % (half); 1.3 % audit floor | Implies σ 1.5 % / 2.5 %; between our case C low and mid; appendix not seen; not results | §20.3 |
| x shift reveals wet material | Weak; x is better used to learn x_w(fill) | §20.3 |
| €860–1,725 OEM = 4.3–8.6 % of €20k | Arithmetic right; hardware only; installed €1,801–5,026 incl. upkeep (team estimate) | §20.6 |
| ~2 min, press idle | Plausible | §20.4 |
| (not on the sheet) press-end crush and load bypass at wall chutes, front foot in the pick-up path | New hazards; interlocks and a site flag | §20.4 |

### 20.9 To confirm with Europress

ENGINEER_QUESTIONS 16–19 (below). Until they are answered, H7-2 is an idea, not a design. Validation adds to §19.11
stage A: the same water-IBC test with both cylinders, the known load at three positions, and the two-height check
with a shim of known stiffness under one runner end.

---

## Proposed RED_TEAM rows (append under the H7 table)

| # | Failure mode | Hits | What would happen | Response | Status |
|---|---|---|---|---|---|
| R31 | **Name clash.** The team sheet [49] calls the two-end lift "Duo", but it shows a COMBI | H7-2, pitch | Europress hears "a DUO solution" that does not exist | Renamed H7-2; §20.5 states that the DUO product is still open | revised |
| R32 | **Front lift against a fixed chute, hood or bin lifter** at the press end | H7-2 | Crush hazard, damage; the fixed part carries load (load bypass, reads low) | No front lift with the charging door open or the bin lifter running; site flag for docked units, which use one-end H7 only | revised (rule) + open (how many units are docked, Q17) |
| R33 | **Partial runner contact below the two-height check floor** | H7-2 | A contact carrying < ~1.5–4 % of a 2.5 t load passes the 20/30 mm check | Accept the floor; add the lift-curve stiffness check (§19.6) and the nightly trend; shim test in stage A | accepted |
| R34 | **Front rod not retracted at hook-up.** The hook lifts the front first | H7-2 | The foot and housing are dragged; damaged cylinder | R26 measures on both rods: spring return, position switch, pick-up blocked unless both are retracted | revised |
| R35 | **Shared sensor, missing valves.** No load-holding valve per cylinder and no relief valve on the sheet; a leaking isolation valve mixes the two lines | H7-2 | Drop on a hose burst; wrong reading | Load-holding valve per cylinder; front and rear relief settings; leak test with the idle cylinder | revised (design) |
| R36 | **Front frame load** up to 64 kN under the press unit; stroke not given (≥ 60 mm needed before uneven ground) | H7-2 | Frame damage; check cannot run | FEA in NRE; 80–100 mm stroke assumed; Q16 | revised (cost) + open |
| R37 | **Unverifiable accuracy.** The sheet's 99.9 % / 95.6 % come from an appendix we have not seen | H7-2 | Overstated pitch claim | Not cited; our case C budget (§19.5) used instead | revised |
| R38 | **DUO docking-frame jack.** Coupling bypass, a different geometry per container, a jack in the exchange path, prior art [31] | DUO | No reading, or a wrong one; FTO risk | Reading only with the coupling released; container ID; for DUO keep H1 or H5; not costed into totals | accepted, open (Q19) |

Result for H7-2 and DUO: 8 failure modes; 6 led to a revision, 2 (R33, R38) are accepted.

## Proposed ENGINEER_QUESTIONS (append as 16–19)

16. **Front frame (H7-2).** Is there room between the runners about 0.8 m from the front, under the press unit, for
    an 80 mm cylinder housing with an 80–100 mm stroke? Can the frame there take up to ~65 kN with local
    reinforcement? Does the truck's tilting frame or roller pass there during pick-up?
17. **Docked units.** How many COMBIs stand against a wall chute, hood or bin lifter fixed to the building? Would a
    10–30 mm rise of the press end touch it?
18. **Pivots.** When one end of a CombiMax is lifted, where does the other end rest: on the rear rollers or on the
    runner ends? Are the runner fronts curved up, and where does the flat part start?
19. **DUO coupling and containers.** How is a DUO container coupled to the press (latches, hydraulic clamps)? Does
    the coupling carry vertical load? Could it be released for ~2 min before pick-up? How many container models
    rotate through one DUO site?

## Cost lines (JSON snippet, same structure as `installed_cost.json` → `candidates`)

All values are team estimates in EUR, VAT excluded, labour €55–90/h. `H7_2` is the sheet's two-end lift on a COMBI.
`DUO_DOCK` is the speculative DUO-product variant: its "factory_fit" means a new DUO compactor with the frame
fitted, and "retrofit" an existing DUO site.

```json
{
  "H7_2": {
   "name": "Two-end hydraulic self-lift on the compactor's own power pack (H7-2; team sheet [49], titled 'Duo')",
   "hardware_eur": {"low": 1030, "high": 2360},
   "retrofit_eur": {"low": 3354, "high": 9676},
   "factory_fit_eur": {"low": 1801, "high": 5026},
   "lines": [
    {"line": "sensors", "item": "one shared 0–250 bar pressure transducer [49], two rod position switches, oil temperature, 2-axis tilt sensor (roll + pitch)", "retrofit": [80, 270], "factory_fit": [80, 270], "source": "team estimate (no supplier quote; [49] gives no line items)"},
    {"line": "electronics", "item": "two valve coil drivers + inputs on the SMART modem, motion sensor, door / hook / bin-lifter interlock", "retrofit": [60, 240], "factory_fit": [50, 190], "source": "team estimate"},
    {"line": "mechanical", "item": "two 80 mm single-acting cylinders (80–100 mm stroke) with spring return, ball-joint feet, housings, bellows; two valve sections (solenoid, pressure-compensated throttle, load-holding, relief), isolation valves, steel pipe, shear pins; local reinforcement at both frame ends", "retrofit": [1500, 3400], "factory_fit": [900, 1900], "source": "H7 mechanical line × ~2 (team estimate); [49] OEM €860–1,725 for the whole system; retrofit: cut and weld both frame ends"},
    {"line": "site work", "item": "steel or concrete pads under two feet on gravel / hot asphalt sites; retrofit: hook-lift round trip to a workshop", "retrofit": [0, 650], "factory_fit": [0, 250], "source": "team estimate (calc/h7_hydraulic.py ground table)"},
    {"line": "labour", "item": "retrofit 20–36 h; factory 5–9 h on the line", "retrofit": [1100, 3240], "factory_fit": [275, 810], "source": "hours team estimate × rate [24]"},
    {"line": "calibration", "item": "tare lifts at both ends, known load (water IBCs) at two positions to fix a, c, bf, br; firmware set-up", "retrofit": [200, 540], "factory_fit": [82, 270], "source": "team estimate × rate [24]"},
    {"line": "maintenance (6 y)", "item": "bellows, feet and seal check 0.75 h/yr; two cylinders, each 30–60 % chance of a seal kit (€80–300 + 2 h); 20–40 % chance of a new (shared) pressure sensor", "retrofit": [374, 1061], "factory_fit": [374, 1061], "source": "team estimate"},
    {"line": "development (NRE)", "item": "FEA of both frame ends per family, two-cylinder hydraulic circuit, risk assessment and CE file update [48] incl. EN ISO 13849-1 safety functions, firmware, field test: €200–550k", "retrofit": [40, 275], "factory_fit": [40, 275], "source": "team estimate"}
   ]
  },
  "DUO_DOCK": {
   "name": "Hydraulic jack in a DUO compactor's docking frame, lifting the coupled end of the container (speculative; not in any totals)",
   "hardware_eur": {"low": 880, "high": 2400},
   "retrofit_eur": {"low": 2610, "high": 9160},
   "factory_fit_eur": {"low": 1970, "high": 6990},
   "lines": [
    {"line": "sensors", "item": "0–250 bar pressure transducer, rod position switch, oil temperature", "retrofit": [80, 250], "factory_fit": [80, 250], "source": "team estimate"},
    {"line": "electronics", "item": "valve driver + inputs on the SMART modem, RFID reader and a tag per container, coupling-released and truck interlocks", "retrofit": [120, 400], "factory_fit": [100, 350], "source": "team estimate"},
    {"line": "mechanical", "item": "80–100 mm cylinder (container 2–3 t + up to 8 t waste, 8–65 kN), foot, frame in the docking base flush with the rails, valve section with load-holding and relief valves, guards", "retrofit": [900, 2200], "factory_fit": [700, 1800], "source": "team estimate; forces from calc/loads.py DUO values"},
    {"line": "site work", "item": "pad or shallow pit at the dock, rail adaptation", "retrofit": [500, 2500], "factory_fit": [300, 1500], "source": "team estimate"},
    {"line": "labour", "item": "retrofit 10–24 h on site; factory 6–16 h", "retrofit": [550, 2160], "factory_fit": [330, 1440], "source": "hours team estimate × rate [24]"},
    {"line": "calibration", "item": "geometry per container model, tare per container", "retrofit": [110, 450], "factory_fit": [110, 450], "source": "team estimate × rate [24]"},
    {"line": "maintenance (6 y)", "item": "seal and foot check, pit cleaning, replacement tags", "retrofit": [300, 900], "factory_fit": [300, 900], "source": "team estimate"},
    {"line": "development (NRE)", "item": "docking-frame design, risk assessment and CE file [48], FTO check against [31], firmware", "retrofit": [50, 300], "factory_fit": [50, 300], "source": "team estimate"}
   ]
  }
}
```
