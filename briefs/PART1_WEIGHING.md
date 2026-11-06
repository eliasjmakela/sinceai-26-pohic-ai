# Agent brief: Part 1 — weighing concept

> Self-contained brief for an agent working on its own. A supervisor agent and the lead developer check the
> result against the **quality gates in §5**. Everything outside those gates is the agent's own judgement.

## 1. Mission
Produce the **Part 1 deliverable** of the Europress challenge: a short, illustrated weighing concept for getting an
affordable, sufficiently accurate weight at the compactor. Target level: **complete and decent, not deep.** Every
element the brief asks for must be present; depth beyond that is not wanted.

Read first:
- Challenge brief (sections 02, 04, 06, 07): `resources/Europress_SinceAI_2026_Challenge_Brief_BUILDER_FINAL (1).pdf` (`pdftotext -layout`)
- `PRODUCT.md` §1 ("Who pays, who uses"), §2 (kickoff constraints), §7.5 (Part 1 in the demo)
- Kickoff transcript `Röst 261106_182238.txt` (Whisper, imperfect): search for "pressure", "cheap", "accurate", "bio", "humidity"
- Starter kit `resources/Europress_SMART_Material_Value_Engine_v1.0.1/`: `README.md` (part 1 table), `docs/ASSUMPTIONS_AND_LIMITATIONS.md`,
  `docs/EUROPRESS_REVIEW.md` point 1.7, `configs/assumptions.yaml` (weighing section), `examples/weighing_accuracy_value.py`,
  `docs/DATA_DICTIONARY.md` (sensor_registry, telemetry_hourly, collection_events, weighbridge_tickets)

Decisions already made (do not reopen):
- **Chosen concept: T1 cheap strain gauges** on the frame / container rails + a low-cost amplifier on the SMART modem.
- Alternatives shown beside it: **T0 virtual weight** (existing hydraulic pressure + fill, €0 BOM, future software
  upgrade) and **T2 shear-beam load cells** (best accuracy, highest cost).
- Hardware is **free to the customer**, funded by Europress and paid back from operators' per-tonne fees.
- Europress is a technology company; it does not transport. Product name "FullLoad"; never put "SMART" in a product name.

## 2. Working rules
- Work on git branch **`part1-weighing`** (in its own worktree). Write **only** inside `part1/`. Do not modify
  `PRODUCT.md`, `TOMMI_QUESTIONS.md`, `briefs/`, `pipeline/`, `web/` or anything in `resources/`.
- `resources/` (starter kit + data, ~135 MB) and the transcript are **not tracked in git**, so they are missing from the
  worktree. Read them from the main checkout by absolute path: `/home/eliasjmakela/Documents/sinceai26-haaste/resources/…`
  and `/home/eliasjmakela/Documents/sinceai26-haaste/Röst 261106_182238.txt`. Scripts take the data root as an argument.
- Python: create `part1/.venv` and `pip install -e` the kit into it (see PRODUCT.md §7.2: import `europress_data` for data access via `sdk.open_dataset`; never edit the kit); record every package you install. Read data only from `data/*/public/`;
  **never** open `private_evaluation/`. `labels_dev/` only for clearly marked validation, never as an input.
- Use web search for component prices and sensor specs; cite every source.
- Timebox: about 4 hours of agent work. If a gate cannot be met, stop and report instead of working around it.
- Where an answer depends on Tommi (Europress) — accuracy target, BOM limit, pressure data, subsidy — write a
  `TOMMI:` marker with your assumption and continue. Questions 8–10b in `TOMMI_QUESTIONS.md`.

## 3. Deliverables (all under `part1/`)
| # | Path | Content |
|---|---|---|
| D1 | `part1/WEIGHING_CONCEPT.md` | The concept (≈ 4–6 pages): measurement principle, placement for **COMBI and DUO separately**, indicative BOM and cost per device (ranges), installation and retrofit steps and time, calibration (factory, on-site reference weights, in-service cross-check against shared weighbridge tickets, auto-zero after each lift), error sources and error budget, validation experiment, limitations, comparison table T0/T1/T2, a brief-coverage table (gate QG1), a human-review list (QG11) |
| D2 | `part1/figures/*.svg` (+ sources) | 2–4 illustrations: placement sketch per machine type, error-budget chart, accuracy→value chart, drift-detection chart. Self-made only (SVG / matplotlib / mermaid) |
| D3 | `part1/sigma_tiers.json` | Interface for the app (§4) |
| D4 | `part1/scripts/` + `part1/README.md` | Scripts that produce every data-derived number and figure; one command reproduces all of them |
| D5 | `part1/THIRD_PARTY_part1.md` | Rows to merge into `THIRD_PARTY.md`: every library, dataset, web source, tool used, with licence and commercial-use note |
| D6 | `part1/GATES_REPORT.md` | Self-check: one row per gate in §5 with PASS/FAIL and evidence (`file:line` or command output) |

