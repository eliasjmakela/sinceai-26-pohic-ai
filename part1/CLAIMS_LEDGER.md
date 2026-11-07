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
