# PRODUCT.md — FullLoad

> North star for everyone (humans and coding agents) working in this repo. **The only goal is an impressive,
> credible end-to-end demo that wins the Europress challenge at Since AI Hackathon 2026.** Not production
> reliability, not benchmark scores. If a task does not make the demo storyline in §4 better, safer or more
> believable, do not do it. When this file and your instinct disagree, this file wins; change it deliberately.
>
> Hard deadline **Sun 8 Nov 2026 10:00**; we submit by **09:30**. One person codes (with agents); two teammates
> own validation, the weighing-concept document, the business case and the pitch.

## 1. Thesis

**FullLoad — pay for tonnes, not trips.**

**The core value is a new business model that makes the market switch from per-trip to per-kg billing.**
Per-kg billing is objectively more efficient: containers are emptied when full, trucks carry more per visit, and
the customer pays for material handled instead of kilometres driven. Today that switch does not happen, for two
reasons we can show with data:

1. **Nobody but the operator knows the weight.** In the synthetic data, per-trip charges (lift fee, transport, fuel,
   emergency, remote, wasted trip) are about **€3.6 M of €6.3 M** gross charges, and about **1 in 3 completed lifts
   empties a container that is under 60 % full** (median fill at lift: fixed schedule 52 %, max-interval rule 44 %,
   customer request 39 %, automatic on-call 82 %).
2. **Per-kg pricing is risky for operators, and only the incumbent can take that risk.** To bid per kg, an operator
   must know how much a site produces. The established operator has years of collection history; a newcomer does
   not. In the data, forecasting a device's next three months of tonnage from **its own history** has a median
   error of about **10 %**; forecasting it from **peers** (same material and container size, which is all a
   newcomer has) is about **38 %** off. The newcomer must add a risk premium and loses. The information advantage
   becomes a **local monopoly**, and the monopoly has no reason to drive less.

**FullLoad breaks this.** The compactor weighs its own load, and the collection data lives with Europress, not with
one operator. Europress sells **weight-based forecasts and verified weights to every operator** on equal terms. Any
operator can now price per kg with the same precision as the incumbent, so customers can tender on per-kg terms
and efficient operators, including new entrants, can win.

### Who pays, who uses (decided)
- **Operators pay**: a **service fee per verified tonne**, as a SMART add-on. They get site forecasts, weight-triggered
  lift orders and a verified weight to check every bill against. It is what lets them offer per-kg prices without risk.
- **The weighing hardware is free for customers**, funded (or subsidised) by Europress and paid back from the operators'
  per-tonne fees. Working assumption: **cheap strain gauges** (tier T1, §7.5). The business case must show this payback.
- **Customers use it for free**: they see how full their containers are when emptied, what per-kg billing would
  simulate to for them, and they get the prompt to tender on per-kg terms. **The customer decides to tender.**
- **Europress stays a technology company**: it never drives trucks, contracts transport or takes a transport margin.
- **The weight is shared and trusted**: the same verified weight is visible to customer and operator; it is not a tool
  for one side to police the other. It is used for **forecasts, weight-triggered lifts and checking the per-kg bill**.
  The **billing (settlement) weight stays the operator's certified weighbridge** by default: using a device weight as a
  billing basis in the EU needs an approved non-automatic weighing instrument (Directive 2014/31/EU), which cheap
  strain gauges are not designed to be. Device-weight settlement is an option only where both parties agree to it in
  their contract, or as a later certified product. Never claim the device weight is legal for trade.

Pitch line: *"Today the weight — and the knowledge of every site — belongs to the incumbent. FullLoad puts it in the
compactor, so every operator can compete per kilo."*

### Where we put our effort
- **The business model and the market before/after is our differentiator** and gets most of the effort. It came from
  domain knowledge in our team and lines up with what Europress said at kickoff.
- **Part 1 (weighing) is "complete and decent", not deep.** It is 25 % of the score and a required deliverable, so every
  element the brief lists must be present (principle, placement, BOM/cost, installation, calibration, error sources,
  validation plan). Agents draft it; a teammate reviews it. In the demo: one short beat plus the accuracy slider.
  Tommi called the value part "maybe the beef in the whole system". Coder time on Part 1: at most about 10 %.

## 2. What Europress told us at kickoff (Tommi Häkkinen, 6 Nov) — design constraints

