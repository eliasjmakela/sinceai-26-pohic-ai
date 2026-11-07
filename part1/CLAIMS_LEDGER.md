# Claims ledger (weighing v2)

Every numeric technical claim in `WEIGHING_CONCEPT.md` (D1), where it comes from, how sure we are, and how an
engineer would check it. Confidence: **high** = published datasheet / own data query; **medium** = listing, vendor
claim or straightforward physics; **low** = team estimate or guess. "calc/…" and "scripts/…" are reproducible with
`part1/scripts/reproduce.sh`. [n] = reference list of D1.

## Europress and machine facts

| # | Claim in D1 | Value | Source | Confidence | How to check |
|---|---|---|---|---|---|
| C1 | Basic COMBI price | €20–25k | Tommi [36] (Whisper, noisy) | medium | ask Tommi |
| C2 | Reference weighing option price | ~€2,000 | Tommi [36]; transcript wording is ambiguous ("20 parampia hinnasta" may be "2000 euroa" or "20 % of the price"; later "säästää 2000") | medium | ask Tommi |
| C3 | Platform scales "almost as expensive" | – | Tommi [36] | medium (what they are compared with is unclear) | ENGINEER_QUESTIONS Q9 |
| C4 | COMBI machine mass | ~3 t (Tommi); 4.0–4.4 t | [36]; listings [18] | medium | Europress datasheet |
| C5 | Waste in a full unit | up to ~5 t | [36] | medium | dataset tickets reach 7.7 t p90 for DUO mixed waste (`calc/loads.py` uses 8 t for DUO) |
| C6 | COMBI infeed 1,500 × 900 mm, height 1,480 mm, 25 t, 42 s cycle | – | listing [17] | medium | Europress datasheet |
| C7 | Hopper-stage weighing idea | – | Tommi [36] | high (attribution) | – |
| C8 | Guide rails sold as an accessory | – | v2 brief (team knowledge) | low (not found online) | ask Europress |
| C9 | Chamber floor 0.4–0.6 m above ground; drop 0.9–1.1 m | – | team estimate | low | Q2 |
| C10 | DUO container empty mass 2–3 t | – | team estimate | low | Europress datasheet |
| C11 | Ram face area 1.5 × 0.8 m | 1.2 m² | aperture width [17] × chamber height team estimate | low | drawing |

## Charges and data (synthetic)

| # | Claim | Value | Source | Confidence | Check |
|---|---|---|---|---|---|
| C12 | Median charge mass per material | 8–30 kg | kit `input_event_kg` [2] | medium (simulation assumption) | bench stage B |
| C13 | Charges per container (median) | 78 | `scripts/charge_sum.py` (compaction cycles between lifts) | high for synthetic data | – |
| C14 | kg per cycle p10 / p50 / p90 | 10.1 / 22.9 / 33.3 | `generated/charge_sum.json` | high (synthetic) | – |
| C15 | Reference lifts / devices for H2 | 5,627 / 368 | `generated/self_calibration.json` | high (synthetic) | rerun |
| C16 | Devices whose operator never shares tickets | 78 | `scripts/self_calibration.py` query | high (synthetic) | rerun |
| C17 | Reference loads for accuracy→value | 5,787 (641 in 2.5–3.5 t) | `scripts/accuracy_value.py` | high (synthetic) | rerun |

## Loads and sizing (`calc/loads.py`)

| # | Claim | Value | Source | Confidence | Check |
|---|---|---|---|---|---|
| C18 | Plate cells 4 × 500 kg, C3 0.017 % | 2 t range | [22] | high (datasheet) | – |
| C19 | Thrown cardboard charge peak | 0.75–0.89 t (42–50× static) | energy balance, stop distance 50 mm (team estimate) | low–medium | drop test, bench stage A |
| C20 | Biowaste bag peak | 2.1–2.5 t | same, 30 mm | low–medium | drop test |
| C21 | Misuse peak (25 kg, 5 mm) | 10–12 t | same | low–medium | drop test |
| C22 | Floor load on the plate during a stroke | 7–14 t | 25 t [17] / 1.2 m² × K 0.3–0.6 (team estimate) × 1.12 m² | low | pressure film test, Q3 |
| C23 | Stop gap | 0.24–0.48 mm | 120 % of 0.2–0.4 mm rated deflection [19] | medium | cell datasheet of the chosen cell |
| C24 | Cell safe / ultimate load | 200 % / 300 % | Flintec SSB5 [20] | high | datasheet |
| C25 | COMBI full on rails | 8.0–9.5 t | C4 + C5 | medium | – |
| C26 | Rear cell at full COMBI pick-up | 5.7 t | 80 % on rear pair × 1.5 dynamic (team estimate) | low | strain test during pick-up |
| C27 | Set-down peak per front cell | 1.7–9.9 t | √(2E k), v 0.05–0.2 m/s, rail stiffness (team estimates) | low | instrumented set-down, Q8 |
| C28 | Horizontal pull force | 3.8–7.6 t | μ 0.4–0.8 dry steel [21] × 9.5 t | medium (μ), low (skids vs rollers) | Q8 |
| C61 | On H5 a 1 t load is 18–25 % of a COMBI reading; a 9–30 kg charge is 0.4–1.5 % of the H1 plate range | – | `calc/loads.py` from C4, C18 | medium | – |
| C29 | Plate inertia in transport | 100–150 kg × a few g | team estimate | low | – |

