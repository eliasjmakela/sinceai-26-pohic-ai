# Agent brief (DRAFT v2): weighing solution — find a defensible edge

> **Status: APPROVED 7 Nov. Filled from the talk with Tommi** (`Since.AI.2.txt`, Whisper, Finnish, noisy). Same
> supervised-gate approach as `briefs/PART1_WEIGHING.md`. Launch after the lead developer approves.

## 1. Why v2 (what Tommi said, 7 Nov)
- **Weight is the blocker for Europress.** Without it "we can't take the case to the end; we always stop halfway". He
  wants the pitch to show *how* we get the weight, pitched as if selling it to him, so Europress can take it forward.
- **Prior attempt: scale platforms** that the unit stands on already exist at Europress, but they are "almost as
  expensive" — too expensive to scale. Do not propose a platform scale under the whole unit as the main concept.
- **Price target**: a basic COMBI costs roughly €20–25k. A weighing option around **€2,000** extra came up as the order
  of magnitude customers would weigh against. Install cost is one-off, so lifecycle value matters more than the very
  lowest BOM — but sales sells on margin, so the lifecycle argument must be easy to explain.
- **Accuracy**: "doesn't need to be very accurate, but it must be cheap" (planning-grade; billing stays on the weighbridge).
- **Load cases that make whole-unit weighing hard**: up to ~5 t of waste, ~3 t machine, plus the forces when the truck
  pulls the unit up and lowers it. "Where would the sensor be?"
- **Tommi's own hint — weigh at the hopper, not the container.** In the compactor, waste first drops into the feed
  hopper (onto the ram or the hopper floor), then the ram pushes it into the container. Weigh each charge *at the
  hopper stage* and add up what has gone into the container. "How to make that work structurally is not trivial…
  we've thought about it ourselves… it was easier than the alternatives." This is the lead direction for v2.

## 2. Hypotheses to test (not conclusions)
1. **H1 Hopper-stage incremental weighing (lead).** Small, cheap load cells or strain sensing under the hopper floor /
   ram guide weigh each charge at rest before the ram stroke; the device sums charges. Advantages to test: small load
   range (a charge is ~10–30 kg; kit `materials.*.input_event_kg`), sensor isolated from container mass, machine mass
   and truck lifting forces, same design for COMBI and DUO. Risks to test: impact loads when waste is thrown in,
   material sticking/bridging, partial charges, ram friction, liquids (biowaste), error accumulation over hundreds of
   charges.
2. **H2 The fleet calibrates itself (our edge in software).** Per-charge random errors average out (√N), but a bias
   accumulates. Every shared weighbridge ticket is a free reference for the *sum* of charges since the last lift, so a
   per-device gain/bias can be estimated online (hierarchical / Bayesian: devices borrow strength from similar devices).
   Show the learning curve on the synthetic data: error of the container total vs number of tickets seen.
2b. **H5 Weighing guide rails (team idea, co-lead with H1).** Europress already sells guide rails as an accessory.
   Put 2 load cells under each of the two rails (4 × ~5 t shear-beam cells, IP68, summing box, amplifier into the SMART
   unit); the unit/container rests only on the rails, so the support points are defined and weight = sum of 4 cells.
   Cells stay on the ground: no transport, tipping or drops; set-down impacts handled by mechanical overload stops and
   cell capacity. Re-zero when the container/unit is away, tare when it returns empty. Team BOM estimate €520–800
   (to verify), plus one-off site work (level base, anchoring). To test:
   - **Which machine**: on a COMBI the whole unit (≈3 t machine + up to 5 t waste) leaves and returns; on a DUO only the
     container does. Check the rails carry the full weight in each case, and size the cells for the right total.
   - **Why is it cheaper than Europress's existing platform scales** ("almost as expensive" per Tommi)? Cost out the
     whole installed system (rail modification, lift-off and side restraint, overload stops, foundation, labour,
     calibration), not just the cells.
   - Set-down impact from the hook-lift, side loads when the unit is pulled on/off, frost heave, debris and ice under
     the rails, cable damage.
3. **H3 Fusion with what the compactor already measures** (ram pressure, ram position, fill %, compaction cycles):
   quantify how much each signal adds to H1, and whether pressure alone (T0) is a usable fallback.