Source: kickoff recording transcript (`Röst 261106_182238.txt` in the project root, Whisper, imperfect).

| What was said | What it means for us |
|---|---|
| "We are **not** going into transportation operating … we are a technology company." | Europress never owns trucks or becomes the hauler. Fee per verified tonne is a service fee paid by operators. |
| The biggest operator owns trucks and "the more transportation they get the more money"; other operators use subcontractors and benefit from transporting as little as possible. A direct integration with a "good operator" was very hard. | The market is split by incentive: one dominant player profits from trips, others from efficiency. Our natural first customers are the efficiency-driven operators. Do not depend on operator data feeds. |
| Some operators already resell SMART Insights to retail chains to win contracts. Partnerships are strategy. | Selling to operators is already proven. Operator-paid model fits. |
| Weighing: "cheap as possible, it doesn't need to be all accurate … ballpark but really close." Customers "are not willing to pay almost anything" for extra hardware. | Part 1 leads with the cheapest viable option. Customer side must be free. |
| The hydraulic **pressure sensor** is "the fingerprint" of the compactor (up to ~200 bar, ram position over time); fill from back-pressure to ~5 %. Biowaste gives little back-pressure; humidity changes cardboard weight. Pressure examples were offered via Discord. | Part 1 tier T0 = virtual weight from existing pressure + fill. Biowaste and wet cardboard are named limitations. |
| ~60–70 % of machines auto-order at ~80 % fill; ~30 % in Finland on fixed schedules; Central Europe/Poland much less automated. | Growth market for per-kg models; fixed schedules are where the waste is. |
| SMART Insights is in only ~**15 %** of the installed base; digital services are the most profitable; small customers are hard to sell to. | Free customer side solves the small-customer sales problem; operators pay. |
| Transport is usually a **fixed price per lift**, agreed between operator and customer; treatment fees are much higher. | Confirms the per-trip pricing the model attacks. |
| "I'm interested in how you managed to utilise AI capabilities … e.g. better end-customer experience." | One bounded AI feature for the customer (§7.6) and one pitch slide on how we built with AI agents. |

## 3. The market before/after simulation (the centrepiece)

A **stylised, deterministic** simulation of one region, built from the real (synthetic) sites. It shows how the
actors behave under each regime. Simple enough to explain on one screen, grounded in data where possible, and
explicit about every assumption.

**Actors**
- **Customers**: real sites/devices in one region (tonnage, material, container size and lifts from the data).
- **Incumbent operator**: has the collection history → forecast error σ_inc ≈ 10 % (measured).
- **Entrant operators (1–3)**: no history → σ_ent ≈ 38 % before (measured peer-based error); ≈ 10 % after (FullLoad forecast).
- **Europress**: provides weights and forecasts after; fee per verified tonne.

**Regimes**
| | Before: per trip, private data | After: per kg, FullLoad data |
|---|---|---|
| When lifts happen | actual lifts from the data (schedules, max interval, customer orders) | weight-triggered: lift when the container reaches its typical full payload (device-specific, from its own full on-call lifts), max-interval rule kept |
| How operators bid | per lift; entrants add a risk premium ∝ σ_ent on unknown volume | per kg; everyone bids with the same σ, premium shrinks |
| Who wins | lowest risk-adjusted price, usually the incumbent | lowest cost operator, entrants included |

**Outputs shown before ↔ after**: trips per year, tonnes per trip, customer €/t, operator revenue and margin per
trip, incumbent market share / concentration (HHI), entrants' win count, Europress fee revenue. Sliders: entrant
cost advantage, number of entrants, sensor/forecast σ (connects to Part 1).

**Grounding rules**
- Tonnage is conserved between regimes (same waste, different number of trips).
- Forecast errors (10 % vs 38 %) come from the pipeline's own backtest, not from us; recompute and show the method.
- Operator cost per trip/per tonne, margin and risk-premium factor are **hypothetical parameters** in
  `pipeline/params.yaml`, tagged as such, with a sensitivity view. Prices before come from actual contract versions.
- The simulation is single-round (one tender). A multi-round version (incumbent share eroding over years) is a nice-to-have.

**Scope verdict**: feasible in about 6–8 coder hours if kept closed-form (no agent learning, no routing, one region,
one tender round). The bidding maths is simple enough to run in the browser for the sliders; the data-derived
inputs are precomputed.

