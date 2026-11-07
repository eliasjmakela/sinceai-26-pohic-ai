"""OpenWeight demo API: two separate portals over one shared tender.

Portal separation is enforced here, not in the browser. The waste company endpoints never return the customer's
prices, invoices or choice, and the bid pack is refused once the customer withdraws its weights. The demo starts with
one open tender and the weights shared.
OpenWeight does not relay offers (Europress does not want to sit in the middle of a tender): the waste company plans its
price here and sends it the usual way, and the customer compares the offers it received and uploaded.
This is a demo: there is no login, so the portal is chosen by URL.

Run: .venv/bin/uvicorn server:app --app-dir app/backend --port 8000
"""
from __future__ import annotations

import json
import logging
import re
import sqlite3
import threading
import time
from pathlib import Path

import llm
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
DIST = HERE.parent / "frontend" / "dist"
DB = HERE / "state.db"
log_ = logging.getLogger("openweight")

CUSTOMER = json.loads((DATA / "customer.json").read_text())
HAULER = json.loads((DATA / "hauler.json").read_text())
PACK = json.loads((DATA / "pack.json").read_text())
NOTICE = json.loads((DATA / "notice.json").read_text())
ABOUT = json.loads((DATA / "about.json").read_text())
ME = HAULER["operator"]["id"]

app = FastAPI(title="OpenWeight demo")
_lock = threading.Lock()
INITIAL = {"recommended": False, "confirmed": [], "checked": [], "decisions": {}, "query": {"status": "none", "text": None, "sent_at": None},
           "tender": {"status": "open", "consent": True, "awarded": None, "log": [{"at": "", "who": "You", "text": "Opened this tender with your weights shared."}]}, "report": None}


def _db() -> sqlite3.Connection:
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS state (id INTEGER PRIMARY KEY CHECK (id = 1), body TEXT NOT NULL)")
    return con


def load() -> dict:
    with _db() as con:
        row = con.execute("SELECT body FROM state WHERE id = 1").fetchone()
    state = json.loads(row[0]) if row else json.loads(json.dumps(INITIAL))
    if "query" not in state or state["tender"].get("status") == "none":
        return json.loads(json.dumps(INITIAL))
    for key in ("confirmed", "checked"):
        state.setdefault(key, [])
    state["tender"].pop("bid", None)  # older state from when the waste company could send an offer here
    return state


def save(state: dict) -> None:
    with _db() as con:
        con.execute("INSERT OR REPLACE INTO state (id, body) VALUES (1, ?)", (json.dumps(state),))


def note(state: dict, who: str, text: str) -> None:
    state["tender"]["log"].insert(0, {"at": time.strftime("%H:%M"), "who": who, "text": text})


def nice_date(iso: str) -> str:
    return time.strftime("%-d %b %Y", time.strptime(iso, "%Y-%m-%d"))


def whole(v: float) -> str:
    """Whole euros, rounding halves up, so server text matches the browser."""
    return f"{int(v + 0.5):,}"