## Temperature (`calc/temperature.py`)

| # | Claim | Value | Source | Confidence | Check |
|---|---|---|---|---|---|
| C30 | TC zero / span | 0.04 % / 0.02 % per 10 °C | SSB5 [20] | high (that cell); medium for others | chosen cell's datasheet |
| C31 | H1 temperature error per charge | 0.02–0.04 kg | C30, ΔT 0.5 °C in 1 min (team estimate) | medium | climate chamber |
| C32 | H5 temperature error | 0.3–0.7 % of 3 t (5 t cells); doubles with 10 t cells | C30, ΔT 25 °C (team estimate) | medium | climate chamber |
| C33 | Compensated range | −10…+40 °C | [20] | high | – |

## H1 error model and results

| # | Claim | Value | Source | Confidence | Check |
|---|---|---|---|---|---|
| C34 | Bridging share per material | 1 % (bio) – 6 % (cardboard) | team estimate (`calc/h1_params.py`) | **low** (largest unknown) | bench stage B, Q5 |
| C35 | Container-to-container spread | 2 / 3 / 5 % | team estimate | low | pilot stage C |
| C36 | Reading noise | 0.3 / 0.5 / 1.0 kg | team estimate from C18 + vibration | low–medium | bench |
| C37 | Missing reading pairs | 0.5 / 1 / 3 % | team estimate | low | firmware log in pilot |
| C38 | Gain drift | 0.3 / 0.5 / 1 % per month | team estimate | low | pilot drift watch |
| C39 | Random part of container error | ≈1–4.5 % | `calc/error_accumulation.py` | medium (given C12, C36) | – |
| C40 | RMS error before calibration | 6.3 / 8.2 / 13.3 % (charge_sum) and 6.8 / 9.5 / 13.8 % (self_calibration, with drift) | scripts | estimate (model output) | pilot |
| C41 | Floor after ideal calibration | 2.1 / 2.9 / 4.9 % | `scripts/charge_sum.py` | estimate | pilot |
| C42 | H2: n = 0 with fleet prior | 3.0 / 4.6 / 6.6 % | `scripts/self_calibration.py` | estimate | pilot held-out devices |
| C43 | H2: after ≥ 10 tickets | 2.3 / 3.4 / 5.4 % | same | estimate | pilot |
| C44 | Fusion with T0 | 3.38 % → 3.25 % | `scripts/fusion.py` | estimate (synthetic) | pilot |
| C45 | T0 median abs error (synthetic) | 5.8 %, p90 20 % | `scripts/fusion.py` | high for synthetic, unknown for real | real pressure data (TOMMI Q8) |
| C46 | Jam alarm delay | 12–78 h by material | cycles per day, `scripts/fusion.py` | high (synthetic cycle rates) | – |

## Other tiers

| # | Claim | Value | Source | Confidence | Check |
|---|---|---|---|---|---|
| C47 | H5 installed σ | 0.6 / 1.0 / 2.0 % | team estimate; vendor ≤ 1 % for truck systems [12][13] | low–medium | pilot |
| C48 | PS σ | 0.2 / 0.5 / 1.0 % | team estimate (C3 cells [8], platform mechanics) | medium | vendor |
| C49 | T1 σ revised | 1.2 / 2.8 / 5.3 % | `scripts/tiers.py` budget incl. support position (RED_TEAM R9) | low | bench + pilot |
| C50 | T0 σ | 5 / 10 / 20 % | v1 team estimate; consistent with C45 | low | real pressure data |

## Costs (`calc/installed_cost.py`; every line also carries its source there)