## 4. Demo storyline (target 4:30, hard max 5:00)

One screen state per beat; the presenter never types. Every screen has a deep link (`/#/beat-2`).

| # | Time | Beat | On screen | Line |
|---|---|---|---|---|
| 0 | 0:00–0:30 | **Paid per trip** | Fleet strip: 447 devices, ~37,600 t/year, "€3.6 M of €6.3 M is paid per trip", fill-at-lift histogram (1 in 3 under 60 %) | "Customers pay for trips. Only the operator knows the tonnes." |
| 1 | 0:30–1:00 | **Weight at the source (Part 1, short)** | Chosen concept: **T1 cheap strain gauges**, free for the customer (Europress-funded). Alternatives beside it: T0 virtual weight (existing pressure + fill, €0 BOM), T2 load cells. Placement, BOM, calibration, σ. Accuracy slider. | "Ballpark but close is enough, and cheap enough that Europress can give it away." |
| 2 | 1:00–1:35 | **Customer view (free)** | Hero customer: a year of lifts coloured by fill at lift; per-trip cost today vs simulated per-kg cost (± band) | Proposal: "Tender your collection on per-kg terms" → customer **Approves** → tender brief | "The customer decides. FullLoad gives them the evidence." |
| 3 | 1:35–2:05 | **Operator view (paid)** | The same site through an operator's eyes: forecast tonnage with Europress data (±10 %) vs without (±38 %) → the per-kg price an operator can safely bid | "Without the data only the incumbent can bid per kilo. With FullLoad, anyone can." |
| 4 | 2:05–3:20 | **WOW: the market, before ↔ after** | One region. Toggle *Per trip, private data ↔ Per kg, FullLoad*: trips fall, tonnes per trip rise, customer €/t falls, entrants win tenders, concentration drops, Europress fee revenue appears. Drag sliders (entrant cost, σ) to show the effect holds. | "Same waste, fewer trucks, more competition. Europress doesn't drive a single truck." |
| 5 | 3:20–3:50 | **A weight both sides trust** | One lift: device weight vs weighbridge vs invoice with ± σ, "weights agree within ± σ → bill confirmed"; a second case where **our own sensor drifted** → recalibration proposal | "Per-kg billing needs a weight both sides can check. Sometimes the error is ours." |
| 6 | 3:50–4:30 | **The business** | Operators pay per verified tonne; customers free, sensors included; sliders for fee and operator adoption; Europress ARR minus the sensor subsidy, payback per device, sensitivity; SMART integration diagram + API payload. All tagged *hypothetical*. | "Weigh at source. Pay per kilo. Let every operator compete." |

**The wow is beat 4.** Build the simulation first, polish it most.

## 5. Where the points come from

| Criterion (weight) | What earns it | Beats | Deliverable |
|---|---|---|---|
| Weighing concept (25 %) | Three tiers incl. zero-BOM virtual weight; placement COMBI/DUO; BOM ranges; installation; calibration (factory, reference weights, cross-check with shared weighbridge tickets, auto-zero after each lift); error sources (temperature, humidity, off-centre load, press cycle, biowaste); validation plan; slider linking σ to value | 1, 4, 5 | D1 illustrated concept (agent-drafted, teammate-reviewed) |
| Customer/business value (25 %) | Customer per-kg cost vs per-trip; fewer trips; competition; operators' risk removed | 2–4 | D3 |
| Data-driven value & traceable calcs (20 %) | Measured forecast asymmetry (10 % vs 38 %); market simulation with stated parameters; re-pricing with the starter kit's economics; receipts on every €; **rules vs ML comparison** (brief §04): e.g. our premature-lift rule vs kit baseline B4, and simple history forecast vs a slightly richer model | 2–5 | D2 + methods page |
| Software workflow & SMART pathway (15 %) | Flow: weight → forecast → customer proposal → approval → tender brief → operator bid → per-kg bill checked against device weight; integration diagram (SMART telemetry in, forecasts and lift orders out to operators) extending `examples/recommendation_api_mock.py` | 2–6 | D2 + setup notes |
| Commercial productisation (10 %) | Operator-paid fee per verified tonne, free customer side, adoption path (efficiency-driven operators first), sensitivity, roadmap | 6 | D3 |
| Clarity / uncertainty / limits (5 %) | ± on every figure, evidence tags, synthetic banner, "what this does not prove", simulation assumptions on screen | all | all + licence list |

