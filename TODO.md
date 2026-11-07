# Final submission TO-DO

Written Sat 7 Nov, ~20:00. Deadlines: **feature freeze Sat 22:00**, **demo frozen and walkthrough recorded Sun
00:00**, **submit Sun 09:30** (hard deadline 10:00). The single source of truth is `MASTER.md` (decisions, numbers
ledger, scoring map, deliverables). Fee reasoning: `PRICING.md`. PDF fixes: `reviews/OPENWEIGHT_PDF_FIXES.md`.

Owner key: **C** = Claude does it (or delegates to an agent and checks the result), **E** = Elias, **T** =
teammates. Status: `[ ]` open, `[~]` running, `[x]` done.

## Needs a human (Elias / teammates)

| # | What | Owner | By | Notes |
|---|---|---|---|---|
| H1 | **Ask Europress (Tommi / Discord):** (a) is ~€1,000 per unit realistic for the self-lift fitted at the factory (cylinder, valve section, pressure sensor)? (b) of the ~1,200 new compactors a year, how many are COMBI and how many DUO? | E | asap | Decides whether €30 pays back (`PRICING.md`). Ready-made questions: `part1/ENGINEER_QUESTIONS.md` 11–12, 15 |
| H2 | Send `reviews/OPENWEIGHT_PDF_FIXES.md` to the PDF's author, and agree the submission language (recommended: English, Finnish PDF as an annex) | E | 20:30 | MASTER §F8 |
| H3 | **Visual pass on the three pitch screens** (`#/beat-1` … `#/beat-3`): spacing, type sizes for a projector, colours, the H7 drawing, the ecosystem reveal | E | 22:00 | Claude can do a first pass with the design skill if you want; say so |
| H4 | **Text quality pass** (make it sound human): the on-screen copy of the three screens, `README.md`, `PRICING.md`, the weighing one-pager (C5), the business case (C6), `LIMITATIONS.md` | E | Sun 08:30 | Claude drafts; you edit. Keep numbers unchanged (or ask Claude to re-check after edits) |
| H5 | Pitch slides / presentation, if the format needs them | T | Sun 08:00 | Use only numbers from `MASTER.md` §C marked agreed |
| H6 | **Record the walkthrough video** (~4:30) from the frozen build, following the script (C8) | E | Sun 00:00 | `cd web && npm run build && npm run preview` |
| H7 | Dry run, timed, on the built demo; report bugs to Claude | T | 23:00 | |
| H8 | Final read and upload of the submission | E | Sun 09:30 | Checklist C11 |

## Claude does or delegates (no human needed)

| # | What | Owner | By | Status |
|---|---|---|---|---|
| C1 | Stale text cleanup across the repo (MASTER §G): PRODUCT, LIMITATIONS, README, Part 1 §0/§3/§17/§19.8, RED_TEAM R27, sigma_tiers, superseded notes | C (agent) | 21:00 | [~] |
| C2 | Merge the two-end lift (H7-2, from the team's "duo mechanism" sheet) into Part 1: §20, RED_TEAM R31–R38, ENGINEER_QUESTIONS 16–19, cost lines in `installed_cost.json`, scripts in `part1/calc/h7_2_*.py`. The sheet is a COMBI variant, not the DUO product; DUO stays on H1 / H5 | C | 21:15 | [ ] |
| C3 | **Independent fact-check** of every number on the three pitch screens, the detail screens, `PRICING.md`, the fix list and the one-pagers against `bundle.json` and the sources; report mismatches | C (agent) | 21:45 | [ ] |
| C4 | Demo freeze checks: `npm run build`, every screen opens with no console errors, arrow-key flow, offline (no network), phone-width sanity, receipts open on every figure | C | 22:00 | [ ] |
| C5 | **Weighing concept one-pager (deliverable 1, illustrated)**, English, H7-first: principle with the side-view drawing, placement on COMBI, BOM and installed cost, installation, calibration by weighbridge tickets, error budget, safety/CE, the two new risks, validation plan, DUO answer | C (draft) → E (text pass) | 22:30 | [ ] |
| C6 | **Business case and productisation (deliverable 3)** in English, from LIITE + `PRICING.md` with all fixes applied: who pays, €30 fee, cost gap and design-to-cost, adoption, pilot, sensitivity, roadmap (virtual scale for the older fleet) | C (draft) → E / T | 23:00 | [~] |
| C7 | **SMART integration note (deliverable 2e)**: data in (fill, cycles, H7 readings), out (forecasts, lift orders, customer reports), the `openweight.proposal.v1` and lift-order payloads, human approval | C | 23:00 | [ ] |
| C8 | Walkthrough script with timings and the exact clicks for H6 | C | 23:00 | [ ] |
| C9 | Tag `demo-frozen` at the frozen commit; build committed | C | Sun 00:00 | [ ] |
| C10 | Final repo hygiene: tests, lint, parity, determinism, `THIRD_PARTY.md` complete, no secrets, no `resources/` in git, README run commands verified from a clean clone | C | Sun 08:00 | [ ] |
| C11 | Submission checklist against the brief §07 (what file goes where), plus a last scan for stale numbers after the text pass (H4) | C | Sun 09:00 | [ ] |

## Done today (for reference)

- Three pitch screens; per-visit vs per-tonne evidence (3.4×); ecosystem reveal; H7 animation.
- H7 paper review, two new risks added; DUO sheet review (it is a two-end COMBI lift, H7-2).
- LIITE vs PDF check; fix list for the PDF's author.
- Fee decision **€30** with the team's cash-flow model reproduced (`PRICING.md`); market sim on the €30 fee
  (customer €/t −12 %).
- `MASTER.md`: one consolidated understanding of everything.

## Open risks to say out loud in the pitch

1. The self-lift must be built for about €1,000 or less, or €30 does not pay back (our estimate €800–2,370).
2. Operator willingness to pay €30 is untested; the case rests on winning per-kg tenders, not only fewer visits.
3. Nothing in the weighing is tested; all accuracy figures are estimates. Billing stays on the certified weighbridge.
