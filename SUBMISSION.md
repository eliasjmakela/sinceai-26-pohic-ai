# Submission checklist (brief §07)

What the brief asks for, and which file answers it. Submit via Since AI by **Sun 8 Nov 09:30** (hard deadline
10:00). No physical prototype is required.

| Brief asks for | Our answer | Status |
|---|---|---|
| (1) Short illustrated weighing concept: principle, placement, indicative BOM and cost, installation, calibration, error sources, validation plan | `part1/WEIGHING_ONEPAGER.md` (with `part1/figures/h7_side_view.svg`); full detail in `part1/WEIGHING_CONCEPT.md` §19–20 | draft, text pass pending (E) |
| (2) Working software demo **or** recorded walkthrough using synthetic weight data | **Live: https://openweight.eliasmakela.fi**; code `app/` (customer and waste company portals; run steps in `README.md` and `app/README.md`; data committed, no starter kit needed) | demo ready; video being recorded (E) |
| (2) Code / setup notes | `README.md` (deliverables map, run the demo, rebuild from the kit), `app/README.md` | ready |
| (2) Traceable economics | In the app every figure opens its calculation and every pickup traces order → ticket → contract version → invoice lines; in the pipeline every number is a Figure with tag, formula and sources; `docs/PRICING.md`, `pipeline/fullload/pricing.py` | ready |
| (2) Proposed SMART integration | `docs/SMART_INTEGRATION.md` | draft, text pass pending (E) |
| (3) Concise customer value and business case: use case, measurable customer benefit, commercial model for Europress, productisation in SMART | `docs/BUSINESS_CASE.md` (English); the team's Finnish `docs/fi/OpenWeight.pdf` is team working material only (not submitted; superseded, see `docs/fi/README.md`) | draft, text pass pending (E/T) |
| Every third-party library, model, dataset or service, its licence and commercial-use restrictions | `docs/THIRD_PARTY.md`, `part1/THIRD_PARTY_part1.md` | ready |
| Assumptions and what remains untested | `docs/LIMITATIONS.md`; "not proven" in every proposal payload | ready |

## Upload set

1. Link to the repository (or a zip of it without `resources/`, `node_modules/`, `.venv/`, `venv/`, `talks/`, `app/.env`, `app/backend/state.db`).
2. The walkthrough video file or link.
3. PDFs of: the weighing one-pager, the business case, and optionally the SMART
   integration note. A Markdown file prints to PDF from any Markdown viewer.

## Last checks (Claude, Sun morning)

- [ ] `.venv/bin/fullload build` gives a byte-identical bundle; tests, lint and parity pass.
- [ ] `git describe --tags` shows `demo-frozen` on the recorded build.
- [ ] After the text pass, re-run the number check (`reviews/FINAL_FACT_CHECK.md`) on the edited files.
- [ ] `.venv/bin/python app/backend/build_data.py` runs (its invoice check equals the pipeline's), the app builds and both portals open.
- [ ] No starter-kit files, secrets (`app/.env` holds a Gemini key) or personal recordings in the upload.