4. **H4 Compare** H1 and H5 with the v1 tiers (T0 pressure-only, T1 frame/rail strain gauges, T2 load cells under the unit,
   and the existing platform scale) on cost, accuracy after calibration, COMBI/DUO fit, retrofit vs factory-fit,
   durability. Recommend one, with the €2k order of magnitude as the cost reference.

5. **H6 Full installed cost (required for every candidate).** Not just the BOM: per device, cost out sensors,
   electronics, mechanical parts (brackets, rail modification, overload stops, lift-off and side restraint),
   site work (levelling, anchoring, cabling), labour hours × rate, calibration and commissioning, and expected
   maintenance / replacement over a 6-year lease. Separate **retrofit** and **factory-fit** (new unit) costs, and give
   ranges with sources or labelled team estimates. Compare against the ~€2k reference and the existing platform
   scales. This table is a headline output: it feeds the business-case payback.

## 3. Working method (the team has no mechanical-engineering expertise)
- **Mechanism first**: describe the compactor's feed cycle (hopper, ram stroke, container) from public sources
  (manufacturer material, patents) before designing; mark anything assumed.
- **Claims ledger**: every technical claim (charge masses, impact forces, strain levels, temperature coefficients,
  prices, survivability) with source, confidence (high/medium/low) and how an engineer would check it.
- **First-principles calculations with shown working** (small scripts): impact force of a thrown charge vs static
  weight, load-cell range and overload protection, error accumulation over a container fill, temperature error.
- **Prior art**: patents and products for compactor / hopper / hook-lift / refuse-truck weighing; position H1 + H2
  against them. No novelty claim without this check.
- **Red-team pass**: a separate review step tries to break the design (frost, wet cardboard, biowaste, overloads,
  vandalism, COMBI transport) and the design is revised or the risk accepted explicitly.
- **Questions for an engineer**: ≤ 10 questions we can put to Tommi / a Europress engineer on Discord.

## 4. Deliverables (new branch `weighing-v2`, from `part1-weighing`)
- `part1/WEIGHING_CONCEPT.md` revised: H1 as the main concept if it survives, "Our edge" section (H1 + H2), prior-art
  table, comparison (H4), and the pitch-ready one-page summary Tommi asked for.
- `part1/calc/`: first-principles calculation scripts.
- `part1/scripts/`: charge-summing error model, self-calibration learning curve, fusion analysis; figures.
- `part1/CLAIMS_LEDGER.md`, `part1/RED_TEAM.md`, `part1/ENGINEER_QUESTIONS.md`.
- `sigma_tiers.json`: keep the schema; add the hopper tier (e.g. `id: "H1"`); bump `schema_version` only with the
  lead developer's agreement.

## 5. Quality gates
All v1 gates (QG1–QG11 in `briefs/PART1_WEIGHING.md`) still apply, plus:
| Gate | Rule | How to check |
|---|---|---|
| WG1 Claims ledger | Every numeric technical claim in D1 is in the ledger with source and confidence | sample 10 numbers from D1, find each in the ledger |
| WG2 Shown working | Every engineering number comes from a script in `part1/calc/` or a cited source | grep D1 numbers vs calc outputs |
| WG3 Edge is measured | H2's benefit is a reproducible analysis with stated assumptions (synthetic data) | rerun; read assumptions |
| WG4 Red team done | `RED_TEAM.md` lists ≥ 8 failure modes, each addressed or explicitly accepted | read |
| WG5 Prior art | ≥ 5 relevant prior-art items with links and how ours differs | open 3 links |
| WG6 Honest novelty | No novelty claim without WG5 behind it; Tommi's hopper idea credited to Europress | read |
| WG7 Platform scale | The existing platform-scale approach is in the comparison, with why H1/H5 differ | read |
| WG8 Installed cost | Every candidate has a full installed-cost table (all H6 lines, retrofit and factory-fit, ranges, each line sourced or labelled team estimate) | read; check no line is missing |

## 6. Open before launch
- Lead developer approves direction (H1 hopper and H5 weighing rails as co-leads, H2 as our software edge) and
  timebox (proposal: ~4 h).
- Ask Tommi on Discord: why are the existing platform scales expensive, and do the guide rails carry the full
  weight of the unit/container?
- Decide demo impact: beat 1 grows from 30 s (PRODUCT.md §4).
