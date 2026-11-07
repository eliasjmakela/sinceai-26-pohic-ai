# OpenWeight

Since AI Hackathon 2026 · Europress challenge "SMART Material Value Engine — Weigh at Source, Create Value".

**OpenWeight: pay for tonnes, not trips.** Customers pay per truck visit, and only the incumbent operator knows how
much each site produces, so challengers cannot price per kilo. OpenWeight puts the weight in the compactor and gives
every operator the same forecasts and verified weights. Operators pay Europress a service fee, customers use it free,
and billing stays on the operator's certified weighbridge. All data is synthetic and every price hypothetical.

| Document | What it is |
|---|---|
| [`PRODUCT.md`](PRODUCT.md) | The spec: thesis, decisions, demo storyline, scoring map, architecture, rules |
| [`LIMITATIONS.md`](LIMITATIONS.md) | Assumptions and what remains untested |
| [`THIRD_PARTY.md`](THIRD_PARTY.md) | Every library, dataset, tool and service with its licence |
| [`part1/WEIGHING_CONCEPT.md`](part1/WEIGHING_CONCEPT.md) | Part 1: the weighing concept, costed, with claims ledger and red team |
| [`reviews/`](reviews/) | Independent reviews and the team briefing page |

## Setup

Requires Python ≥ 3.11 (tested on 3.14) and Node ≥ 23 (tested on 24).

1. Put the starter kit at `resources/Europress_SMART_Material_Value_Engine_v1.0.1/` (not in git: size, no licence file).
2. Install:
   ```bash
   python3 -m venv .venv
   .venv/bin/pip install -e "resources/Europress_SMART_Material_Value_Engine_v1.0.1[dev]" -e "pipeline[dev]"
   (cd web && npm install)
   ```
   Elsewhere, point the pipeline at the kit with `FULLLOAD_KIT=/path/to/kit`.

## Run

| Task | Command |
|---|---|
| Build the demo data | `.venv/bin/fullload build` (competition pack, ~15 s) or `--data quickstart` |
| Run the demo | `cd web && npm run dev` (or `npm run build && npm run preview` for the offline build) |
| Tests | `cd pipeline && ../.venv/bin/pytest` |
| Lint | `.venv/bin/ruff check pipeline` and `cd web && npx oxlint src scripts` |
| Browser models match Python | `cd web && npm run parity` |
| Reproduce Part 1 numbers | `part1/scripts/reproduce.sh` (see `part1/README.md`) |

The demo reads one committed file, `web/public/data/bundle.json`, so it runs offline without Python.

## Layout

```
pipeline/fullload/    Python package (internal name "fullload"): starter-kit data -> bundle.json
  config.py           paths (FULLLOAD_KIT, FULLLOAD_DATA), excluded materials
  kit.py              the only bridge to the starter kit
  figures.py          Figure: every number with tag, formula and sources
  fleet.py            fleet facts, shared invoice-charge helpers
  forecast.py         own-history vs peer forecast backtest
  trips.py            weight-triggered lifts
  premature.py        explainable premature-lift rule
  scorecard.py        operator service figures; invoice vs contract
  market.py           market before/after simulation (mirrored in web/src/market/model.ts)
  customer.py         customer and operator views, contract check, AI-summarized report
  value.py            value per device, compared with the business team's figures
  business.py         Europress business model (mirrored in web/src/business/model.ts)
  virtual_scale.py    virtual scale accuracy and calibration learning curve
  weighing.py         Part 1 numbers for the demo (installed cost, H7 statics), read from part1/
  validate.py         scores against dev labels (validation split only)
  params.yaml         every hypothetical assumption with its rationale
  reports/            AI-written report templates; numbers filled from the data and checked
web/                  Vite + React + TypeScript demo: src/pitch/ (the three pitch screens), src/details/
part1/                Part 1 weighing concept, calculations and figures
briefs/               briefs and reports of the supervised agents that built parts of this repo
```

## How the numbers stay honest

- Money is computed in integer cents with the starter kit's own pricing code; unknown mass is never imputed.
- Every displayed number carries an evidence tag (observed, estimated, simulated, hypothetical) and its sources.
- Dev labels are read only in `validate.py` (and could be in `pick_heroes.py`); a test enforces it. Test-period labels
  are never touched.
- Builds are deterministic: the same inputs give a byte-identical bundle.
- The browser copies of the market and business models are checked against Python (`npm run parity`).
