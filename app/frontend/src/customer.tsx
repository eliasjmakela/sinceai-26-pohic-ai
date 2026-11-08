import { useEffect, useMemo, useState } from "react";
import { Link, Route, Routes, useLocation, useSearchParams } from "react-router-dom";
import { post, useData } from "./api";
import { FillScatter, WeightTrend } from "./charts";
import { Bar, Compactor, Drawer, Icon, Kpi, Loading, Panel, Shell, Tabs, Tag, cls, date, eur, eur2, int, kg, monthName, pct, shortDate, t1, useToast } from "./ui";

const BASIS: Record<string, string> = { WEIGHBRIDGE: "Weighing ticket", INVOICE_QUANTITY: "Invoice tonnage, no ticket shared", DEVICE_ESTIMATE: "Compactor weight", UNKNOWN: "Not known" };
const STATUS: Record<string, string> = { MISSED_BY_OPERATOR: "Visit missed", PARTIAL: "Partial pickup", CANCELLED_BY_CUSTOMER: "Cancelled by you", WASTED_TRIP: "Wasted trip" };
const PRICING: Record<string, string> = { FIXED_PER_LIFT: "Per pickup", HYBRID: "Per pickup + per tonne", HYBRID_MIN: "Per pickup + per tonne", PER_TONNE: "Per tonne" };

const isDone = (a: any, c: any) => a === "tender" ? c.tender_status === "awarded" : a === "contract" ? c.query_state.status === "sent" : Boolean(c.decisions?.["order-by-weight"]);

export function CustomerPortal() {
  const { data: c, error, reload } = useData("/api/customer");
  const { pathname } = useLocation();
  useEffect(() => { reload(); }, [pathname, reload]);
  const pending = c ? ["trips", "contract", "tender"].filter((id) => !isDone(id, c)).length : 0;
  const nav = [
    { to: "/customer", label: "Today", icon: "today", end: true, badge: pending || null },
    { to: "/customer/contract", label: "Contract", icon: "contract" },
    { to: "/customer/tender", label: "Tender", icon: "tender", badge: c && c.tender_status === "open" ? "Open" : null },
  ];
  return (
    <Shell who={c?.name ?? ""} sub={c ? `${c.facts.devices} compactors, ${c.region}` : ""} portal="Customer" nav={nav} liveLabel={c ? `Live · ${date(c.as_of)}` : "Live"}>
      {!c ? <div className="canvas"><Loading error={error} /></div> : (
        <Routes>
          <Route index element={<Today c={c} reload={reload} pending={pending} />} />
          <Route path="contract" element={<Contract c={c} />} />
          <Route path="tender" element={<Tender c={c} onChange={reload} />} />
        </Routes>
      )}
    </Shell>
  );
}

// ---- Today: overview, then the selected compactor, then what needs deciding --------------------------------------------
function Today({ c, reload, pending }: any) {
  const [params, setParams] = useSearchParams();
  const total = c.live.reduce((s: number, x: any) => s + x.mass_kg, 0);
  const soonest = c.live.reduce((a: any, x: any) => (x.days_to_full < a.days_to_full ? x : a), c.live[0]);
  const selected = c.live.find((x: any) => x.id === params.get("c")) ?? soonest;
  const select = (id: string) => setParams({ c: id }, { replace: true });
  return (
    <>
      <Bar title={soonest.days_to_full < 0.5 ? `${soonest.name} is full now` : `Nothing needs a truck for ${soonest.days_to_full.toFixed(0)} days`} sub={monthName(c.as_of.slice(0, 7), true)} />
      <div className="canvas">
        <div className="kpis">
          <Kpi label="In your compactors now" value={kg(total)} sub={`${c.live.length} weighing live`} />
          <Kpi label="Next pickup needed" value={soonest.days_to_full < 0.5 ? "Now" : `${soonest.days_to_full.toFixed(0)} days`} sub={soonest.name} tag="estimate" />
          <Kpi label="You pay per tonne" value={eur2(c.market.today_price_t)} sub={`${int(c.facts.lifts)} pickups, ${t1(c.facts.tonnes)} a year`} />
          <Kpi label="Decisions waiting" value={pending || "None"} sub={pending ? "This month" : "No open decisions"} tone={pending ? undefined : "good"} />
        </div>
        <div className="today-grid">
          <Panel title="Compactors" flush className="p-list">
            <ul className="select-list">
              {c.live.map((x: any) => (
                <li key={x.id}>
                  <button className={cls("select-row", selected.id === x.id && "select-on")} aria-pressed={selected.id === x.id} onClick={() => select(x.id)}>
                    <Compactor share={x.share_pct} size="small" />
                    <span className="sr-main"><strong>{x.name}</strong><span>{kg(x.mass_kg)} · {x.days_to_full < 0.5 ? "full now" : `full in ${x.days_to_full.toFixed(0)} d`}</span></span>
                  </button>
                </li>
              ))}
            </ul>
            {c.not_weighed > 0 && <p className="list-note">{c.not_weighed} compactor without weighing.</p>}
          </Panel>
          <CompactorDetail x={selected} c={c} tabParam={params.get("tab")} focus={params.get("pickup")} />
          <Decisions c={c} reload={reload} />
        </div>
      </div>
    </>
  );
}