Required submission items (brief §07): (1) illustrated weighing concept; (2) working demo **and** a recorded
walkthrough, code/setup notes, traceable economics, SMART integration; (3) customer value and business case.
Plus `THIRD_PARTY.md` (every library, model, dataset, service + licence) and `LIMITATIONS.md` (assumptions, untested).

Starter-kit tasks covered: **A** re-pricing; **B** premature lifts (without flagging justified ones); **B2** operator
efficiency figures inside the simulation; **C** context only (thresholds/schedules are SMART's domain; we sell the
commercial model on top); **C2** tender proposal with human approval; **D** operator-paid per-tonne fee with our own
price and adoption reasoning (`baselines/business_case.py --params`); **E** receipts, ± and evidence tags.

## 6. Scope (1 coder × ~1.5 days)

### Must-have, in build order
1. **Pipeline skeleton** → one deterministic `web/public/data/bundle.json`.
2. **Forecast backtest**: per device, monthly tonnage; own-history forecast vs peer forecast; error distribution. Simple
   (trailing mean, maybe + seasonal factor from peers); no ML needed for the must-have.
3. **Trips model**: per device, typical full payload from its own full on-call lifts; trips needed under weight
   trigger = tonnage / payload, bounded by the max-interval rule; compare with actual lifts.
4. **Market simulation** (§3) for one region, precomputed inputs + browser-side bidding maths.
5. **Hero selection** (`pipeline/pick_heroes.py`): hero customer on a per-lift/hybrid contract with low fill at lift; one
   weighbridge-agreement case; one drift case; hero region with an incumbent and ≥1 other operator. IDs committed.
6. **Screens**: beat 4 first, then 2, 3, 0, 6, 1, 5.
7. **Proposal card + Approve** → tender brief JSON, in-memory audit log, "Reset demo".
8. **Trust layer**: synthetic banner, evidence tag + receipt drawer on every €, ± on every figure.
9. **Recorded walkthrough video** by Sun 00:00.

### Nice-to-have (only after the freeze checklist is green, in this order)
1. Multi-round market simulation (3 yearly tenders: incumbent share erodes, prices settle).
2. AI customer brief (§7.6).
3. Validation panel: premature-lift rule vs `labels_dev` and vs B4.
4. ESG / recycling-by-weight panel for the hero customer.
5. Daily replay of weight-triggered lifts (instead of the payload approximation), with overflow-risk days.

### Explicitly OUT
Route optimisation and truck load planning (roadmap line in the pitch only), auth, databases, a runtime backend,
live operator/SMART integration, an LLM chatbot, ML leaderboard chasing, a generic Tasks A–E dashboard, a better
threshold algorithm sold *as such*, contamination detection, agent-based learning simulations, mobile layout, i18n,
Docker, anything in `private_evaluation/`.

### Time plan
| When | Coder (+ agents) | Teammates |
|---|---|---|
| Fri 22:00–01:30 | Fresh `.venv` (the existing `venv/` is the whisper env — leave it), starter kit editable, scaffold, pipeline skeleton, forecast backtest, trips model; background agent drafts D1 | Review `TOMMI_QUESTIONS.md`; review D1 draft |
| Sat 08:00–13:00 | Market simulation + beat 4 screen (**wow first**), hero selection | Ask Tommi + Since AI; set hypothetical cost parameters with rationale; hand-check one site's numbers |
| Sat 13:00–18:00 | Beats 2, 3, 0, 6; proposal/approve; receipts | D3 business case with our numbers; pitch skeleton; D1 final |
| Sat 18:00–22:00 | Beats 1, 5; polish beat 4; deploy static build; nice-to-have 1 if green | Rehearse on the live build, report bugs |
| **Sat 22:00 FEATURE FREEZE** | Fixes and copy only | Dry run #1, timed |
| Sat 22:00–24:00 | Dry-run fixes; record walkthrough | Dry runs #2–3; slides final |
| **Sun 00:00 DEMO FROZEN** | git tag `demo-frozen`; bundle and build committed | |
| Sun 07:00–09:30 | Typos, setup notes, `THIRD_PARTY.md`, `LIMITATIONS.md`; **submit by 09:30** | Final rehearsal; upload |

