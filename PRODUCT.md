# PRODUCT.md — OpenWeight

> North star for everyone (humans and coding agents) working in this repo. **The only goal is an impressive,
> credible end-to-end demo that wins the Europress challenge at Since AI Hackathon 2026.** Not production
> reliability, not benchmark scores. If a task does not make the demo storyline in §4 better, safer or more
> believable, do not do it. When this file and your instinct disagree, this file wins; change it deliberately.
>
> Hard deadline **Sun 8 Nov 2026 10:00**; we submit by **09:30**. One person codes (with agents); two teammates
> own validation, the weighing-concept document, the business case and the pitch.

## 1. Thesis

**OpenWeight — pay for tonnes, not trips.**

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

**OpenWeight breaks this.** The compactor weighs its own load, and the collection data lives with Europress, not with
one operator. Europress sells **weight-based forecasts and device weights to every operator** on equal terms. Any
operator can now price per kg with the same precision as the incumbent, so customers can tender on per-kg terms
and efficient operators, including new entrants, can win.

### Who pays, who uses (decided)
- **Operators pay**: a **service fee of €30 per weighed device per month** (changed 7 Nov evening, `docs/PRICING.md`;
  ≈ €3.9 per tonne at the fleet's 92.6 t per device-year, the equivalent the market model uses), as a SMART add-on. They get site forecasts, weight-triggered
  lift orders and a device weight to check every bill against. It is what lets them offer per-kg prices without risk.
- **The weighing hardware is free for customers**, funded by Europress and paid back from the operators' fees.
  Every new COMBI gets the H7 hydraulic self-lift, factory-fit (a two-end version, H7-2, is an option for higher
  accuracy). DUO containers have no hydraulics; for DUO the hopper plate (H1) or weighing rails (H5) remain the
  options. The team's planning cost for H7 is **€1,000 capex per new unit** (upkeep €73/yr); at that cost €30 is the
  break-even fee: NPV +€0.18 M over 10 years, payback year 9 (`docs/PRICING.md`). The margin is thin: above ~€1,020 capex
  €30 no longer pays back (Part 1 estimate €800–2,370, mid €1,585 → −€4.53 M), so a supplier quote comes first.
  The COMBI/DUO split of new units is unknown; the model assumes all ~1,200 new units a year are weighed.
- **Customers use it for free**: they see how full their containers are when emptied, what per-kg billing would
  simulate to for them, and they get the prompt to tender on per-kg terms. **The customer decides to tender.**
  It must be effortless (a property manager spends ~3 % of working time on waste): plain-language AI reports that say
  what the data means and which decision to take, and value **between tenders** too (contracts run ~3 years), e.g.
  service-level follow-up and monthly reports, so Europress stays present all the time.
  **Visibility is value in itself** (team insight, 7 Nov): the customer sees whether the operator keeps the contract
  (on-time visits, missed visits, weighbridge-ticket sharing, invoice lines vs contract terms), not only a better price
  at the next tender. Beat 2 shows this (`customer.service_check`).
- **Europress stays a technology company**: it never drives trucks, contracts transport or takes a transport margin.
- **Billing stays as it is today (decided)**: the final bill is based on the operator's certified weighbridge, exactly as
  now. That keeps billing legal: in the EU a weight used to set a price must come from an approved non-automatic weighing
  instrument (Directive 2014/31/EU), which the device scale is not designed to be. We do not propose device-weight billing.
- **The device scale produces the data for the service**: forecasts, weight-triggered pickups and the per-site tonnage
  that operators need to price per kg. For that, ballpark accuracy (a few %) is plenty.
- **Cross-check (side benefit, but a strong one)**: the same device weight is visible to customer and operator, so a
  difference from the weighbridge figure is flagged for a human to look at. That gives the customer peace of mind and
  the operator a solid reason to report honestly. The H7 estimate is ±4.4 % 1σ after 10 shared weighbridge tickets (est., untested;
  about ±10 % without tickets), so a clear tonnage difference shows after a few loads.
  Never claim the device weight is legal for trade.

Pitch line: *"Today the weight — and the knowledge of every site — belongs to the incumbent. OpenWeight puts it in the
compactor, so every operator can compete per kilo."*

### Decisions and facts, 7 Nov afternoon
- **OpenWeight never relays offers (decided 7 Nov night, from a teammate; matches Tommi: Europress does not want to
  sit inside the tender or the contract).** The waste company plans its per-tonne price in its portal and sends the
  offer the usual way; the customer uploads the offers it received and compares them per tonne with the service
  record beside the price. No "send offer" button, and the waste company never learns whom the customer chose.
- **Name: OpenWeight** (for now). The Python package stays `fullload` internally; user-facing text says OpenWeight.
- **The customer owns the data** and decides who may see it; sharing the weight profile with bidders is a consent step
  in the customer view.
- **Source of truth for numbers: this repo's pipeline** (evidence in `bundle.json`, tests, validations). Figures from
  team documents without scripts are compared, not copied (`value_per_device` shows both).
- **Biowaste is left out of the business claims** (`config.EXCLUDED_MATERIALS`): hardest stream to weigh. Observed
  fleet facts keep every stream.
- **Municipal waste is out of scope**: there the customer cannot choose the operator.
- **Weighing architecture (changed 7 Nov evening): H7 on every new COMBI.** The compactor lifts itself with its own
  hydraulics and reads the weight from the pressure (Part 1 §19). Shared weighbridge tickets calibrate each unit.
  DUO containers have no hydraulics; for DUO the hopper plate (H1) or weighing rails (H5) remain the options. A
  virtual scale (`virtual_scale`, simulated ~8 % per lift) is not part of the product claim; at most a roadmap item
  that could later estimate weights on older units.
- **New facts** (team document `docs/fi/TIIMILLE.md`): Europress already sells a weighing product, **Scaletipper X1**, which is
  expensive, fits only bin-fed sites, and whose data stays in tenant reports (prior art for Part 1). HSY's logistics
  manager: *"Kuljetusyritys ei suoraan säästä, jopa menettää"* (the transport company does not directly save, it may
  even lose). SMART promises 37 % fewer emptyings (do not confuse with our forecast-error figures in the pitch).

### Figure decisions (7 Nov, delegated to Claude by the lead developer; evidence in `bundle.json`)
Use only these figures in the demo, the pitch and the documents. Other team documents' numbers are superseded.
| Topic | Use | Why |
|---|---|---|
| Incumbent's information advantage | **±10 % vs ±37 %** forecast error (own history vs peers, monthly tonnage, 3 held-out months) | What an operator prices; reproducible backtest. The team's 9 % vs 21 % (per visit) corroborates the direction; do not show both. Never next to SMART's "37 % fewer emptyings". |
| Fewer trips | **6–18 %** (labels lower bound – model upper) | Validated per device (r = 0.85). |
| Customer saving | **−12 % cost per tonne** in the simulated region (€113.1 → €99.6, with the €30 fee = €3.9/t); visits −19 % is the same region, fleet-wide 6–18 % | Market model. The showcase customer's −30.8 % only as "best case". |
| Customer value per device | **avoidable visits €0.7–1.5k/yr**, tonnes priced above peers **~€1.3k/yr** | Agree with the team's independent estimates. |
| Operator value | **"removes the risk premium on per-kg bids"**, no single € figure | Our €2.7k and the team document's operator figure are both parameter-driven. |
| Europress | **€30 per weighed device per month** (changed 7 Nov evening, `docs/PRICING.md`), customer pays €0. Every new compactor gets the H7 self-lift. Base (H7 €1,000 capex, team decision): **NPV +€0.18 M, payback year 9, deepest −€3.83 M**; €30 is the break-even fee. Sensitivity: Part 1 range €800–2,370 (mid €1,585 → −€4.53 M); above ~€1,020 capex €30 does not pay back | `pipeline/fullload/pricing.py` reproduces the team model exactly (H7 €825 → +€2.49 M, y7); €20 never pays back at the base (−€2.46 M) |
| Weighing | **H7 hydraulic self-lift on every new COMBI**: ±4.4 % 1σ after 10 shared tickets (est., untested; ~±10 % without), €1,034–3,008 installed factory-fit (capex €800–2,370, upkeep €39–106/yr). H7-2 (both ends) is an option for higher accuracy. DUO: hopper plate (H1) or weighing rails (H5). The weighbridge stays the bill | H7 shows original thinking; prior art exists for truck-side hydraulic weighing (Hiab US 2020/0096383), not found for a compactor lifting itself |
| Live AI Q&A for customers | **Out.** No chat. Pitch demo: frozen, number-checked AI report. Product demo (`app/`): Gemini rewords fixed texts at runtime; a guard rejects any reply with a number not in the facts, replies are cached, and a template is the fallback | Stage risk; the brief rewards traceability. |

### Where we put our effort
- **The business model and the market before/after is our differentiator** and gets most of the effort. It came from
  domain knowledge in our team and lines up with what Europress said at kickoff.
- **Part 1 (weighing) is now a real second track (changed 7 Nov after talking to Tommi).** Weight is what blocks
  Europress today ("we always stop halfway"), and he wants the pitch to show *how* we get it. A supervised agent
  deepened the concept (`part1/WEIGHING_CONCEPT.md`; H7 hydraulic self-lift is the lead, hopper plate and weighing
  rails are the DUO options, full installed cost, calibration from shared tickets); a teammate reviews it. The coder's time stays on the
  pipeline and demo; the demo's sensor beat grows to about a minute.

## 2. What Europress told us at kickoff (Tommi Häkkinen, 6 Nov) — design constraints

Source: kickoff recording transcript (`talks/Röst 261106_182238.txt`, local only, Whisper, imperfect).

| What was said | What it means for us |
|---|---|
| "We are **not** going into transportation operating … we are a technology company." | Europress never owns trucks or becomes the hauler. The fee (per device per month) is a service fee paid by operators. |
| The biggest operator owns trucks and "the more transportation they get the more money"; other operators use subcontractors and benefit from transporting as little as possible. A direct integration with a "good operator" was very hard. | The market is split by incentive: one dominant player profits from trips, others from efficiency. Our natural first customers are the efficiency-driven operators. Do not depend on operator data feeds. |
| Some operators already resell SMART Insights to retail chains to win contracts. Partnerships are strategy. | Selling to operators is already proven. Operator-paid model fits. |
| Weighing: "cheap as possible, it doesn't need to be all accurate … ballpark but really close." Customers "are not willing to pay almost anything" for extra hardware. | Part 1 leads with the cheapest viable option. Customer side must be free. |
| The hydraulic **pressure sensor** is "the fingerprint" of the compactor (up to ~200 bar, ram position over time); fill from back-pressure to ~5 %. Biowaste gives little back-pressure; humidity changes cardboard weight. Pressure examples were offered via Discord. | Basis of H7: the compactor lifts itself and reads its own pressure. Biowaste and wet cardboard are named limitations. |
| ~60–70 % of machines auto-order at ~80 % fill; ~30 % in Finland on fixed schedules; Central Europe/Poland much less automated. | Growth market for per-kg models; fixed schedules are where the waste is. |
| SMART Insights is in only ~**15 %** of the installed base; digital services are the most profitable; small customers are hard to sell to. | Free customer side solves the small-customer sales problem; operators pay. |
| Transport is usually a **fixed price per lift**, agreed between operator and customer; treatment fees are much higher. | Confirms the per-trip pricing the model attacks. |
| "I'm interested in how you managed to utilise AI capabilities … e.g. better end-customer experience." | One bounded AI feature for the customer (§7.6) and one pitch slide on how we built with AI agents. |

**Follow-up talk, 7 Nov** (`Since.AI.2.txt`, Finnish):

| What was said | What it means for us |
|---|---|
| On our incumbent-data thesis: "a good starting point… probably something the market needs"; "you're on the right track". | The business model stands. |
| Contracts run ~3 years with service-level terms (e.g. response times), then are re-tendered, mostly on price, which can backfire. | Tendering happens rarely; the customer view must also give value between tenders. |
| Serving operators is part of Europress strategy; an operator that gains an edge would also promote Europress machines. | Operator-paid model fits; operators become a sales channel. |
| Think it through from the buyer's / property manager's view; they spend ~3 % of their time on waste. Free AI reports that explain the data and the decision. | Customer side: effortless, AI-written reports (§7.6 moves from nice-to-have towards must-have). |
| Without weight "we always stop halfway"; show how we get the weight, pitched as if selling to him. | Part 1 becomes a real track (§1). |
| Europress already has scale platforms under the unit, but they are "almost as expensive" (as the machine). A COMBI costs ~€20–25k; ~€2,000 for weighing came up as the reference. | Cost reference for Part 1: full installed cost vs ~€2k; platform scales are the prior attempt to beat. |
| Weigh at the feed hopper and sum the charges, instead of weighing the whole container; "not trivial, but easier than the alternatives". | Hypothesis H1, credited to Europress; now the DUO option (H7 leads for COMBI). |
| Big chains (e.g. Kesko) have ~100 machines, shopping centres ~20; roughly 10,000 machines mentioned. | Market sizing for the business case. |

## 3. The market before/after simulation (the centrepiece)

A **stylised, deterministic** simulation of one region, built from the real (synthetic) sites. It shows how the
actors behave under each regime. Simple enough to explain on one screen, grounded in data where possible, and
explicit about every assumption.

**Actors**
- **Customers**: real sites/devices in one region (tonnage, material, container size and lifts from the data).
- **Incumbent operator**: has the collection history → forecast error σ_inc ≈ 10 % (measured).
- **Entrant operators (1–3)**: no history → σ_ent ≈ 38 % before (measured peer-based error); ≈ 10 % after (OpenWeight forecast).
- **Europress**: provides weights and forecasts after; fee per device (per-tonne equivalent in the model).

**Regimes**
| | Before: per trip, private data | After: per kg, OpenWeight data |
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

## 4. Demo storyline (decided 7 Nov 15:30: three screens, target 4:30, hard max 5:00)

> **8 Nov: the three pitch screens and detail screens (`web/`) were deleted. The demo is `app/` (below).** The
> story outline in this table still holds for the pitch and the video.

Three pitch screens; the presenter steps with the arrow keys and never types. Deep links `/#/beat-1` … `/#/beat-3`.
The ecosystem diagram carried screen 3: it starts in its *today* state and
adds one arrow per step. Screen 1 shows only the per-visit vs per-tonne evidence.

| # | Time | Screen | On screen | Line |
|---|---|---|---|---|
| 1 | 0:00–1:15 | **The market today** | Per visit vs per tonne, observed: a visit costs about the same (€143–160) whether the compactor is under 60 % or over 90 % full, so per-visit charges are €167/t vs €49/t (3.4×). Receipts: 56.5 % of charges are per visit; 0 of 19 customers a challenger can safely win. No diagram (it starts on screen 3) | "Customers pay for trips. Only the incumbent knows the tonnes." |
| 2 | 1:15–2:45 | **How we get the weight** | H7 hydraulic self-lift, animated side view: tare 27 bar → reading 57 bar → 2.5 t; accuracy ±4.4 % (1σ, est.), installed cost vs the ~€2k reference and the platform scale; known limits. Every new unit weighs itself; the certified weighbridge stays the bill and its tickets calibrate the device | "The compactor weighs itself, with the hydraulics it already has." |
| 3 | 2:45–4:30 | **The value** | Ecosystem diagram revealed one arrow per click / → (3 boxes, ≤ 3 arrows, fades only): ① the compactor weighs every lift → Europress, ② the same data to every operator, ③ per-kg bids straight to the customer (Europress is not in the tender); then the market KPIs (€/t −12 %, visits −19 % in the simulated region, 19 / 19 contestable); what each party gets: customer free, operators €30 / device / month, Europress: NPV +€0.18 M over 10 years, payback year 9 with the self-lift at €1,000; €30 is the break-even fee | "Same waste, fewer trucks, open competition. Europress never drives a truck." |

**Detail screens** (not in the pitch; for questions, the walkthrough video and judges exploring): Fleet, Customer
(AI-summarized report, contract check, proposal + approve), Operator (forecast table, bids), Market (all sliders),
(The Business screen was removed on 8 Nov: the business model lives in `docs/PRICING.md`, `docs/BUSINESS_CASE.md` and `pipeline/fullload/pricing.py`.)

**Cut from the pitch demo on 7 Nov (roadmap lines only):** multi-round market simulation; ESG panel; daily lift
replay; invoice upload. Invoice matching, the operator "due soon" list, the Europress sales lead and the customer
consent step now live in the product demo below.

**Product demo (`app/`, built by the team on 7 Nov evening, merged into this repo on 7 Nov night). Decided 7 Nov
night: this is the demo of record** for the video and the judges; the three pitch screens above are an earlier
prototype. Same numbers (it reads `bundle.json`; the hero is ORG-0036).
- **Customer portal (free):** *Contract*, the first screen (is the contract kept: response, schedule, tickets; every
  pickup traces order → ticket → contract version → invoice lines), *Today* (fill level with pickup at 80 %, weight and
  € per tonne before the truck leaves, a three-item report with Approve / Not now / Undo, invoice query), *Tender* (offer
  comparison: uploaded offers per tonne, service record beside price; share or withdraw the weights).
- **Waste company portal (paid):** *Tenders* (offer planning for a tender request it uploaded: bid pack, forecast,
  price with and without the weights on its own costs), *Weight check* (trucks whose tickets disagree with the
  compactors: tare errors).

## 5. Where the points come from

| Criterion (weight) | What earns it | Beats | Deliverable |
|---|---|---|---|
| Weighing concept (25 %) | H7 hydraulic self-lift on every new COMBI (H1 / H5 for DUO; T0 virtual weight as roadmap); placement COMBI/DUO; BOM ranges; installation; calibration (factory, reference weights, cross-check with shared weighbridge tickets, auto-zero after each lift); error sources (temperature, humidity, off-centre load, press cycle, biowaste); validation plan; slider linking σ to value | 1, 4, 5 | D1 illustrated concept (agent-drafted, teammate-reviewed) |
| Customer/business value (25 %) | Customer per-kg cost vs per-trip; fewer trips; competition; operators' risk removed | 2–4 | D3 |
| Data-driven value & traceable calcs (20 %) | Measured forecast asymmetry (10 % vs 38 %); market simulation with stated parameters; re-pricing with the starter kit's economics; receipts on every €; **rules vs ML comparison** (brief §04): e.g. our premature-lift rule vs kit baseline B4, and simple history forecast vs a slightly richer model | 2–5 | D2 + methods page |
| Software workflow & SMART pathway (15 %) | Flow: weight → forecast → customer proposal → approval → tender brief → operator plans its per-kg bid with the bid pack (product demo) → customer compares the uploaded offers → per-kg bill checked against device weight; integration diagram (SMART telemetry in, forecasts and lift orders out to operators) extending `examples/recommendation_api_mock.py` | 2–6 | D2 + setup notes |
| Commercial productisation (10 %) | Operator-paid fee per device per month, free customer side, adoption path (efficiency-driven operators first), sensitivity, roadmap | 6 | D3 |
| Clarity / uncertainty / limits (5 %) | ± on every figure, evidence tags, synthetic banner, "what this does not prove", simulation assumptions on screen | all | all + licence list |

Required submission items (brief §07): (1) illustrated weighing concept; (2) working demo **and** a recorded
walkthrough, code/setup notes, traceable economics, SMART integration; (3) customer value and business case.
Plus `docs/THIRD_PARTY.md` (every library, model, dataset, service + licence) and `docs/LIMITATIONS.md` (assumptions, untested).

Starter-kit tasks covered: **A** re-pricing; **B** premature lifts (without flagging justified ones); **B2** operator
efficiency figures inside the simulation; **C** context only (thresholds/schedules are SMART's domain; we sell the
commercial model on top); **C2** tender proposal with human approval; **D** operator-paid fee per weighed device with our own
price and adoption reasoning (`baselines/business_case.py --params`); **E** receipts, ± and evidence tags.

## 6. Scope (1 coder × ~1.5 days)

### Must-have, in build order
1. **Pipeline skeleton** → one deterministic `pipeline/out/bundle.json`.
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
Route optimisation and truck load planning (roadmap line in the pitch only), auth, live operator/SMART integration,
an LLM chatbot, relaying offers between operators and customers, (pitch demo only:) databases and a runtime backend, ML leaderboard chasing, a generic Tasks A–E dashboard, a better
threshold algorithm sold *as such*, contamination detection, agent-based learning simulations, mobile layout, i18n,
Docker, anything in `private_evaluation/`.

### Time plan
| When | Coder (+ agents) | Teammates |
|---|---|---|
| Fri 22:00–01:30 | Fresh `.venv` (the existing `venv/` is the whisper env — leave it), starter kit editable, scaffold, pipeline skeleton, forecast backtest, trips model; background agent drafts D1 | Review `docs/TOMMI_QUESTIONS.md`; review D1 draft |
| Sat 08:00–13:00 | Market simulation + beat 4 screen (**wow first**), hero selection | Ask Tommi + Since AI; set hypothetical cost parameters with rationale; hand-check one site's numbers |
| Sat 13:00–18:00 | Beats 2, 3, 0, 6; proposal/approve; receipts | D3 business case with our numbers; pitch skeleton; D1 final |
| Sat 18:00–22:00 | Three pitch screens (decided 15:30), design pass on them, ecosystem diagram polish; deploy static build | Rehearse on the live build, report bugs |
| **Sat 22:00 FEATURE FREEZE** | Fixes and copy only | Dry run #1, timed |
| Sat 22:00–24:00 | Dry-run fixes; record walkthrough | Dry runs #2–3; slides final |
| **Sun 00:00 DEMO FROZEN** | git tag `demo-frozen`; bundle and build committed | |
| Sun 07:00–09:30 | Typos, setup notes, `docs/THIRD_PARTY.md`, `docs/LIMITATIONS.md`; **submit by 09:30** | Final rehearsal; upload |

## 7. Architecture

### 7.1 Stack
**Python precompute → `pipeline/out/bundle.json` → the app.** `app/`: `build_data.py` (reads `bundle.json` and the kit through `fullload.kit`) → JSON →
FastAPI + SQLite demo state → React portals; optional Gemini wording (§7.6).
- `pipeline/` — Python (3.14 is what this machine has; the kit needs ≥ 3.11), pandas + DuckDB + pyarrow, on top of the
  starter kit (§7.2). Our euros are *the dataset's own euros*.
- `app/` — FastAPI backend + Vite/React/TypeScript frontend (the pitch screens in `web/` were deleted on 8 Nov).
- Rejected: Streamlit (generic look, poor control over a staged story), notebooks (not a product).

### 7.2 How our code fits the starter kit

The kit (`resources/Europress_SMART_Material_Value_Engine_v1.0.1/`) is three different things, and each one is used
differently:

| Kit part | What it is | How we use it |
|---|---|---|
| `src/europress_data/` | An installable package (src layout, `pyproject.toml`): `sdk.open_dataset` (DuckDB views, `as_of`, `telemetry_dedup`), `economics.price_event` / `summarize` (contract pricing in integer cents), `evaluate.score_*` (scorers on `labels_dev`); plus the generator and validator | **Import it.** `pip install -e resources/Europress_…_v1.0.1` into our `.venv`. All data access goes through `open_dataset`, all money through `economics`. Never copy or reimplement these. The generator, validator and simulator modules are not used. |
| `baselines/*.py` | Scripts, not a package; they put `src/` and `baselines/` on `sys.path` themselves. Useful functions: `b1_economic_calculator.compute` (expected charges per lift + mass basis), `b2_rules_anomaly` (premature-lift and invoice rules), `b4_ml_models` (the ML side of the rules-vs-ML comparison), `b5_operator_scorecard.scorecard` | **Import through one adapter**, `pipeline/fullload/kit.py`, which is the only file that touches `sys.path` or kit internals. Everything else imports from `fullload.kit`. If a kit function doesn't fit, wrap it there; don't edit the kit. |
| `baselines/business_case.py` + `configs/` | A customer-value calculator whose levers (over-servicing, billing review, tendering …) are customer-side; its "future models" put Europress in the middle of transport | **Cross-check only.** Its `over_servicing` lever is our "fewer trips" value seen from the customer. Our revenue model (operators pay per device, sensors subsidised) is different, so `pipeline/fullload/pricing.py` is our own and cites the kit's numbers where they overlap. |
| `examples/` | Small scripts: `weighing_accuracy_value.py`, `recommendation_api_mock.py`, SQL examples | **Adapt with attribution.** Part 1 adapts `weighing_accuracy_value.py` in `part1/scripts/`. Our proposal payload is `openweight.proposal.v1`, which keeps the mock's `smve.recommendation.v0` fields (`requires_human_approval`, `auto_execute`, `evidence.observed/estimated/hypothetical`, `not_proven`) and adds ours. |
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
  `pip install -e` it. The committed `pipeline/out/bundle.json` means the demo itself never needs the kit.
- **Labels**: `labels_dev` is read only by `pipeline/fullload/validate.py` (scores via `europress_data.evaluate`,
  validation split) and `pick_heroes.py`. Nothing else may import it.

```
sinceai26-haaste/
  README.md  CLAUDE.md  PRODUCT.md  MASTER.md  SUBMISSION.md  TODO.md   entry points and decisions
  docs/                            submission docs (business case, pricing, limitations, SMART integration,
                                   third-party list, walkthrough script, questions for Europress)
  docs/fi/                         the team's Finnish material: OpenWeight.pdf (from template.html via build_pdf.py),
                                   LIITE, video script, team papers; analysis/ = their cash-flow scripts
  talks/                           recordings and transcripts of the Europress talks (local only, not in git)
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
      pricing.py                   operator fee per weighed device, H7 cost, NPV / payback (team model)
      validate.py                  scores vs labels_dev (validation split only)
      pick_heroes.py               deterministic hero IDs → heroes.json
      export.py                    bundle.json with Figure objects
      params.yaml                  every hypothetical parameter with its rationale
    tests/                         run against quickstart
  part1/                           Part 1 agent's branch output (sigma_tiers.json is read by export.py)
  pipeline/out/bundle.json         every figure, committed; the app reads it
  app/                             product demo: backend/ (FastAPI, build_data.py, llm.py), frontend/ (React portals)
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
**Chosen concept (changed 7 Nov evening): H7 hydraulic self-lift on every new COMBI** (`part1/WEIGHING_CONCEPT.md`
§0, §19; untested). DUO containers have no hydraulics; for DUO the hopper plate (H1) or weighing rails (H5) remain
the options. In the app: screen 2 shows H7, its installed cost and its accuracy with and without tickets. The v1 tiers
below are history. The coder does not build hardware models; the Part 1 agent's scripts produce the numbers.
- **T1 strain gauges** (v1 working assumption, superseded by H7). Bonded/weld-on strain gauges on the frame or
  container rails + a cheap amplifier on the SMART modem. Low cost, retrofit-friendly, per-unit calibration,
  temperature-sensitive. Free to the customer; its cost per device is an input to the business case payback.
- **T0 virtual weight** (roadmap: could later estimate weights on older units): existing hydraulic pressure / ram position + fill +
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
- **Product demo (`app/`)**: Gemini (`gemini-3.6-flash`, `GEMINI_MODEL`) rewords the report paragraphs, the invoice
  query and the one-line offer summary at runtime. It never produces a figure: `llm.guarded` rejects any reply
  containing a number not in the facts, and the template text is shown instead. Replies are cached by hash, so a
  demo run costs nothing after the first.
- Pitch slide: how we built with AI agents.

## 8. Engineering rules for agents

**Demo safety**
- The demo (`app/`) needs Python and a local server, but not the starter kit (its data is committed); without network or a Gemini key it falls back to template texts.
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

**Rules over accuracy (decided 7 Nov)**: transparent, explainable rules beat small accuracy gains. Example: our
premature-lift rule (F1 0.81, 0 justified lifts flagged, every flag explained) is preferred over the kit's ML baseline
(F1 0.93, 13 justified lifts flagged, no reasons). ML appears only as the comparison the brief asks for.

**Where not to spend time**
CSS perfection before freeze, generic components, settings pages, abstractions for future tasks, ML models beyond the
rules-vs-ML comparison, more than three hero cases. If a chart doesn't serve a line in §4, delete it.

**Testing stance**
Few, demo-serving tests: (1) tonnage conserved between regimes; (2) re-pricing matches `labels_dev/reference_economics`
on a sample; (3) forecast backtest reproduces the published σ values; (4) Python ↔ TypeScript parity for the bidding
model; (5) determinism; (6) the bundle parses against its TypeScript type and every `Figure` has `tag` and `sources`.
No UI unit tests; a manual click-through checklist per beat.

**Licences**
Adding a dependency = adding a row to `docs/THIRD_PARTY.md` (name, version, licence, commercial-use note) in the same
commit. Include the starter kit and dataset (terms to confirm), fonts/icons, hosting, Claude API if used, Claude Code as a dev tool.

## 9. Risks and open questions

| Risk | Mitigation |
|---|---|
| Market simulation looks invented | Data-derived inputs (σ backtest, tonnage, payloads, current prices); hypothetical parameters in one file with rationale and sensitivity sliders; result holds across slider ranges or we say where it doesn't |
| Per-kg pricing looks worse for some customers | Show the distribution, not only the hero; say who loses (e.g. dense, already-full sites) |
| 12 months of data cannot show "time of year" knowledge | State it; the asymmetry is measured on 3-month horizons; seasonality is a named limitation |
| Free sensors don't pay back | At the €1,000 H7 base, €30 just pays back (NPV +€0.18 M, year 9; needs ≥ 59 % paying adoption). The risk is the H7 cost: above ~€1,020 capex it loses money, and Part 1's mid estimate (€1,585) gives −€4.53 M. Mitigation: supplier quote for the self-lift first, then a pilot. `docs/PRICING.md` shows the base and the Part 1 range |
| Device weight presented as a legal-for-trade billing weight | Wording rule (§1): billing stays on the certified weighbridge as today; device weight is planning and service data |
| Europress hears the model as going into transport | Always: operators pay a service fee per device; Europress never contracts transport |
| Part 1 looks weak because no one on the team is a mechanical engineer | Claims ledger, shown working, prior-art check and red-team pass (`briefs/WEIGHING_V2.md`); questions for a Europress engineer; Tommi's hopper hint credited |
| Simulation overruns | Fallback: static before/after table for the hero region with the same numbers, no sliders |
| Projector / Wi-Fi / laptop failure | Offline build on two laptops + recorded video + screenshots in slides |

**Open questions**
- For Tommi and Since AI: `docs/TOMMI_QUESTIONS.md` (ask Sat morning, write answers there, update this file).
- Internal: hypothetical operator cost parameters, who signs them off, and the €30 fee (decided 7 Nov evening; `docs/PRICING.md`) [business-case teammate, by Sat 13:00].
- For Europress: a supplier quote confirming H7 at ~€1,000 capex (break-even ~€1,020 at €30). The COMBI/DUO split of
  the ~1,200 new units a year is unknown; the model assumes all new units are weighed.