function CompactorDetail({ x, c, tabParam, focus }: any) {
  const [tab, setTab] = useState(tabParam === "pickups" ? "pickups" : "now");
  useEffect(() => { if (tabParam === "pickups") setTab("pickups"); }, [tabParam, x.id]);
  return (
    <Panel className="p-detail" title={x.name} meta={<Tabs value={tab} onChange={setTab} items={[{ id: "now", label: "Now" }, { id: "pickups", label: "Pickups" }]} />}>
      {tab === "now" ? (
        <div className="detail-now">
          <div className="detail-top">
            <div className="detail-glyph"><Compactor share={x.share_pct} /></div>
            <div className="detail-figs">
              <div className="big-kg">{kg(x.mass_kg)}</div>
              <div className="muted">{pct(x.share_pct)} of its {kg(x.usual_kg)} target</div>
              <div className="detail-when">{x.days_to_full < 0.5 ? "Full now" : `Full in about ${x.days_to_full.toFixed(0)} days`}</div>
            </div>
            <dl className="detail-cost">
              <div><dt>Picked up now</dt><dd>{x.eur_t_now == null || x.share_pct < 25 ? "–" : `${eur(x.eur_t_now)}/t`}</dd></div>
              <div><dt>At target</dt><dd className="tone-good">{eur(x.eur_t_full)}/t</dd></div>
            </dl>
          </div>
          <WeightTrend trend={x.trend} target={x.usual_kg} kgPerDay={x.kg_per_day} asOf={c.as_of} />
          <dl className="mini-stats">
            <div><dt>Pickups a year</dt><dd>{x.pickups}</dd></div>
            <div><dt>If ordered by weight</dt><dd>{x.weight_pickups} <Tag kind="estimate" /></dd></div>
            <div><dt>Tonnes a year</dt><dd>{x.tonnes.toFixed(1)}</dd></div>
            <div><dt>Material credits</dt><dd>{eur(x.credit_eur)}</dd></div>
          </dl>
          <p className="fine">Estimated before the truck leaves, credits included.</p>
        </div>
      ) : <PickupList id={x.id} focus={focus} />}
    </Panel>
  );
}

function PickupList({ id, focus }: any) {
  const { data: v, error } = useData(`/api/customer/compactors/${id}`);
  if (!v) return <Loading error={error} />;
  return (
    <div className="table-wrap"><table className="pickups">
      <thead><tr><th>Date</th><th className="num">Fill</th><th className="num">In container</th><th className="num">Billed</th><th className="num">Cost</th></tr></thead>
      <tbody>{v.pickups.filter((p: any) => p.status !== "SKIPPED_LOW_FILL").map((p: any) => <PickupRow key={p.id} x={p} defaultOpen={focus === p.id} />)}</tbody>
    </table></div>
  );
}