## 7. Architecture

### 7.1 Stack
**Python precompute → static JSON → React single-page app. No server and no network at demo time.**
- `pipeline/` — Python (3.14 is what this machine has; the kit needs ≥ 3.11), pandas + DuckDB + pyarrow, on top of the
  starter kit (§7.2). Our euros are *the dataset's own euros*.
- `web/` — Vite + React + TypeScript + Tailwind + Recharts. Reads `web/public/data/*.json`; runs from
  `npm run preview` with Wi-Fi off and from a static host.
- Rejected: Streamlit (generic look, poor control over a staged story), notebooks (not a product).

### 7.2 How our code fits the starter kit

The kit (`resources/Europress_SMART_Material_Value_Engine_v1.0.1/`) is three different things, and each one is used
differently:

| Kit part | What it is | How we use it |
|---|---|---|
| `src/europress_data/` | An installable package (src layout, `pyproject.toml`): `sdk.open_dataset` (DuckDB views, `as_of`, `telemetry_dedup`), `economics.price_event` / `summarize` (contract pricing in integer cents), `evaluate.score_*` (scorers on `labels_dev`); plus the generator and validator | **Import it.** `pip install -e resources/Europress_…_v1.0.1` into our `.venv`. All data access goes through `open_dataset`, all money through `economics`. Never copy or reimplement these. The generator, validator and simulator modules are not used. |
| `baselines/*.py` | Scripts, not a package; they put `src/` and `baselines/` on `sys.path` themselves. Useful functions: `b1_economic_calculator.compute` (expected charges per lift + mass basis), `b2_rules_anomaly` (premature-lift and invoice rules), `b4_ml_models` (the ML side of the rules-vs-ML comparison), `b5_operator_scorecard.scorecard` | **Import through one adapter**, `pipeline/fullload/kit.py`, which is the only file that touches `sys.path` or kit internals. Everything else imports from `fullload.kit`. If a kit function doesn't fit, wrap it there; don't edit the kit. |
| `baselines/business_case.py` + `configs/` | A customer-value calculator whose levers (over-servicing, billing review, tendering …) are customer-side; its "future models" put Europress in the middle of transport | **Cross-check only.** Its `over_servicing` lever is our "fewer trips" value seen from the customer. Our revenue model (operators pay per verified tonne, sensors subsidised) is different, so `pipeline/fullload/business.py` is our own and cites the kit's numbers where they overlap. |
| `examples/` | Small scripts: `weighing_accuracy_value.py`, `recommendation_api_mock.py`, SQL examples | **Adapt with attribution.** Part 1 adapts `weighing_accuracy_value.py` in `part1/scripts/`. Our proposal payload is `fullload.proposal.v1`, which keeps the mock's `smve.recommendation.v0` fields (`requires_human_approval`, `auto_execute`, `evidence.observed/estimated/hypothetical`, `not_proven`) and adds ours. |
| `data/quickstart/public` (50 devices × 90 d, 19 MB) and `data/competition/public` (447 × 365 d, 116 MB) | Parquet packages; `labels_dev/` holds dev labels | **Read-only input.** Competition pack for the demo; quickstart for fast tests and development loops. |
| `docs/`, `tests/` | Reference | Read `SCHEMA.md`, `DATA_DICTIONARY.md`, `ECONOMIC_MODEL.md` before using a column or a price. We don't run or extend the kit's tests. |

Rules:
- **The kit is pristine and read-only.** Never edit, move or rename anything under `resources/`. (The `__pycache__` and
  `*.egg-info` folders an earlier install left there are harmless.) The long path is written once, in config.
- **One config entry point**: `pipeline/fullload/config.py` reads `FULLLOAD_KIT` (kit root) and `FULLLOAD_DATA`
  (data package root; default competition, `quickstart` for tests) from the environment, with defaults pointing into
  `resources/`. Worktrees and agents set them to absolute paths of the main checkout.
- **Not in git**: `resources/` (size, and the kit has no licence file), `venv/`, `.venv/`, the audio file, pipeline
  caches. Setup notes say: put the kit at `resources/Europress_SMART_Material_Value_Engine_v1.0.1/`, then
  `pip install -e` it. The committed `web/public/data/bundle.json` means the demo itself never needs the kit.