# ---- the three-item report --------------------------------------------------------------------------------------------
def report_items() -> list[dict]:
    """The monthly report: fixed templates filled from the data. Gemini may reword the body (number-guarded)."""
    f, sv, m, bands, ic, r = CUSTOMER["facts"], CUSTOMER["service"], CUSTOMER["market"], CUSTOMER["bands"], CUSTOMER["invoice_check"], CUSTOMER["response"]
    company = CUSTOMER["operator"]
    notice = CUSTOMER.get("next_notice")
    return [
        {"id": "trips", "figure": f"{f['low_fill_share_pct']:.0f} %", "figure_label": "of pickups under 60 % full", "evidence": None,
         "headline": "Pickups before the container is full",
         "body": f"{f['low_fill_lifts']} of {f['lifts']} pickups were under 60 % full. Cost per tonne: €{bands[0]['eur_per_t']:.0f} under 60 % full, €{bands[2]['eur_per_t']:.0f} at 90 % or more. Ordering by weight: {f['lifts_after']}–{f['lifts_after_lower']} pickups a year.",
         "calc": [f"Pickups under 60 % full: {f['low_fill_lifts']} of {f['lifts']}"] + [f"{b['label']}: {b['pickups']} pickups, €{b['eur_per_pickup']:.0f} per pickup, €{b['eur_per_t']:.0f} per tonne" for b in bands] + [f"Flagged as early: {f['flagged_lifts']} pickups, €{whole(CUSTOMER['early_eur'])}", "SMART still orders a pickup if waiting would break hygiene limits or overflow."],
         "action": {"id": "order-by-weight", "kind": "approve", "label": "Order by weight", "done": "Ordering by weight", "reversal": "You can switch back at any time."}, "link": "/customer/contract"},
        {"id": "contract", "figure": f"{r['within'] / r['orders'] * 100:.0f} %", "figure_label": f"of orders within {r['hours']} h", "evidence": "assumption",
         "headline": "Contract follow-up",
         "body": f"Orders within {r['hours']} h: {r['within']} of {r['orders']}. Missed visits: {sv['missed_visits']}. Invoice lines differing from the contract: {ic['lines_differing']} of {ic['lines_total']}, €{whole(ic['above_eur'])} above.",
         "calc": [f"Orders within {r['hours']} h: {r['within']} of {r['orders']}, median {r['median_h']:.0f} h, longest {r['longest_h']:.0f} h", f"On schedule (±2 h): {sv['on_time_share_pct']} % of {sv['lifts']} pickups", f"Missed visits: {sv['missed_visits']}", f"Weighing tickets shared within 7 days: {sv['tickets_shared_share_pct']} %", f"Invoice lines differing: {ic['lines_differing']} of {ic['lines_total']}", f"Above the contract: €{ic['above_eur']:,.2f}. Below: €{ic['below_eur']:,.2f}", f"Different job reference on the invoice: {ic['mistyped_refs']} pickups, amounts match"],
         "action": {"id": "query", "kind": "query", "label": f"Send a query to {company}", "reversal": ""}, "link": "/customer/contract"},
        {"id": "tender", "figure": f"−€{whole(m['saving_eur'])}", "figure_label": "a year", "evidence": "simulated",
         "headline": "Tender per tonne",
         "body": f"Estimated cost with a price per tonne: €{whole(m['price_after_eur'])} a year, against €{whole(m['today_eur'])} today. Regional average: −{m['region_saving_pct']:.0f} %.",
         "calc": [f"Today: €{whole(m['today_eur'])} a year, €{m['today_price_t']:.1f} per tonne (pickups, transport, treatment)", f"Per tonne: €{whole(m['price_after_eur'])} a year, −{m['saving_pct']} %", "Market simulation on synthetic data"],
         "action": {"id": "tender", "kind": "link", "label": "Compare offers", "to": "/customer/tender", "reversal": (f"Next notice date: {nice_date(notice['date'])}, {notice['name']}" if notice else "")}, "link": "/customer/tender"},
    ]


REPORT_SCHEMA = {"type": "object", "properties": {"items": {"type": "array", "items": {"type": "object", "properties": {"id": {"type": "string"}, "body": {"type": "string"}}, "required": ["id", "body"]}}}, "required": ["items"]}


REPORT_PROMPT = "Rewrite each item's body as a short plain summary for a busy property manager, at most 2 sentences. Keep the exact meaning of the original: keep every comparison as it is, and keep today's facts clearly apart from simulated figures. Keep every id. Do not rewrite the headline."


def report_facts(items: list[dict]) -> dict:
    return {"items": [{k: i[k] for k in ("id", "headline", "body", "calc")} for i in items], "company": CUSTOMER["operator"]}