function PickupRow({ x, defaultOpen }: any) {
  const [open, setOpen] = useState(defaultOpen);
  const missed = ["MISSED_BY_OPERATOR", "CANCELLED_BY_CUSTOMER"].includes(x.status);
  return (
    <>
      <tr className={cls("row-click", open && "row-open", missed && "row-muted")} onClick={() => !missed && setOpen(!open)}>
        <td><button className="row-toggle" aria-expanded={open} disabled={missed}>{!missed && <span className={open ? "chev chev-open" : "chev"}><Icon name="chevron" /></span>}{date(x.date)}</button>{STATUS[x.status] && <div className="fine">{STATUS[x.status]}</div>}</td>
        <td className="num">{pct(x.fill_pct)}</td><td className="num">{kg(x.mass_before_kg)}</td><td className="num">{kg(x.billed_kg)}</td><td className="num">{missed ? "–" : eur2(x.cost_eur)}</td>
      </tr>
      {open && (
        <tr className="trace-row"><td colSpan={5}>
          <ol className="trace">
            <li><b>Order</b>{x.job_ref}{x.ref_on_invoice && <small>Invoice says {x.ref_on_invoice}</small>}{x.hours_to_pickup != null && <small>{x.hours_to_pickup.toFixed(0)} h to pickup</small>}</li>
            <li><b>Weighing ticket</b>{x.ticket_id ?? "Not shared"}{x.ticket_kg != null && <small>{kg(x.ticket_kg)}{x.truck ? `, ${x.truck}` : ""}</small>}</li>
            <li><b>Compactor</b>{kg(x.compactor_kg)}<small>{x.ticket_kg && x.compactor_kg ? `${x.compactor_kg - x.ticket_kg > 0 ? "+" : ""}${int(x.compactor_kg - x.ticket_kg)} kg against the ticket` : "No ticket to compare"}</small></li>
            <li><b>Contract</b>{x.version}<small>{BASIS[x.basis] ?? x.basis}</small></li>
          </ol>
          <table className="inner">
            <thead><tr><th>Invoice line</th><th className="num">Contract</th><th className="num">Invoice</th><th className="num">Difference</th></tr></thead>
            <tbody>{x.lines.map((ln: any) => {
              const diff = (ln.invoice_eur ?? 0) - (ln.contract_eur ?? 0);
              const differs = Math.abs(diff) > 0.005;
              return <tr key={ln.type} className={differs ? "line-diff" : ""}><td>{ln.label}</td><td className="num">{eur2(ln.contract_eur)}</td><td className="num">{eur2(ln.invoice_eur)}</td><td className="num">{differs ? eur2(diff) : "–"}</td></tr>;
            })}</tbody>
          </table>
        </td></tr>
      )}
    </>
  );
}