| # | Claim | Value | Source | Confidence | Check |
|---|---|---|---|---|---|
| C51 | 500 kg C3 cell | €220 list; ~€12 low-end listing | [22]; [25] | medium | supplier quote at volume |
| C52 | 5 t shear-beam cell | €225–435 | [26] ($262.50), [8] (€435) | medium | quote |
| C53 | Junction box / transmitter | €130 / €52–330 | [9] / [10][11] | medium | quote |
| C54 | Weigh module with lift-off protection | $1,225 per 5 t module | [23] | medium | quote |
| C55 | Container scale (beams + ramps, 15 t) | €4,800–5,620 | [27] | medium | quote |
| C56 | Technician rate | €55–90/h | [24] €55 + team estimate; [37] €152 expert upper bound | medium | Europress service price |
| C57 | H1 mechanical, retrofit / factory | €400–1,000 / €150–400 | team estimate | low | Europress workshop |
| C58 | H5 site work, retrofit / new | €800–2,500 / €300–1,000 | team estimate | low | ground-works quote |
| C59 | Development amortised | €50–400k over 2,000–5,000 units | team estimate | low | Europress R&D |
| C60 | Totals (H1 factory €548–2,363, retrofit €1,270–4,923; H5 €2,382–7,056 / €3,412–10,136; PS €7,860–22,160 / €8,580–23,880; T1 €226–1,179 / €419–1,674; T2 €1,635–4,338 / €1,960–5,438; T0 €10–125 / €10–215) | – | sum of lines | as weak as their weakest line | – |

Sampling check (WG1): ten numbers drawn from D1 (§0 €548–2,363; §0 9.5 % → 4.6 %; §3.1 0.24–0.48 mm; §3.2 12–78 h;
§5.3 7–14 t; §6 18–25 %; §6 0.3–0.7 %; §6 €4,800–5,620; §8.1 1–4.5 %; §9 3.38 → 3.25 %) are C60, C40/C42, C23,
C46, C22, C61, C32, C55, C39, C44.

## H7 hydraulic self-lift (team idea, §19; `calc/h7_hydraulic.py`, `calc/installed_cost.py`)