def build_report() -> dict:
    items = report_items()
    text, reason = llm.guarded(REPORT_PROMPT, report_facts(items), REPORT_SCHEMA)
    source = "template"
    if text:
        try:
            wording = {w["id"]: w for w in json.loads(text)["items"]}
            if set(wording) == {i["id"] for i in items}:
                for i in items:
                    i["body"] = wording[i["id"]]["body"]
                source = "gemini"
            else:
                reason = "item ids changed"
        except (json.JSONDecodeError, KeyError, TypeError):
            reason = "reply was not valid JSON"
    if source != "gemini":
        log_.warning("report from template: %s", reason)
    return {"source": source, "month": CUSTOMER["as_of"][:7], "items": items}


# ---- the invoice query -------------------------------------------------------------------------------------------------
def query_facts() -> dict:
    q = CUSTOMER["query"]
    ic = CUSTOMER["invoice_check"]
    return {"company": q["operator"], "total_to_check_eur": round(q["total_eur"], 2), "above_contract_eur": round(ic["above_eur"], 2),
            "invoice_differences_eur": round(q["invoice_eur"], 2), "late_overflow_charges_eur": round(q["surcharge_eur"], 2), "truck_tare_eur": round(q["tare_eur"], 2),
            "items": [{"date": i["date"], "site": i["site"], "material": i["material"], "detail": i["detail"], "eur": round(i["eur"], 2)} for i in q["items"][:8]], "shown": min(8, len(q["items"])), "total_listed": len(q["items"])}


def query_template(f: dict) -> str:
    rows = "\n".join(f"- {i['date']}, {i['site']}, {i['material'].lower()}: {i['detail']}" for i in f["items"])
    return (f"Hello {f['company']},\n\nWhen comparing this year's invoices with our contract, we found lines that differ from the agreed terms, about €{f['above_contract_eur']:,.2f} above them in total"
            + (f", and €{f['late_overflow_charges_eur']:,.2f} of overflow charges on pickups that came late" if f["late_overflow_charges_eur"] else "") + ". "
            f"The largest are below.\n\n{rows}\n\nThere may be a good reason, such as a reschedule or an access problem. Could you check these and let us know? Thank you.")


# ---- models ---------------------------------------------------------------------------------------------------------
class Decision(BaseModel):
    id: str = Field(max_length=60)
    decision: str | None = Field(default=None, pattern="^(approved|not_now)$")


class Consent(BaseModel):
    granted: bool


class Award(BaseModel):
    offer_id: str = Field(max_length=60)


class QueryText(BaseModel):
    text: str = Field(min_length=10, max_length=5000)


# ---- common ---------------------------------------------------------------------------------------------------------
@app.get("/api/about")
def get_about():
    """Public facts for the sign-in page: the market simulation's headline, nothing about one customer."""
    return ABOUT


@app.post("/api/demo/reset")
def reset():
    with _lock:
        save(json.loads(json.dumps(INITIAL)))
    return {"ok": True}


# ---- customer ---------------------------------------------------------------------------------------------------------
@app.get("/api/customer")
def get_customer():
    state = load()
    return CUSTOMER | {"decisions": state["decisions"], "query_state": state["query"], "tender_status": state["tender"]["status"]}


def template_report() -> dict:
    return {"source": "template", "month": CUSTOMER["as_of"][:7], "items": report_items()}


_wording = False


def upgrade_report() -> None:
    """Word the report with Gemini once, in the background, so the first view never waits for a model."""
    global _wording
    try:
        report = build_report()
        if report["source"] == "gemini":
            with _lock:
                state = load()
                if state.get("report") and state["report"]["source"] == "template":
                    state["report"] = report
                    save(state)
    finally:
        _wording = False


@app.get("/api/customer/report")
def get_report():
    """Asking for the report never costs anything by itself: Gemini is used at most once per distinct content."""
    global _wording
    with _lock:
        state = load()
        if not state.get("report"):
            known = llm.cached(REPORT_PROMPT, report_facts(report_items()), REPORT_SCHEMA) is not None
            state["report"] = build_report() if known else template_report()
            save(state)
            if not known and llm.api_key() and not _wording:
                _wording = True
                threading.Thread(target=upgrade_report, daemon=True).start()
    return state["report"] | {"pending": _wording}