function Decisions({ c, reload }: any) {
  const [poll, setPoll] = useState<number | undefined>(4000);
  const { data: r, error } = useData("/api/customer/report", poll);
  useEffect(() => { if (r && !r.pending) setPoll(undefined); }, [r]);
  const toast = useToast();
  const [openId, setOpenId] = useState<string | null>(null);
  const [numbers, setNumbers] = useState<any>(null);
  const [draft, setDraft] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const items = r?.items ?? [];
  const todo = items.filter((i: any) => !isDone(i.id, c));
  const done = items.filter((i: any) => isDone(i.id, c));
  const current = todo.find((i: any) => i.id === openId) ?? todo[0];
  const decide = async (decision: string | null) => { await post("/api/customer/decisions", { id: "order-by-weight", decision }); reload(); };
  const undoQuery = async () => { await post("/api/customer/query/cancel"); reload(); };
  const q = c.query_state;

  const act = async (it: any) => {
    const a = it.action;
    if (a.kind === "approve") { await decide("approved"); toast(a.done, () => decide(null)); }
    if (a.kind === "query") {
      setBusy(true);
      try { const res = await post("/api/customer/query/draft"); setDraft(res.text); await reload(); } finally { setBusy(false); }
    }
  };
  if (!r) return <Panel title="Decisions" className="p-decide"><Loading error={error} /></Panel>;
  return (
    <Panel title="Decisions" meta={todo.length ? <span className="count">{todo.length}</span> : <span className="tone-good strong">All done</span>} className="p-decide" flush>
      <ul className="inbox">
        {todo.map((it: any) => {
          const on = current?.id === it.id;
          return (
            <li key={it.id} className={cls("inbox-item", on && "inbox-on")}>
              <button className="inbox-head" aria-expanded={on} onClick={() => setOpenId(it.id)}>
                <span className="inbox-figline"><span className="inbox-fig">{it.figure}</span><span className="inbox-figlabel">{it.figure_label}{it.evidence && <> <Tag kind={it.evidence} /></>}</span></span>
                <span className="inbox-title">{it.headline}</span>
              </button>
              {on && (
                <div className="inbox-body">
                  <p>{it.body}</p>
                  {it.action.kind === "link"
                    ? <Link className="btn btn-primary btn-block" to={it.action.to}>{it.action.label}</Link>
                    : <button className="btn btn-primary btn-block" disabled={busy} onClick={() => act(it)}>{busy ? "Writing your message…" : it.action.label}</button>}
                  <div className="inbox-foot">
                    <button className="link-btn" onClick={() => setNumbers(it)}>Show the numbers</button>
                    {it.action.kind === "approve" && <button className="link-btn link-quiet" onClick={async () => { await decide("not_now"); toast("Left as it is for now", () => decide(null)); }}>Not now</button>}
                  </div>
                  {it.action.reversal && <p className="fine">{it.action.reversal}</p>}
                </div>
              )}
            </li>
          );
        })}
        {done.map((it: any) => (
          <li key={it.id} className="inbox-done">
            <Icon name="check" />
            <span className="inbox-title">{it.id === "tender" ? <Link to="/customer/tender">Offer chosen</Link> : it.id === "contract" ? `Sent to ${c.operator}` : c.decisions["order-by-weight"] === "approved" ? it.action.done : "Target weight: not now"}</span>
            {it.id !== "tender" && <button className="link-btn" onClick={() => (it.id === "contract" ? undoQuery() : decide(null))}>Undo</button>}
          </li>
        ))}
      </ul>
      <p className="list-note">You approve every action.</p>
      {numbers && (
        <Drawer title={numbers.headline} onClose={() => setNumbers(null)}>
          <div className="drawer-fig"><strong>{numbers.figure}</strong><span>{numbers.figure_label}</span></div>
          <p>{numbers.body}</p>
          <h3>How this is worked out</h3>
          <ul className="calc">{numbers.calc.map((l: string) => <li key={l}>{l}</li>)}</ul>
          <Link className="btn" to={numbers.link} onClick={() => setNumbers(null)}>Open the records</Link>
        </Drawer>
      )}
      {(draft !== null || q.status === "draft") && (
        <Drawer title={`Your message to ${c.operator}`} onClose={async () => { setDraft(null); await post("/api/customer/query/cancel"); reload(); }}>
                    <textarea className="draft" rows={16} value={draft ?? q.text ?? ""} onChange={(e) => setDraft(e.target.value)} aria-label="Message" />
          <div className="drawer-actions">
            <button className="btn btn-primary" onClick={async () => { await post("/api/customer/query/send", { text: draft ?? q.text }); setDraft(null); await reload(); toast(`Sent to ${c.operator}`, undoQuery); }}>Send</button>
            <button className="btn" onClick={async () => { setDraft(null); await post("/api/customer/query/cancel"); reload(); }}>Cancel</button>
          </div>
        </Drawer>
      )}
    </Panel>
  );
}

// ---- Contract: a verdict first, then the evidence ----------------------------------------------------------------------
const GROUPS: { kind: string; title: (n: number) => string; note?: string }[] = [
  { kind: "FAR_FROM_FULL", title: (n) => `${n} pickups came early`, note: "Amount: avoidable pickup cost." },
  { kind: "WRONG_MATERIAL", title: (n) => `${n} loads graded C or R`, note: "Graded by the waste company. Amount: added charges." },
  { kind: "INVOICE", title: (n) => `${n} pickups billed differently from the contract`, note: "Amount: billed above the contract." },
  { kind: "LATE_SURCHARGE", title: (n) => `${n} overflow ${n === 1 ? "charge" : "charges"} on a late pickup` },
  { kind: "MISSED_VISIT", title: (n) => `${n} planned ${n === 1 ? "visit" : "visits"} didn't happen` },
  { kind: "MOISTURE", title: (n) => `${n} compactors got heavier while unused`, note: "Likely cause: rain or snow in the container." },
  { kind: "REFERENCE", title: (n) => `${n} invoices with a different job reference`, note: "Matched by contract and date." },
  { kind: "CALIBRATION", title: (n) => `${n} compactors may need calibrating` },
];
const KEPT_AT = 90;

