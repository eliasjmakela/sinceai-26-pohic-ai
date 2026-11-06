# CLAUDE.md

Hackathon project (Since AI 2026, Europress challenge). **`PRODUCT.md` is the north star**: read it before building
anything; scope, rules and the module map (§7.2) live there. Questions for Europress: `TOMMI_QUESTIONS.md`.

- Setup: `python3 -m venv .venv && .venv/bin/pip install -e resources/Europress_SMART_Material_Value_Engine_v1.0.1 -e "pipeline[dev]"`
- Build the demo bundle: `.venv/bin/fullload build` (`--data quickstart` for a fast run) → `web/public/data/bundle.json`
- Tests: `cd pipeline && ../.venv/bin/pytest`
- Never edit anything under `resources/` (the starter kit); reach kit internals only through `pipeline/fullload/kit.py`.

Side note: the user is the sole coder and is responsible for the code matching the spec. Keep them in the loop on
core code decisions (briefly say what you chose and why) rather than deciding architecture silently.