@app.post("/api/customer/decisions")
def post_decision(body: Decision):
    with _lock:
        state = load()
        if body.decision is None:
            state["decisions"].pop(body.id, None)
        else:
            state["decisions"][body.id] = body.decision
        save(state)
    return state["decisions"]


@app.post("/api/customer/query/draft")
def post_query_draft():
    facts = query_facts()
    text, reason = llm.guarded("Write a short, polite message from the customer to the waste company asking it to check these invoice differences and charges. Keep the amount above the contract (above_contract_eur) apart from the overflow charges; do not add them up. Plain text, no subject line, at most 120 words plus the list of items. Neutral: there may be a good reason. Quote dates and amounts as given.", facts)
    if not text:
        log_.warning("query from template: %s", reason)
    with _lock:
        state = load()
        state["query"] = {"status": "draft", "text": text or query_template(facts), "sent_at": None}
        save(state)
    return state["query"]


@app.post("/api/customer/query/send")
def post_query_send(body: QueryText):
    with _lock:
        state = load()
        state["query"] = {"status": "sent", "text": body.text, "sent_at": time.strftime("%Y-%m-%d %H:%M")}
        save(state)
    return state["query"]


@app.post("/api/customer/query/cancel")
def post_query_cancel():
    with _lock:
        state = load()
        state["query"] = {"status": "none", "text": None, "sent_at": None}
        save(state)
    return state["query"]


def tender_view(state: dict) -> dict:
    t = state["tender"]
    m = CUSTOMER["market"]
    rows = [dict(o) for o in (CUSTOMER["offers"] if t["status"] != "none" else [])]
    for r in rows:
        c = CUSTOMER["cards"].get(r["operator_id"], {})
        r |= {"saving_eur": m["saving_eur"] + m["price_after_eur"] - r["annual_eur"],  # anchored to the report's saving (unrounded today)
               "on_time_pct": c.get("on_time_pct"), "tickets_pct": c.get("tickets_pct"), "billed_above_pct": c.get("billed_above_pct"), "response_h": c.get("response_h")}
    rows.sort(key=lambda r: (round(r["annual_eur"]), not r.get("model_winner")))  # a tie goes to the market model's winner
    return t | {"rows": rows}


@app.get("/api/customer/tender")
def get_tender():
    return tender_view(load())


@app.post("/api/customer/tender/consent")
def post_consent(body: Consent):
    with _lock:
        state = load()
        t = state["tender"]
        if body.granted:
            t.update(status="open" if t["status"] == "none" else t["status"], consent=True)
            note(state, "You", "Started the tender and allowed bidders to see the weight profile.")
        else:
            t.update(consent=False)
            note(state, "You", "Withdrew consent. Bidders can no longer open the weight profile.")
        save(state)
    return tender_view(state)


@app.post("/api/customer/tender/award")
def post_award(body: Award):
    with _lock:
        state = load()
        row = next((r for r in tender_view(state)["rows"] if r["id"] == body.offer_id), None)
        if row is None:
            raise HTTPException(404, "Unknown offer")
        state["tender"].update(status="awarded", awarded=body.offer_id)
        note(state, "You", f"Chose {row['operator']}.")
        save(state)
    return tender_view(state)


@app.post("/api/customer/tender/reopen")
def post_reopen():
    with _lock:
        state = load()
        state["tender"].update(status="open", awarded=None)
        note(state, "You", "Undid the choice. The tender is open again.")
        save(state)
    return tender_view(state)


EXPLAIN_PROMPT = "In one sentence of at most 28 words, name the trade-off between the lowest price and the best on-time record. Do not list every company. Quote figures as given, never state a difference between figures, and do not pick a winner."