function Contract({ c }: any) {
  const sv = c.service, ic = c.invoice_check, res = c.response;
  const [group, setGroup] = useState<any>(null);
  const groups = GROUPS.map((g) => ({ ...g, rows: c.findings.filter((z: any) => z.kind === g.kind) })).filter((g) => g.rows.length).map((g) => ({ ...g, sum: g.rows.reduce((a: number, z: any) => a + Math.max(z.eur ?? 0, 0), 0) }));
  const promises = [
    { key: "response", name: "Response time", label: `Orders picked up within ${res.hours} h`, value: (res.within / res.orders) * 100, detail: `${res.within} of ${res.orders}, longest ${res.longest_h.toFixed(0)} h`, tag: "assumption" as const },
    { key: "schedule", name: "Keeping to schedule", label: "On schedule, within 2 h", value: sv.on_time_share_pct, detail: `${sv.lifts} pickups, ${sv.missed_visits} missed` },
    { key: "tickets", name: "Sharing tickets", label: "Tickets shared within 7 days", value: sv.tickets_shared_share_pct, detail: "" },
    { key: "invoices", name: "Invoice accuracy", label: "Invoice lines match the contract", value: (1 - ic.lines_differing / ic.lines_total) * 100, detail: `${ic.lines_differing} of ${ic.lines_total} differ, ${eur(ic.above_eur)} above` },
  ];
  const kept = promises.filter((p) => p.value >= KEPT_AT).length;
  const asks = promises.filter((p) => p.value < KEPT_AT);
  const total = c.materials.reduce((s: number, z: any) => s + z.tonnes, 0);
  return (
    <>
      <Bar title={`${c.operator}: ${kept} of ${promises.length} contract terms on target`} sub={asks.length ? `Below target: ${asks.map((p) => p.name.toLowerCase()).join(", ")}` : "All on target"} />
      <div className="canvas">
        <div className="promises">
          {promises.map((p) => {
            const ok = p.value >= KEPT_AT;
            return (
              <div className="promise" key={p.key}>
                <div className="promise-top"><span className={ok ? "chip chip-good" : "chip chip-ask"}>{ok ? "On target" : "Below target"}</span>{p.tag && <Tag kind={p.tag} />}</div>
                <div className="promise-value">{pct(p.value)}</div>
                <div className="promise-bar"><div className={ok ? "bar-kept" : "bar-ask"} style={{ width: `${Math.min(100, p.value)}%` }} /><i style={{ left: `${KEPT_AT}%` }} /></div>
                <div className="promise-label">{p.label}</div>
                <div className="fine">{p.detail}</div>
              </div>
            );
          })}
        </div>
        <div className="contract-grid">
          <Panel title="Fill level at pickup" className="p-chart">
            <FillScatter rows={c.scatter} />
            <div className="bands">{c.bands.map((b: any) => <div key={b.label}><strong>{eur(b.eur_per_t)}/t</strong><span>{b.label}</span></div>)}</div>
          </Panel>
          <Panel title="Findings" className="p-look" flush>
            <ul className="look-list">
              {groups.map((g) => (
                <li key={g.kind}><button className="look-row" onClick={() => setGroup(g)}><span>{g.title(g.rows.length)}</span>{g.sum > 0 && <strong>{eur(g.sum)}</strong>}<Icon name="chevron" /></button></li>
              ))}
            </ul>
            <p className="list-note">A difference can come from the device, the data or the company.</p>
          </Panel>
          <Panel title="Your compactors" className="p-comp" flush>
            <div className="table-wrap"><table className="tight">
              <thead><tr><th>Compactor</th><th>You pay</th><th className="num">Pickups</th><th className="num">By weight <Tag kind="estimate" /></th><th className="num">Tonnes</th><th className="num">Credits</th></tr></thead>
              <tbody>{c.compactors.map((x: any) => (
                <tr key={x.id}>
                  <td><Link className="row-link" to={`/customer?c=${x.id}`}>{x.municipality}, {x.material.toLowerCase()}</Link></td>
                  <td>{PRICING[x.pricing_model]}</td><td className="num">{x.pickups}</td><td className="num">{x.weight_pickups}</td><td className="num">{x.tonnes.toFixed(1)}</td><td className="num">{eur(x.credit_eur)}</td>
                </tr>
              ))}</tbody>
            </table></div>
          </Panel>
          <Panel title="Materials" meta={<span className="esg">{pct(c.recycled_pct)} <small>into recycling streams</small></span>} className="p-esg">
            <div className="stack" role="img" aria-label="Tonnes by material">{c.materials.map((z: any, i: number) => <div key={z.material} className={`stack-seg seg-${i}`} style={{ flexGrow: z.tonnes }} />)}</div>
            <ul className="stack-legend">{c.materials.map((z: any, i: number) => <li key={z.material}><i className={`seg-${i}`} />{z.material} <strong>{z.tonnes.toFixed(1)} t</strong> <span className="muted">{pct((z.tonnes / total) * 100)}</span></li>)}</ul>
          </Panel>
        </div>
        <p className="fine">Target: {KEPT_AT} % or more. Only you see your prices and invoices.</p>
      </div>
      {group && (
        <Drawer title={group.title(group.rows.length)} onClose={() => setGroup(null)}>
          {group.note && <p className="muted">{group.note}</p>}
          <ul className="group-rows">
            {group.rows.map((z: any) => (
              <li key={z.id}>
                <span className="fine nowrap">{shortDate(z.date)}</span>
                <span>{z.site}, {z.material.toLowerCase()}. {z.detail}</span>
                {z.pickup ? <Link className="inline-link nowrap" to={`/customer?c=${z.compactor}&tab=pickups&pickup=${z.pickup}`}>Open</Link> : <span />}
              </li>
            ))}
          </ul>
        </Drawer>
      )}
    </>
  );
}

