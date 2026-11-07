# Submission checklist (brief §07)

What the brief asks for, and which file answers it. Submit via Since AI by **Sun 8 Nov 09:30** (hard deadline
10:00). No physical prototype is required.

| Brief asks for | Our answer | Status |
|---|---|---|
| (1) Short illustrated weighing concept: principle, placement, indicative BOM and cost, installation, calibration, error sources, validation plan | `part1/WEIGHING_ONEPAGER.md` (with `part1/figures/h7_side_view.svg`); full detail in `part1/WEIGHING_CONCEPT.md` §19–20 | draft, text pass pending (E) |
| (2) Working software demo **or** recorded walkthrough using synthetic weight data | `web/` (three pitch screens + details); video recorded from `WALKTHROUGH_SCRIPT.md` | demo ready; video pending (E) |
| (2) Code / setup notes | `README.md` | ready |
| (2) Traceable economics | Every number is a Figure with tag, formula and sources (open any figure in the demo); `PRICING.md`, `pipeline/fullload/pricing.py`; `npm run parity` | ready |
| (2) Proposed SMART integration | `SMART_INTEGRATION.md`; Business detail screen | draft, text pass pending (E) |
| (3) Concise customer value and business case: use case, measurable customer benefit, commercial model for Europress, productisation in SMART | `BUSINESS_CASE.md` (English); the team's `OpenWeight.pdf` once the fixes in `reviews/OPENWEIGHT_PDF_FIXES.md` are applied | draft, text pass pending (E/T) |
| Every third-party library, model, dataset or service, its licence and commercial-use restrictions | `THIRD_PARTY.md`, `part1/THIRD_PARTY_part1.md` | ready |
| Assumptions and what remains untested | `LIMITATIONS.md`; "not proven" in every proposal payload | ready |

## Upload set

1. Link to the repository (or a zip of it without `resources/`, `node_modules/`, `.venv/`, `venv/`, audio files).
2. The walkthrough video file or link.
3. PDFs of: the weighing one-pager, the business case (or the fixed `OpenWeight.pdf`), and optionally the SMART
   integration note. A Markdown file prints to PDF from any Markdown viewer.

## Last checks (Claude, Sun morning)

- [ ] `.venv/bin/fullload build` gives a byte-identical bundle; tests, lint and parity pass.
- [ ] `git describe --tags` shows `demo-frozen` on the recorded build.
- [ ] After the text pass, re-run the number check (`reviews/FINAL_FACT_CHECK.md`) on the edited files.
- [ ] No starter-kit files, secrets or personal recordings in the upload.