- **Labels**: `labels_dev` is read only by `pipeline/fullload/validate.py` (scores via `europress_data.evaluate`,
  validation split) and `pick_heroes.py`. Nothing else may import it.

```
sinceai26-haaste/
  PRODUCT.md  TOMMI_QUESTIONS.md  README.md  THIRD_PARTY.md  LIMITATIONS.md
  briefs/                          agent briefs (Part 1 …)
  resources/                       starter kit + data — read-only, not in git
  pipeline/
    pyproject.toml                 package "fullload"; depends on europress-smart-material-value-engine
    fullload/
      config.py                    FULLLOAD_KIT / FULLLOAD_DATA
      kit.py                       the only bridge to kit internals (sdk, economics, baselines)
      forecast.py                  monthly tonnage per device; own-history vs peer backtest → σ_inc, σ_ent
      trips.py                     typical full payload per device; trips under weight trigger vs actual
      reprice.py                   economics.price_event on actual and per-kg scenarios
      market.py                    region inputs + Python reference implementation of the bidding model
      reconcile.py                 device kg vs weighbridge vs invoice, ± σ (beat 5)
      business.py                  operator-paid fee per verified tonne, sensor subsidy, payback
      validate.py                  scores vs labels_dev (validation split only)
      pick_heroes.py               deterministic hero IDs → heroes.json
      export.py                    bundle.json with Figure objects
      params.yaml                  every hypothetical parameter with its rationale
    tests/                         run against quickstart
  part1/                           Part 1 agent's branch output (sigma_tiers.json is read by export.py)
  web/                             Vite app; public/data/bundle.json is committed
```

### 7.3 Figures and receipts
Every number the UI shows is a `Figure` from the bundle:
`{value, sigma, unit, tag: observed|estimated|simulated|hypothetical, formula, sources: [table.column], row_ids: [...], assumptions: [...]}`.
The UI never hard-codes € or kg. Browser-side maths (market bidding, sliders) must mirror a Python reference
implementation, guarded by a parity test on fixed inputs.

### 7.4 Data notes
- Monthly tonnage: `collection_events` (`status = COMPLETED`, `device_estimated_collected_kg`, `actual_at`) joined to
  `reference/devices` (`material_stream`, `container_volume_m3`) and `reference/sites` (`region_code`). 404 devices with
  weight, 12 months.
- Payload: device's full lifts (`trigger_type = ON_CALL_ORDER`, high `device_fill_pct_before`).
- Current prices: `reference/contract_versions` (`pricing_model`, `lift_fee_cents`, `processing_fee_cents_per_t`, …);
  per-kg comparison prices from PER_TONNE contracts of similar sites (66 contracts).
- Operators in a region: `collection_events.operator_id` × `sites.region_code`.

### 7.5 Part 1 in the demo
**Target level: complete and decent.** D1 must tick every item the brief lists and no more. In the app: tier cards
plus the slider only. No pressure-signal models, hardware simulations or extra Part 1 screens.
- **T1 strain gauges — the chosen concept (working assumption).** Bonded/weld-on strain gauges on the frame or
  container rails + a cheap amplifier on the SMART modem. Low cost, retrofit-friendly, per-unit calibration,
  temperature-sensitive. Free to the customer; its cost per device is an input to the business case payback.
- **T0 virtual weight** (alternative / future software upgrade): existing hydraulic pressure / ram position + fill +
  material density, calibrated per device with occasional reference weighings. €0 extra BOM. Weak for biowaste.
- **T2 shear-beam load cells** under the DUO container frame or COMBI base frame + summing box + transmitter on the
  SMART modem: best accuracy, highest cost and install effort.
- All costs and σ labelled *estimate, to be validated with suppliers*; the dataset's ≈ ±100 kg on 3 t is *a simulation
  target, not a Europress specification*.
- The slider's σ feeds the forecast σ and the bill-check uncertainty in beats 3–5. Validation plan card: bench test, field
  pilot paired with weighed-tare weighbridge tickets, acceptance threshold, 90-day drift watch. Stated as **untested**.