// ---- Tender -------------------------------------------------------------------------------------------------------------
function Stepper({ steps }: { steps: { label: string; on: boolean }[] }) {
  return <ol className="stepper" aria-label="Tender progress">{steps.map((s, i) => <li key={i} className={s.on ? "step step-on" : "step"}><b>{s.on ? <Icon name="check" /> : i + 1}</b>{s.label}</li>)}</ol>;
}

function Tender({ c, onChange }: any) {
  const { data: t, setData } = useData("/api/customer/tender", 3000);
  const toast = useToast();
  if (!t) return <div className="canvas"><Loading /></div>;
  const act = async (path: string, body?: any) => { setData(await post(path, body)); onChange?.(); };
  const steps = [{ label: "Weights shared", on: t.consent }, { label: `${t.rows.length} offers uploaded`, on: t.rows.length > 0 }, { label: "You choose", on: t.status === "awarded" }];
  return <Offers c={c} t={t} act={act} toast={toast} steps={steps} />;
}

function ContractDates({ c }: any) {
  const from = new Date(c.as_of).getTime();
  const last = Math.max(...c.compactors.map((x: any) => new Date(x.contract_end).getTime()));
  const to = from + (last - from) * 1.04;
  const left = (d: string) => `${Math.max(0, ((new Date(d).getTime() - from) / (to - from)) * 100)}%`;
  const passed = (d: string) => new Date(d) < new Date(c.as_of);
  return (
    <Panel title="When each contract comes up" meta={<Tag kind="assumption" />}>
      <ul className="timeline">
        {c.compactors.map((x: any) => (
          <li key={x.id}>
            <span className="tl-name">{x.municipality}, {x.material.toLowerCase()}</span>
            <span className="tl-track" aria-hidden><i className="tl-line" style={{ width: left(x.contract_end) }} />{!passed(x.notice_by) && <i className="tl-notice" style={{ left: left(x.notice_by) }} />}<i className="tl-end" style={{ left: left(x.contract_end) }} /></span>
            <span className="tl-dates">{passed(x.notice_by) ? <span className="warn">Notice date passed</span> : <>Notice {date(x.notice_by)}</>}<small>Ends {date(x.contract_end)}</small></span>
          </li>
        ))}
      </ul>
    </Panel>
  );
}

