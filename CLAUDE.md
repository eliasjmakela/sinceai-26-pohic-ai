# CLAUDE.md

Hackathon project (Since AI 2026, Europress challenge). **`PRODUCT.md` is the north star**: read it before building
anything; scope, rules and the module map (§7.2) live there. Questions for Europress: `docs/TOMMI_QUESTIONS.md`.

- Setup: `python3 -m venv .venv && .venv/bin/pip install -e "resources/Europress_SMART_Material_Value_Engine_v1.0.1[dev]" -e "pipeline[dev]"` (the kit's `[dev]` extra brings scikit-learn for the ML baseline)
- Build the demo bundle: `.venv/bin/fullload build` (`--data quickstart` for a fast run) → `pipeline/out/bundle.json` (the app's data source; there is no other frontend)
- Product demo (`app/`): `.venv/bin/pip install -r app/requirements.txt`; data `.venv/bin/python app/backend/build_data.py` (reads the bundle, so rebuild it after `fullload build`); run `(cd app/frontend && npm run build)` then `.venv/bin/uvicorn server:app --app-dir app/backend --port 8000`
- Tests: `cd pipeline && ../.venv/bin/pytest`
- Never edit anything under `resources/` (the starter kit); reach kit internals only through `pipeline/fullload/kit.py` (the app's `build_data.py` does too).
- OpenWeight never relays offers between a waste company and a customer (Europress stays out of the tender): planning on one side, comparison of uploaded offers on the other.

Side note: the user is the sole coder and is responsible for the code matching the spec. Keep them in the loop on
core code decisions (briefly say what you chose and why) rather than deciding architecture silently.
