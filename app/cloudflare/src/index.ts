/**
 * OpenWeight demo on Cloudflare: the same API as app/backend/server.py, for the hosted demo.
 *
 * Every figure and text comes from app/backend (export_static.py writes static.json with the server's own code).
 * This Worker only keeps each visitor's demo state (decisions, invoice query, tender choice, consent, confirmed
 * pickups) in a Durable Object per browser session, and enforces the same portal separation: the waste company
 * endpoints never return the customer's prices, invoices or choice, and the bid pack is refused once the customer
 * withdraws its weights. No language model is called at runtime.
 */
import { DurableObject } from "cloudflare:workers";
import S from "./static.json";

type Json = any;
type State = Json;
const clone = <T>(v: T): T => JSON.parse(JSON.stringify(v));

export class Session extends DurableObject<Env> {
  async load(): Promise<State> {
    return (await this.ctx.storage.get<State>("state")) ?? clone(S.initial);
  }
  async save(state: State): Promise<void> {
    await this.ctx.storage.put("state", state);
  }
}

const json = (body: unknown, status = 200, headers: HeadersInit = {}) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json", "cache-control": "no-store", ...headers } });
const fail = (status: number, detail: string) => json({ detail }, status);

function note(state: State, who: string, text: string) {
  const t = new Date().toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", timeZone: "Europe/Helsinki" });
  state.tender.log.unshift({ at: t, who, text });
}

function tenderView(state: State) {
  const t = state.tender;
  return { ...t, rows: t.status !== "none" ? S.offer_rows : [] };
}

function toggle(state: State, key: "confirmed" | "checked", valid: Set<string>, body: Json) {
  if (typeof body?.id !== "string" || !valid.has(body.id)) return null;
  const items = (state[key] as string[]).filter((i) => i !== body.id);
  state[key] = body.on ? [...items, body.id] : items;
  return state[key];
}

type Store = { load(): Promise<State>; save(state: State): Promise<void> };

async function api(req: Request, url: URL, stub: Store): Promise<Response> {
  const p = url.pathname, method = req.method;
  const body: Json = method === "POST" ? await req.json().catch(() => ({})) : null;
  const state = await stub.load();
  const done = async (out: unknown) => { await stub.save(state); return json(out); };

  if (p === "/api/about" && method === "GET") return json(S.about);
  if (p === "/api/demo/reset" && method === "POST") { await stub.save(clone(S.initial)); return json({ ok: true }); }

  // ---- customer
  if (p === "/api/customer" && method === "GET")
    return json({ ...S.customer, decisions: state.decisions, query_state: state.query, tender_status: state.tender.status });
  if (p === "/api/customer/report" && method === "GET") {
    if (!state.report) { state.report = S.report; await stub.save(state); }
    return json({ ...state.report, pending: false });
  }
  if (p === "/api/customer/summary" && method === "GET") return json(S.summary);
  if (p === "/api/customer/decisions" && method === "POST") {
    if (typeof body.id !== "string" || body.id.length > 60) return fail(422, "Invalid decision");
    if (body.decision == null) delete state.decisions[body.id];
    else if (body.decision === "approved" || body.decision === "not_now") state.decisions[body.id] = body.decision;
    else return fail(422, "Invalid decision");
    return done(state.decisions);
  }
  if (p === "/api/customer/query/draft" && method === "POST") { state.query = { status: "draft", text: S.query_text, sent_at: null }; return done(state.query); }
  if (p === "/api/customer/query/send" && method === "POST") {
    if (typeof body.text !== "string" || body.text.length < 10 || body.text.length > 5000) return fail(422, "The message must be 10–5,000 characters");
    state.query = { status: "sent", text: body.text, sent_at: new Date().toISOString().slice(0, 16).replace("T", " ") };
    return done(state.query);
  }
  if (p === "/api/customer/query/cancel" && method === "POST") { state.query = { status: "none", text: null, sent_at: null }; return done(state.query); }
  if (p === "/api/customer/tender" && method === "GET") return json(tenderView(state));
  if (p === "/api/customer/tender/explain" && method === "GET") return json(S.explain);
  if (p === "/api/customer/tender/consent" && method === "POST") {
    const t = state.tender;
    if (body.granted) { t.consent = true; if (t.status === "none") t.status = "open"; note(state, "You", "Started the tender and allowed bidders to see the weight profile."); }
    else { t.consent = false; note(state, "You", "Withdrew consent. Bidders can no longer open the weight profile."); }
    return done(tenderView(state));
  }
  if (p === "/api/customer/tender/award" && method === "POST") {
    const row = S.offer_rows.find((r: Json) => r.id === body.offer_id);
    if (!row) return fail(404, "Unknown offer");
    Object.assign(state.tender, { status: "awarded", awarded: row.id });
    note(state, "You", `Chose ${row.operator}.`);
    return done(tenderView(state));
  }
  if (p === "/api/customer/tender/reopen" && method === "POST") {
    Object.assign(state.tender, { status: "open", awarded: null });
    note(state, "You", "Undid the choice. The tender is open again.");
    return done(tenderView(state));
  }
  const m = p.match(/^\/api\/customer\/compactors\/(CMP-\d{5})$/);
  if (m && method === "GET") {
    const v = (S.compactors as Record<string, Json>)[m[1]];
    return v ? json(v) : fail(404, "Unknown compactor");
  }

  // ---- waste company (never the customer's prices, invoices or choice)
  if (p === "/api/hauler" && method === "GET")
    return json({ ...S.hauler, recommended: state.recommended ?? false, confirmed: state.confirmed, checked: state.checked });
  if (p === "/api/hauler/tender" && method === "GET")
    return json({ notice: S.notice, consent: state.tender.consent, my_record: (S.customer.cards as Record<string, Json>)[S.me] ?? null });
  if (p === "/api/hauler/tender/pack" && method === "GET")
    return state.tender.consent ? json(S.pack) : fail(403, "The customer has withdrawn its weights");
  if (p === "/api/hauler/pickups" && method === "POST") {
    const out = toggle(state, "confirmed", new Set(S.hauler.fleet.map((x: Json) => x.id)), body);
    return out ? done(out) : fail(404, "Unknown item");
  }
  if (p === "/api/hauler/trucks" && method === "POST") {
    const out = toggle(state, "checked", new Set(S.hauler.trucks.map((t: Json) => t.truck)), body);
    return out ? done(out) : fail(404, "Unknown item");
  }
  if (p === "/api/hauler/recommend" && method === "POST") { state.recommended = Boolean(body.on); return done({ recommended: state.recommended }); }

  return fail(404, "Unknown API path");
}

const SID = /(?:^|;\s*)ow_sid=([A-Za-z0-9-]{20,64})/;

export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    const url = new URL(req.url);
    const found = req.headers.get("cookie")?.match(SID)?.[1];
    const sid = found ?? crypto.randomUUID();
    // The session cookie is set on the page load itself, so the page's parallel API calls share one session.
    const res = url.pathname.startsWith("/api/")
      ? await api(req, url, env.SESSIONS.get(env.SESSIONS.idFromName(sid)) as unknown as Store)
      : await env.ASSETS.fetch(req).then((a) => new Response(a.body, a));
    if (!found) res.headers.append("set-cookie", `ow_sid=${sid}; Path=/; Max-Age=2592000; HttpOnly; Secure; SameSite=Lax`);
    return res;
  },
} satisfies ExportedHandler<Env>;