function Offers({ c, t, act, toast, steps }: any) {
  const key = t.rows.map((r: any) => r.price_eur_t.toFixed(2)).join("-");
  const { data: quick } = useData(`/api/customer/tender/explain?fast=true&k=${key}`);
  const { data: worded } = useData(`/api/customer/tender/explain?k=${key}`);
  const summary = worded?.text ?? quick?.text;
  const m = c.market;
  const chosen = t.rows.find((r: any) => r.id === t.awarded);
  const today = c.cards[c.operator_id];
  const choose = async (r: any) => { await act("/api/customer/tender/award", { offer_id: r.id }); toast(`You chose ${r.operator}. Nothing is signed yet.`, () => act("/api/customer/tender/reopen")); };
  const row = (r: any, isToday = false) => (
    <li key={r.id} className={cls("offer", isToday && "offer-today", t.awarded === r.id && "offer-chosen")}>
      <div className="offer-who"><strong>{r.operator}</strong><span>{isToday ? "Today, paying per trip" : <>{r.kind} · uploaded {shortDate(r.uploaded)} <Tag kind="simulated" /></>}</span></div>
      <div className="offer-price">
        <div className="offer-figures"><strong>{eur2(r.price_eur_t)}<small>/t</small></strong><span>{eur(r.annual_eur)} a year{!isToday && <em> {r.saving_eur > 0 ? "−" : "+"}{eur(Math.abs(r.saving_eur))}</em>}</span></div>
        <div className="offer-bar"><div className={isToday ? "bar-today" : "bar-offer"} style={{ width: `${Math.min(100, (r.price_eur_t / m.today_price_t) * 100)}%` }} /></div>
      </div>
      <dl className="offer-service">
        <div><dt>On time</dt><dd>{r.on_time_pct == null ? "–" : pct(r.on_time_pct)}</dd></div>
        <div><dt>Response</dt><dd>{r.response_h == null ? "–" : `${r.response_h.toFixed(0)} h`}</dd></div>
        <div><dt>Tickets</dt><dd>{r.tickets_pct == null ? "–" : pct(r.tickets_pct)}</dd></div>
      </dl>
      <div className="offer-act">{isToday ? null : t.status === "awarded" ? (t.awarded === r.id ? <span className="chip chip-good">Chosen</span> : null) : <button className="btn" onClick={() => choose(r)}>Choose</button>}</div>
    </li>
  );
  return (
    <>
      <Bar title={t.status === "awarded" ? `You chose ${chosen?.operator}` : "Compare the offers"} sub={t.status === "awarded" ? `${eur2(chosen?.price_eur_t)} per tonne, about ${eur(chosen?.annual_eur)} a year.` : `Priced on your ${t1(m.tonnes)} a year.`}><Stepper steps={steps} /></Bar>
      <div className="canvas">
        {t.status !== "awarded" && summary && <div className="ai-line">{summary}</div>}
        <div className="notice">Offers you've received, uploaded to compare.</div>
        <ul className="offers">
          {row({ id: "today", operator: c.operator, price_eur_t: m.today_price_t, annual_eur: m.today_eur, on_time_pct: today?.on_time_pct, response_h: today?.response_h, tickets_pct: today?.tickets_pct }, true)}
          {t.rows.map((r: any) => row(r))}
        </ul>
        <div className="under-offers">
          <p className="fine">Prices cover pickups, transport and treatment. Material credits and rental don't change. Service record: the company's average in your region.</p>
          {t.status === "awarded" && <button className="link-btn" onClick={() => act("/api/customer/tender/reopen")}>Undo my choice</button>}
        </div>
        <div className="tender-grid">
          <ContractDates c={c} />
          <Panel title="What this tender shares" meta={<span className={t.consent ? "chip chip-good" : "chip chip-ask"}>{t.consent ? "Weights shared" : "Weights withdrawn"}</span>}>
            <div className="share-cols">
              <div><h3>Bidders see</h3><ul><li>Kilos per pickup, by compactor</li><li>Tonnes a year and a 12-month forecast</li><li>Contract end dates</li></ul></div>
              <div><h3>Bidders don't see</h3><ul><li>Your prices and invoices</li></ul></div>
            </div>
            <p className="fine">With your weights a bidder's estimate of your tonnes is typically ±{m.sigma_data_pct.toFixed(0)} % off, against ±{m.sigma_blind_pct.toFixed(0)} % guessing. <Tag kind="estimate" /></p>
            {t.consent
              ? <button className="link-btn link-quiet align-start" onClick={async () => { await act("/api/customer/tender/consent", { granted: false }); toast("Bidders can no longer open your weights.", () => act("/api/customer/tender/consent", { granted: true })); }}>Withdraw my weights</button>
              : <button className="link-btn align-start" onClick={() => act("/api/customer/tender/consent", { granted: true })}>Share my weights again</button>}
          </Panel>
        </div>
      </div>
    </>
  );
}