### 7.6 LLM decision
- **No LLM in any number, status or decision.** Deterministic and traceable.
- **One bounded AI feature for the customer (nice-to-have 2):** a plain-language brief for the facility manager
  ("how full your lifts were, what per-kg would mean for you, what we propose"), generated by Claude **at build time**
  from a structured fact sheet, number-checked by a script, reviewed by a human, frozen, labelled "Drafted by AI from
  the evidence below". Template fallback always exists.
- Pitch slide: how we built with AI agents.

## 8. Engineering rules for agents

**Demo safety**
- Static build + committed JSON; no runtime network. The demo machine never needs Python.
- Every screen renders with the committed bundle; missing data shows "not available", never a crash or a blank chart.
- Determinism: fixed seeds, sorted outputs, committed hero IDs; running the pipeline twice yields byte-identical JSON.
- After **Sat 22:00**: fixes and copy only. After **Sun 00:00**: no dependency changes, no refactors, no regeneration.
- Don't break `main`: merge only when `npm run build` and `pytest pipeline` pass.

**Data and money**
- Money in integer cents via `europress_data.economics`; format only in the UI. Never reimplement tariff rules.
- Unknown mass ⇒ `null` and "cannot be computed". Never impute a mass or a €/t.
- Every hypothetical parameter lives in `pipeline/params.yaml` with a rationale line; never inline.
- `labels_dev/` is only for hero selection and validation, never a feature. Never touch test periods or `private_evaluation/`.
- Read `docs/SCHEMA.md` / `docs/DATA_DICTIONARY.md` before using a column; quote it in the Figure's `sources`.

**Wording** (full tone pass happens before the freeze; for now keep these minimum rules)
- Banner on every € screen: "Synthetic data · hypothetical prices · simulation".
- Results of the replay and the market simulation are *simulated*, never "savings achieved".
- Every action is a proposal with `requires_human_approval: true`. No button may imply sending anything.
- Do not put "SMART" in our product name.

**Where not to spend time**
CSS perfection before freeze, generic components, settings pages, abstractions for future tasks, ML models beyond the
rules-vs-ML comparison, more than three hero cases. If a chart doesn't serve a line in §4, delete it.

**Testing stance**
Few, demo-serving tests: (1) tonnage conserved between regimes; (2) re-pricing matches `labels_dev/reference_economics`
on a sample; (3) forecast backtest reproduces the published σ values; (4) Python ↔ TypeScript parity for the bidding
model; (5) determinism; (6) the bundle parses against its TypeScript type and every `Figure` has `tag` and `sources`.
No UI unit tests; a manual click-through checklist per beat.

**Licences**
Adding a dependency = adding a row to `THIRD_PARTY.md` (name, version, licence, commercial-use note) in the same
commit. Include the starter kit and dataset (terms to confirm), fonts/icons, hosting, Claude API if used, Claude Code as a dev tool.

## 9. Risks and open questions

| Risk | Mitigation |
|---|---|
| Market simulation looks invented | Data-derived inputs (σ backtest, tonnage, payloads, current prices); hypothetical parameters in one file with rationale and sensitivity sliders; result holds across slider ranges or we say where it doesn't |
| Per-kg pricing looks worse for some customers | Show the distribution, not only the hero; say who loses (e.g. dense, already-full sites) |
| 12 months of data cannot show "time of year" knowledge | State it; the asymmetry is measured on 3-month horizons; seasonality is a named limitation |
| Free sensors don't pay back | Business case shows sensor cost per device vs per-tonne fee per device-year; payback months on screen; T0 as the zero-hardware fallback |
| Device weight presented as a legal-for-trade billing weight | Wording: device weight checks the bill, the certified weighbridge settles it (§1); device settlement only by contract agreement |
| Europress hears the model as going into transport | Always: operators pay a service fee per verified tonne; Europress never contracts transport |
| Part 1 scores low because it is "only decent" | D1 ticks every brief item; the slider ties it to the simulation; skip depth, never an item |
| Simulation overruns | Fallback: static before/after table for the hero region with the same numbers, no sliders |
| Projector / Wi-Fi / laptop failure | Offline build on two laptops + recorded video + screenshots in slides |

**Open questions**
- For Tommi and Since AI: `TOMMI_QUESTIONS.md` (ask Sat morning, write answers there, update this file).
- Internal: hypothetical operator cost parameters and fee level, and who signs them off [business-case teammate, by Sat 13:00].