@app.get("/api/customer/tender/explain")
def get_explain(fast: bool = False):
    rows = tender_view(load())["rows"]
    if not rows:
        return {"text": None, "source": "template"}
    lowest = rows[0]
    punctual = max((r for r in rows if r.get("on_time_pct") is not None), key=lambda r: r["on_time_pct"])
    tied = [r for r in rows if round(r["annual_eur"]) == round(lowest["annual_eur"])]
    who = " and ".join(r["operator"] for r in tied)
    template = f"{who} {'are' if len(tied) > 1 else 'is'} lowest at €{whole(lowest['annual_eur'])} a year. "
    template += ("It also has the best on-time record here, " + f"{punctual['on_time_pct']:.0f} %." if punctual["id"] == lowest["id"] and len(tied) == 1 else f"{punctual['operator']} has the best on-time record, {punctual['on_time_pct']:.0f} %.")
    facts = [{"company": r["operator"], "price_per_tonne_eur": round(r["price_eur_t"], 2), "annual_eur": round(r["annual_eur"]), "saving_against_today_eur": round(r["saving_eur"]), "on_time_pct": None if r["on_time_pct"] is None else round(r["on_time_pct"]), "records_shared_pct": None if r["tickets_pct"] is None else round(r["tickets_pct"])} for r in rows]
    if fast and llm.cached(EXPLAIN_PROMPT, facts) is None:
        return {"text": template, "source": "template"}
    text, reason = llm.guarded(EXPLAIN_PROMPT, facts)
    return {"text": text or template, "source": "gemini" if text else "template"}


@app.get("/api/customer/compactors/{device_id}")
def get_compactor(device_id: str):
    if not re.fullmatch(r"CMP-\d{5}", device_id) or device_id not in {c["id"] for c in CUSTOMER["compactors"]}:
        raise HTTPException(404, "Unknown compactor")
    return json.loads((DATA / "compactors" / f"{device_id}.json").read_text())


# ---- waste company ---------------------------------------------------------------------------------------------------
@app.get("/api/hauler")
def get_hauler():
    state = load()
    return HAULER | {"recommended": state.get("recommended", False), "confirmed": state["confirmed"], "checked": state["checked"]}


@app.get("/api/hauler/tender")
def get_hauler_tender():
    """The tender request the waste company uploaded. Whether the customer has chosen is not its business here."""
    t = load()["tender"]
    return {"notice": NOTICE, "consent": t["consent"], "my_record": CUSTOMER["cards"].get(ME)}


@app.get("/api/hauler/tender/pack")
def get_pack():
    t = load()["tender"]
    if not t["consent"]:
        raise HTTPException(403, "The customer has withdrawn its weights")
    return PACK


class Recommend(BaseModel):
    on: bool


class Toggle(BaseModel):
    id: str = Field(max_length=40)
    on: bool


def toggle(key: str, valid: set[str], body: Toggle) -> list[str]:
    if body.id not in valid:
        raise HTTPException(404, "Unknown item")
    with _lock:
        state = load()
        items = [i for i in state[key] if i != body.id]
        state[key] = items + [body.id] if body.on else items
        save(state)
    return state[key]


@app.post("/api/hauler/pickups")
def post_pickup(body: Toggle):
    return toggle("confirmed", {x["id"] for x in HAULER["fleet"]}, body)


@app.post("/api/hauler/trucks")
def post_truck(body: Toggle):
    return toggle("checked", {t["truck"] for t in HAULER["trucks"]}, body)


@app.post("/api/hauler/recommend")
def post_recommend(body: Recommend):
    with _lock:
        state = load()
        state["recommended"] = body.on
        save(state)
    return {"recommended": body.on}


# ---- frontend ---------------------------------------------------------------------------------------------------------
if (DIST / "assets").exists():
    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")


@app.get("/{path:path}", include_in_schema=False)
def spa(path: str):
    if path.startswith("api/"):
        raise HTTPException(404, "Unknown API path")
    index = DIST / "index.html"
    if not index.exists():
        raise HTTPException(503, "Frontend not built. Run: npm run build (in app/frontend)")
    return FileResponse(index)
