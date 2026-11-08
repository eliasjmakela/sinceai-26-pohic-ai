"""Export everything the hosted demo (app/cloudflare/) needs, computed by this server's own code.

The Cloudflare Worker re-implements only the small state machine (decisions, query, tender, toggles). Every text and
figure comes from here: the report, the invoice query, the offer rows and the offer summary, worded by Gemini where a
guarded reply exists (llm.py) and by the templates otherwise. So the hosted demo needs no Gemini key.
Run: .venv/bin/python app/backend/export_static.py   (after build_data.py)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import server  # noqa: E402

OUT = HERE.parent / "cloudflare" / "src" / "static.json"


def main() -> None:
    initial = json.loads(json.dumps(server.INITIAL))
    view = server.tender_view(initial)
    explain = server.get_explain(fast=False)
    static = {
        "initial": initial,
        "report": server.build_report(),
        "summary": server.build_summary(),
        "query_text": server.draft_query_text(),
        "offer_rows": view["rows"],
        "explain": explain,
        "customer": server.CUSTOMER, "hauler": server.HAULER, "pack": server.PACK, "notice": server.NOTICE, "about": server.ABOUT,
        "compactors": {c["id"]: json.loads((server.DATA / "compactors" / f"{c['id']}.json").read_text()) for c in server.CUSTOMER["compactors"]},
        "me": server.ME,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(static, ensure_ascii=False, separators=(",", ":")))
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB); report: {static['report']['source']}, explain: {explain['source']}")


if __name__ == "__main__":
    main()