| # | Claim in D1 | Value | Source | Confidence | How to check |
|---|---|---|---|---|---|
| C62 | Cylinder 0.5–1 m from the door end, 10 mm lift, 50 mm stroke, foot 30 mm above runner bottom, 300 × 300 mm foot, 15 s lift and 15 s lower | – | team document [39] | low ([39] itself calls the dimensions assumptions) | Europress drawings, Q11 |
| C63 | Pivot-to-cylinder distance L | 5.0–6.0 m | team estimate (unit 6–7 m long) | low | drawing |
| C64 | Door-end share of the machine mass | 0.30–0.45 | 1 − press-end share 0.55–0.70 in `calc/loads.py` (team estimate); press assumed at the hook end | low | Europress datasheet, Q14 |
| C65 | Waste centre of mass x_w / L | 0.45–0.75 | team estimate | **low** (largest unknown) | §19.11 stages A/B, Q14 |
| C66 | System pressure | ~200 bar | Tommi [36], as quoted in the review | medium | Q12 |
| C67 | Cylinder force, empty / full (5 t) | 9–20 kN / 31–57 kN | C4, C5, C63–C65, statics | medium (physics), low (inputs) | load cell under the foot, stage A |
| C68 | Pressure, 80 mm bore, empty / full; 63 mm bore, full | 18–40 / 61–113 bar; 99–182 bar | C67 / piston area | medium | – |
| C69 | Worked example: R0 27 bar, R 57 bar; 1 bar ≈ 85 kg of waste (80 mm, x_w/L 0.6) | – | `calc/h7_hydraulic.py` statics | medium | – |
| C70 | Oil per lift, flow, speed, work | 50 cm³, 0.20 L/min, 0.67 mm/s, 0.6 kJ | area × 10 mm over 15 s; force × 10 mm | high (arithmetic) | – |
| C71 | Stroke margin left | 10 mm | 50 − 30 − 10 mm [39] | medium | – |
| C72 | Foot pressure in the heaviest case; allowable bearing (concrete 3, cold asphalt 1, hot asphalt 0.4, gravel 0.3, soft 0.1 MPa); pad sizes 376–753 mm | 0.63 MPa | C67 / 0.09 m²; bearing values team estimate (order of magnitude) | low (bearing values) | geotechnical table, plate-load test |
| C73 | Seal + guide friction of an 80 mm cylinder | 0.3 / 0.7 / 1.5 kN = 3–17 % of the lightest tare force, 0.5–2.6 % of the heaviest force | team estimate | low | stage A friction log (half the up–down difference) |
| C74 | Share of friction not cancelled by up/down averaging | 10 / 20 / 30 % | team estimate; principle in [43][44] | low | stage A |
| C75 | Pressure-sensor repeatability after auto-zero | 0.10 / 0.15 / 0.25 % of 250 bar | team estimate (industrial transducer class; no datasheet fetched) | low–medium | datasheet of the chosen sensor |
| C76 | Span drift between tare and reading | 0.1 / 0.25 / 0.5 % of R | team estimate | low | climate chamber |
| C77 | Pivot shift 0.5 / 2 / 5 cm → up to ≈2 % at 5 cm | – | `calc/h7_hydraulic.py` (exact statics including the machine term); the review had 0.8 % without it | medium (physics), low (shift sizes) | survey before and after |
| C78 | Tare change (rain, ice, residue) 25 / 50 / 150 kg; heavy roof snow ≈0.7–1.4 t (14 m² × 0.5–1 kN/m²) | – | team estimate | low | nightly trend, stage B |
| C79 | Centre-of-mass error: fixed value 5 / 10 / 20 %; fill model after tickets 2 / 3 / 5 %; two-end geometry residual 0.3 / 0.5 / 1 % | – | team estimate (the calibrated value equals H1's container floor, C35) | **low** | stage B |
| C80 | Gain and geometry error: before tickets 1 / 2 / 3 %; after H2 0.3 / 0.5 / 1 % | – | team estimate | low | stage A |
| C81 | H7 1σ at 2.5 t: A 5.3 / 10.7 / 21.9 %, B 2.6 / 4.4 / 9.7 %, C 1.7 / 3.2 / 8.4 %; at 5 t: B 2.2 / 3.5 / 6.8 %, C 0.9 / 1.9 / 4.8 % | – | RSS of C73–C80, `generated/h7_budget.md` | estimate (model output) | stage B |
| C82 | H7 absolute floor | 40 / 80 / 200 kg | sensor + friction + tare change, `calc/h7_hydraulic.py` | estimate | – |
| C83 | Accuracy target | 1σ ≤ 5 % (one end) or ≤ 3 % (both ends) after 10 tickets, loads ≥ 2.5 t | team target, untested | – | stage B pass criterion |
| C84 | Virtual scale (pipeline) | median error 8.3 % uncalibrated, 7.6 % after 5 tickets, 5.5 % monthly; reference shares above ~5 % add little | `web/public/data/bundle.json → virtual_scale` (synthetic, optimistic) | high for the simulation, unknown for real | rerun the pipeline |
| C85 | Median-abs → 1σ factor; H7 fused with the virtual scale | 1 / 0.6745 (7.6 % → 11.3 %); 2.5 / 4.1 / 7.4 % | normal distribution; inverse variance, assumes independence (optimistic) | medium | – |
| C86 | Lifts per year per unit | ≈445 (365 nightly + 2 × ~40 pick-ups) | review row 4 (`bundle.json`: 18,042 lifts / 447 devices) | medium | SMART logs |
| C87 | H7 installed cost: factory-fit €1,034–3,008, retrofit €1,994–6,168; hardware €550–1,300 | – | `calc/installed_cost.py`, every line a team estimate; parts anchored on [39] €550–1,100 (retail −50 %) | low | OEM quotes for cylinder, valve and sensor (Q12) |
| C88 | Front cylinder for a two-end lift (not in the H7 totals) | €510–1,150 | the H7 sensor + mechanical lines again (team estimate) | low | quote |
| C89 | H7 accuracy → value at mid (4.4 %, 80 kg): 57 % of 2.5–3.5 t loads within ±100 kg, 41 % of +10 % differences flagged, 9 loads to see 3 % | – | `scripts/accuracy_value.py` with the H7 tier | estimate | rerun |
| C90 | Machinery Regulation (EU) 2023/1230 applies from 20 Jan 2027 | – | [48] | high | – |

Sampling check for H7: §0 €1,034–3,008 (C87); §0 ≤ 5 % (C83); §19.2 113 bar (C68); §19.2 85 kg per bar (C69);
§19.2 0.20 L/min (C70); §19.5 ≈2 % pivot (C77); §19.8 4.1 % fused (C85); §19.6 0.63 MPa (C72); §19.6 ≈445 lifts
(C86); §19.5 €510–1,150 (C88).
