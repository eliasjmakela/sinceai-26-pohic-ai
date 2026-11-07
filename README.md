# OpenWeight

Since AI Hackathon 2026 · Europress challenge "SMART Material Value Engine — Weigh at Source, Create Value".

**OpenWeight: pay for tonnes, not trips.** Customers pay per truck visit, and only the incumbent operator knows how
much each site produces, so challengers cannot price per kilo. OpenWeight puts the weight in the compactor and gives
every operator the same site forecasts and weight data, with the customer's consent. Operators pay Europress a
service fee, customers use it free, and billing stays on the operator's certified weighbridge. Europress never
drives a truck and never sits in the tender: offers go from operator to customer as today. All data is synthetic and
every price hypothetical.

## Deliverables (brief §07)

| Brief asks for | Where |
|---|---|
| (1) Illustrated weighing concept: principle, placement, BOM and cost, installation, calibration, error sources, validation plan | [`part1/WEIGHING_ONEPAGER.md`](part1/WEIGHING_ONEPAGER.md); full working in [`part1/WEIGHING_CONCEPT.md`](part1/WEIGHING_CONCEPT.md) §19–20 |
| (2) Working software demo on synthetic weight data | **[`app/`](app/README.md)**: the customer's free portal and the waste company's paid portal |
| (2) Code and setup notes | this file and [`app/README.md`](app/README.md) |
| (2) Traceable economics | every figure in the app opens its calculation, and every pickup traces order → ticket → contract version → invoice lines; the business model in [`docs/PRICING.md`](docs/PRICING.md) and `pipeline/fullload/pricing.py` |
| (2) Proposed SMART integration | [`docs/SMART_INTEGRATION.md`](docs/SMART_INTEGRATION.md) |
| (3) Customer value and business case, commercial model, productisation in SMART | [`docs/BUSINESS_CASE.md`](docs/BUSINESS_CASE.md) |
| Third-party libraries, models, data and services with licences | [`docs/THIRD_PARTY.md`](docs/THIRD_PARTY.md), [`part1/THIRD_PARTY_part1.md`](part1/THIRD_PARTY_part1.md) |
| Assumptions and what remains untested | [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md) |
| Walkthrough video | recorded separately |

Internal: [`PRODUCT.md`](PRODUCT.md) (spec), [`MASTER.md`](MASTER.md) (decisions and numbers ledger),
[`SUBMISSION.md`](SUBMISSION.md) (checklist), [`reviews/`](reviews/), [`briefs/`](briefs/).

## Run the demo

Requires Python ≥ 3.11 (tested on 3.14) and Node ≥ 23 (tested on 24). The app's data is committed
(`app/backend/data/`), so the demo runs without the starter kit:

```bash
python3 -m venv .venv
.venv/bin/pip install -r app/requirements.txt
(cd app/frontend && npm install && npm run build)
echo "GEMINI_API_KEY=your-key" > app/.env      # optional; without it the texts come from templates
.venv/bin/uvicorn server:app --app-dir app/backend --port 8000
```

Open http://127.0.0.1:8000, sign in as the customer or the waste company (each in its own tab). "Reset the demo" on
the sign-in page clears the demo state. More in [`app/README.md`](app/README.md).

## Rebuild the numbers from the starter kit

1. Put the starter kit at `resources/Europress_SMART_Material_Value_Engine_v1.0.1/` (not in git: size, no licence
   file). Elsewhere, point to it with `FULLLOAD_KIT=/path/to/kit`.
2. Install and build:
   ```bash
   .venv/bin/pip install -e "resources/Europress_SMART_Material_Value_Engine_v1.0.1[dev]" -e "pipeline[dev]"
   .venv/bin/fullload build                       # → pipeline/out/bundle.json (~15 s; --data quickstart for a fast run)
   .venv/bin/python app/backend/build_data.py     # → app/backend/data/ (reads the bundle; asserts the invoice check agrees)
   ```

| Task | Command |
|---|---|
| Tests | `cd pipeline && ../.venv/bin/pytest` |
| Lint | `.venv/bin/ruff check pipeline` |
| Reproduce Part 1 numbers | `part1/scripts/reproduce.sh` (see `part1/README.md`) |

## Layout

```
pipeline/out/         bundle.json: every figure the app shows, with tag, formula and sources (committed)
pipeline/fullload/    Python package (internal name "fullload"): starter-kit data -> bundle.json
  config.py           paths (FULLLOAD_KIT, FULLLOAD_DATA), excluded materials
  kit.py              the only bridge to the starter kit
  figures.py          Figure: every number with tag, formula and sources
  fleet.py            fleet facts, shared invoice-charge helpers
  forecast.py         own-history vs peer forecast backtest
  trips.py            weight-triggered lifts
  premature.py        explainable premature-lift rule
  scorecard.py        operator service figures; invoice vs contract
  market.py           market before/after simulation
  customer.py         customer and operator views, contract check, AI-summarized report
  value.py            value per device, compared with the business team's figures
  pricing.py          the operator fee and Europress cash flow (docs/PRICING.md)
  virtual_scale.py    roadmap analysis: virtual scale for older units (not in the product claim)
  weighing.py         Part 1 numbers for the demo (installed cost, H7 statics), read from part1/
  validate.py         scores against dev labels (validation split only)
  params.yaml         every hypothetical assumption with its rationale
  reports/            AI-written report templates; numbers filled from the data and checked
app/                  THE DEMO: backend/ (FastAPI server, build_data.py, Gemini wording with a number guard), frontend/ (React)
docs/                 submission documents (business case, pricing, limitations, SMART integration, licences, script)
docs/fi/              superseded Finnish team working material (first business-case PDF, LIITE, papers, cash-flow
                      scripts); not a deliverable, see docs/fi/README.md
reviews/              independent reviews and the team briefing page
talks/                recordings and transcripts of the Europress talks (local only, not in git)
part1/                Part 1 weighing concept, calculations and figures
briefs/               briefs and reports of the supervised agents that built parts of this repo
```

## How the numbers stay honest

- Money is computed in integer cents with the starter kit's own pricing code; unknown mass is never imputed.
- Every displayed number carries an evidence tag (observed, estimated, simulated, hypothetical) and its sources.
- Dev labels are read only in `validate.py` (and could be in `pick_heroes.py`); a test enforces it. The app's
  `build_data.py` reads them only to evaluate its rules (validation split), never for a figure the customer sees.
  Test-period labels are never touched.
- The app never asks the language model for a number: a guard rejects any reply with a figure not in the facts.
- Builds are deterministic: the same inputs give a byte-identical bundle.
- The app's data build checks that its invoice figures equal the pipeline's.