## 4. Interface contract: `part1/sigma_tiers.json`
The app on `main` reads this file; until merge it uses a placeholder with the same shape. Do not change the shape.
```json
{
  "schema_version": 1,
  "chosen_tier": "T1",
  "tiers": [
    {
      "id": "T0 | T1 | T2",
      "name": "string",
      "principle": "one sentence",
      "sigma_rel_pct": {"low": 0.0, "mid": 0.0, "high": 0.0},
      "sigma_abs_kg": {"low": 0.0, "mid": 0.0, "high": 0.0},
      "bom_eur_per_device": {"low": 0, "high": 0},
      "install_hours": {"low": 0, "high": 0},
      "suits": ["COMBI", "DUO"],
      "weak_for": ["e.g. BIOWASTE"],
      "evidence_tag": "estimate | simulation_target | literature",
      "sources": ["[n] ids pointing to D1's reference list"]
    }
  ]
}
```

## 5. Quality gates (each must PASS; the supervisor checks every one)

| Gate | Rule | How to check |
|---|---|---|
| **QG1 Brief coverage** | D1 covers every item from the brief: sensor/measurement principle, placement, indicative BOM and cost, installation, retrofit potential, calibration, error sources, accuracy reasoning, limitations, validation plan/experiment. | D1 contains a coverage table mapping each item to a section; every row points to a non-empty section |
| **QG2 Sourced costs** | Every price, cost and supplier spec in D1 and D3 is a **range** with a citation `[n]` to a reference list (URL + access date). No uncited euro figures. Where no source exists: labelled "team estimate" with the reasoning. | grep every `€` in D1; each has `[n]` or "team estimate" within the same sentence; spot-check 3 URLs open |
| **QG3 No over-claiming** | The data does **not** prove hardware feasibility. Every accuracy figure is tagged *estimate*, *simulation target* or *literature*. The ±100 kg on a 3 t load figure is always called "the dataset's simulation target, not a Europress specification". Banned in D1: "proven", "validated" (except for the validation *plan*), "guaranteed", "certified accuracy", "Europress specification". | grep banned words; read every σ number in context |
| **QG4 Machine-type correctness** | Placement is described separately for **COMBI** (compactor and container joined, whole unit lifted and transported: the sensor travels with the unit and must survive lifting and road transport) and **DUO** (compactor stays on site, only the container is detached and emptied: the sensor sits on the stationary frame/rails and must weigh the container only and handle container exchange). Mechanical assumptions are listed in the human-review list. | Read both placement sections against these definitions (from the starter kit `START_HERE.md`) |
| **QG5 Reproducible data claims** | Every number derived from the dataset comes from a script in `part1/scripts/`; one documented command regenerates all numbers and figures; output is deterministic (fixed seeds); scripts read only `data/*/public/`. | Run the command twice; diff outputs; grep scripts for `private_evaluation` |
| **QG6 Interface valid** | `sigma_tiers.json` matches §4 exactly; its values match D1's comparison table; `chosen_tier` is `T1`. | Validate with a small script; compare to D1 table |
| **QG7 Consistent with PRODUCT.md** | T1 chosen, T0/T2 as alternatives; hardware free to customers; Europress never transports; name "FullLoad", no "SMART" in product names; nothing contradicts PRODUCT.md §1–2. | Read D1 against PRODUCT.md §1, §2, §7.5 |
| **QG8 Licences** | D5 lists every Python package, tool, dataset and web source used, with licence and commercial-use note. Figures are self-made; no copied images. | Compare D5 to `part1/.venv` package list and D1 references |
| **QG9 Scope respected** | No web UI work, no pressure-signal ML model, no hardware simulation beyond what a figure needs, no files outside `part1/`, timebox respected. | `git diff --stat main...part1-weighing` touches only `part1/` |
| **QG10 Limitations stated** | D1 has a limitations section naming at least: biowaste (little back-pressure, for T0), humidity/moisture changing weight, temperature drift, off-centre loads, the press cycle disturbing readings, and that everything is **untested**. | Read section |
| **QG11 Human-review list** | D1 ends with ≤ 10 concrete items a person with machine knowledge must confirm (e.g. "gauge position on DUO rails is feasible without frame modification"). | Read section |

## 6. Data-backed content (suggested, keep small)
- **Accuracy → value**: run or adapt `examples/weighing_accuracy_value.py` for σ per tier: share of 2.5–3.5 t loads
  within ±100 kg, €/t error, ability to detect a tonnage difference. One chart.
- **Calibration from shared tickets**: pair device weights with single-load, weighed-tare weighbridge tickets
  (`collection_events.operator_job_ref` ↔ `weighbridge_tickets`); show a rolling device/ticket ratio for one drifting
  device and one healthy device. One chart. This shows how cheap sensors stay honest in service.
- **Error budget** for T1: reading noise, temperature, calibration gain/offset, off-centre load, residue → combined σ
  (root-sum-square). One chart.

## 7. Final report
When done, reply with: the branch name, the list of files created, the `GATES_REPORT.md` table, all `TOMMI:` markers,
and the human-review list. Do not merge into `main`.

## 8. Supervisor checklist (for the reviewing agent and the lead developer)
1. `git diff --stat main...part1-weighing` → only `part1/` changed (QG9).
2. Open `GATES_REPORT.md`; for each gate, verify the evidence yourself — do not trust the self-check.
3. Run the reproduce command twice and diff (QG5).
4. grep D1 for `€` without `[n]`/"team estimate", and for banned words (QG2, QG3).
5. Validate `sigma_tiers.json` against §4 (QG6).
6. Read both placement sections (QG4) and the limitations section (QG10).
7. Hand the human-review list (QG11) to a teammate; list `TOMMI:` markers for the post-meeting adjustment pass.
8. Merge only after all gates pass and the teammate review is done.
