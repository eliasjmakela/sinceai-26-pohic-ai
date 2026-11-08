import { useEffect, useMemo, useState } from "react";
import { Route, Routes } from "react-router-dom";
import { ApiError, post, useData } from "./api";
import { ForecastChart, PriceWaterfall, TonnesRange } from "./charts";
import { Bar, Compactor, Drawer, Icon, Kpi, Loading, Panel, Shell, Tabs, Tag, cls, date, eur, eur2, int, kg, pct, shortDate, t1, useToast } from "./ui";

export function HaulerPortal() {
  const { data: h, error, reload } = useData("/api/hauler");
  const { data: t } = useData("/api/hauler/tender", 3000);
  const soon = h ? h.fleet.filter((x: any) => x.days_to_full <= 3 && !h.confirmed.includes(x.id)).length : 0;
  const trucks = h ? h.trucks.filter((x: any) => !h.checked.includes(x.truck)).length : 0;
  const nav = [
    { to: "/waste-company", label: "Tenders", icon: "tender", end: true, badge: null },
    { to: "/waste-company/full-loads", label: "Full loads", icon: "truck", badge: soon || null },
    { to: "/waste-company/weight-check", label: "Weight check", icon: "scale", badge: trucks || null },
  ];
  return (
    <Shell who={h?.operator.name ?? ""} sub={h ? `${h.fleet.length} weighed compactors` : ""} portal="Waste company" nav={nav} liveLabel={h ? `Live · ${date(h.as_of)}` : "Live"}>
      {!h ? <div className="canvas"><Loading error={error} /></div> : (
        <Routes>
          <Route index element={<Tenders t={t} />} />
          <Route path="full-loads" element={<FullLoads h={h} reload={reload} />} />
          <Route path="weight-check" element={<WeightCheck h={h} reload={reload} />} />
        </Routes>
      )}
    </Shell>
  );
}

function Tenders({ t }: any) {
  if (!t) return <div className="canvas"><Loading /></div>;
  const n = t.notice;
  return (
    <>
      <Bar title={`${n.compactors} compactors in ${n.region}, price per tonne`} sub={`${n.materials.join(", ")} · ${n.term_years}-year contract · tender request uploaded ${shortDate(n.uploaded)}`}>
        <span className="chip chip-ask">{`Offers by ${shortDate(n.offers_due)}`}</span>
      </Bar>
      <div className="canvas">
        {t.consent ? <Pack t={t} n={n} /> : (
          <>
            <div className="notice notice-warn"><strong>Weight data withdrawn by the customer.</strong></div>
            <Panel title="Estimate without weight data">
              <div className="guess"><strong>{eur(n.blind_price_t)}</strong><span>per tonne, to be safe at ±{n.sigma_blind_pct.toFixed(0)} % <Tag kind="simulated" /></span></div>
              <TonnesRange blind={n.range_blind} />
              <p className="fine">Tonnes a year, guessed from similar sites.</p>
            </Panel>
          </>
        )}
      </div>
    </>
  );
}

function Pack({ t, n }: any) {
  const { data: p, error } = useData("/api/hauler/tender/pack");
  const [tab, setTab] = useState("price");
  if (error instanceof ApiError && error.status === 403) return null;
  if (!p) return <Loading error={error} />;
  return (
    <>
      <Tabs value={tab} onChange={setTab} items={[{ id: "price", label: "Your price" }, { id: "compactors", label: "The compactors" }, { id: "forecast", label: "Forecast" }]} />
      {tab === "price" && <Calculator p={p} t={t} n={n} />}
      {tab === "compactors" && (
        <Panel title="The compactors" flush>
          <div className="table-wrap"><table className="tight">
            <thead><tr><th>Compactor</th><th className="num">Tonnes a year</th><th className="num">Typical load</th><th className="num">Load range</th><th className="num">Pickups today</th><th className="num">When full</th><th>Contract ends</th></tr></thead>
            <tbody>{p.rows.map((r: any) => (
              <tr key={r.site + r.material}>
                <td><strong>{r.site}, {r.material.toLowerCase()}</strong><div className="fine">{r.container_m3} m³ {r.equipment_class}</div></td>
                <td className="num">{r.tonnes.toFixed(1)}</td><td className="num">{kg(r.p50)}</td><td className="num">{int(r.p10)}–{int(r.p90)}</td><td className="num">{r.pickups}</td><td className="num">{r.weight_pickups}</td><td>{date(r.contract_end)}</td>
              </tr>
            ))}</tbody>
          </table></div>
        </Panel>
      )}
      {tab === "forecast" && (
        <div className="tender-grid">
          <Panel title="Tonnes a month, next 12 months"><ForecastChart rows={p.forecast} /><p className="fine">One year of history, so the seasonal shape is uncertain. <Tag kind="estimate" /></p></Panel>
          <Panel title="How sure you can be of the tonnes"><TonnesRange blind={p.range_blind} data={p.range_data} /><p className="fine">Tonnes a year. Typical error in a backtest across the data. <Tag kind="estimate" /></p></Panel>
        </div>
      )}
    </>
  );
}

function Calculator({ p, t, n }: any) {
  const m = p.model, T = p.tonnes;
  const [perPickup, setPerPickup] = useState<number>(m.cost_per_pickup);
  const [perTonne, setPerTonne] = useState<number>(m.cost_per_t);
  const [margin, setMargin] = useState<number>(m.margin_pct);
  const [costs, setCosts] = useState(false);
  const mg = 1 + margin / 100;
  const blindRisk = 1 + (m.risk_z * p.sigma_blind_pct) / 100;
  const dataRisk = 1 + (m.risk_z * p.sigma_data_pct) / 100;
  const costToday = perPickup * p.pickups_today + perTonne * T;
  const costByWeight = perPickup * p.pickups_by_weight + (perTonne + m.fee_t) * T;
  const blind = (costToday * mg * blindRisk) / T;
  const fullLoads = (costByWeight * mg * blindRisk) / T;
  const withData = (costByWeight * mg * dataRisk) / T;
  const [price, setPrice] = useState<number>(Math.round(withData * 1.04));
  const profit = price * T - costByWeight;
  const lowT = T * (1 - p.sigma_own_pct / 100);
  const profitLow = price * lowT - (perPickup * p.pickups_by_weight + (perTonne + m.fee_t) * lowT);
  const field = (label: string, v: number, set: (n: number) => void, unit: string, id: string) => (
    <div className="field"><label htmlFor={id}>{label}</label><div className="input"><input id={id} type="number" step="any" value={v} onChange={(e) => { const n = Number(e.target.value); if (Number.isFinite(n)) set(n); }} /><em>{unit}</em></div></div>
  );
  const rec = t.my_record;
  return (
    <div className="price-grid">
      <Panel title={`Price per tonne: ${eur(blind)} without weight data, ${eur(withData)} with`} meta={<button className="link-btn" onClick={() => setCosts(true)}>Your costs</button>}>
        <PriceWaterfall blind={blind} fullLoads={fullLoads} withData={withData} labels={["Guessing the tonnes", `Full loads: ${((1 - p.pickups_by_weight / p.pickups_today) * 100).toFixed(1)} % fewer pickups`, `Risk: ±${p.sigma_blind_pct.toFixed(0)} % → ±${p.sigma_data_pct.toFixed(0)} %`, "With the weights"]} />
        <p className="fine">The price that keeps your margin, on your costs. <Tag kind="simulated" /></p>
      </Panel>
      <Panel title="Plan your offer" className="p-offer">
        <label className="offer-big" htmlFor="offer">{eur(price)}<small> per tonne</small></label>
        <input id="offer" className="slider" type="range" min={Math.floor(withData * 0.8)} max={Math.ceil(blind)} step={1} value={price} onChange={(e) => setPrice(Number(e.target.value))} />
        <dl className="offer-out">
          <div><dt>Revenue a year, {t1(T)}</dt><dd>{eur(price * T)}</dd></div>
          <div><dt>Profit, as expected</dt><dd className={profit < 0 ? "warn" : "tone-good"}>{eur(profit)}</dd></div>
          <div><dt>If tonnes come in {p.sigma_own_pct.toFixed(0)} % low</dt><dd className={profitLow < 0 ? "warn" : ""}>{eur(profitLow)}</dd></div>
        </dl>
        <div className="offer-asks"><h3>The customer asks for</h3><ul className="ask-list">{n.asks.map((a: string) => <li key={a}>{a}</li>)}</ul></div>
        {rec && <p className="fine">Your service record: {pct(rec.on_time_pct)} on time, {rec.response_h.toFixed(0)} h response, {pct(rec.tickets_pct)} tickets shared.</p>}
                <p className="fine center">Bid pack: {eur(n.price_per_pack_eur)} per tender.</p>
      </Panel>
      {costs && (
        <Drawer title="Your costs" onClose={() => setCosts(false)}>
          <p className="muted">Starting values. Enter your own; the price updates as you type. <Tag kind="assumption" /></p>
          <div className="fields">
            {field("Cost per pickup", perPickup, setPerPickup, "€", "c1")}
            {field("Cost per tonne", perTonne, setPerTonne, "€/t", "c2")}
            {field("Margin you need", margin, setMargin, "%", "c3")}
          </div>
          <p className="fine">Includes the OpenWeight fee: €30 per weighed compactor a month (about {eur2(m.fee_t)} a tonne at average tonnage).</p>
          <div className="drawer-fig"><strong>{eur2(withData)}</strong><span>per tonne with the weights</span></div>
        </Drawer>
      )}
    </div>
  );
}

function FullLoads({ h, reload }: any) {
  const toast = useToast();
  const [region, setRegion] = useState<string | null>(null);
  const nw = h.not_weighing, e = h.efficiency;
  const soon = h.fleet.filter((x: any) => x.days_to_full <= 3);
  const todo = soon.filter((x: any) => !h.confirmed.includes(x.id));
  const done = soon.filter((x: any) => h.confirmed.includes(x.id));
  const tonnes = (xs: any[]) => xs.reduce((sum: number, x: any) => sum + x.full_kg, 0) / 1000;
  const regions = useMemo(() => {
    const m = new Map<string, any[]>();
    todo.forEach((x: any) => m.set(x.region, [...(m.get(x.region) ?? []), x]));
    return [...m.entries()].sort((p, q) => q[1].length - p[1].length);
  }, [h.confirmed]);
  useEffect(() => { if (region && !regions.some(([r]) => r === region)) setRegion(null); }, [regions, region]);
  const shown = region ? todo.filter((x: any) => x.region === region) : todo;
  const mark = async (x: any, on: boolean) => {
    await post("/api/hauler/pickups", { id: x.id, on }); reload();
    if (on) toast(`Pickup confirmed: ${x.site}`, async () => { await post("/api/hauler/pickups", { id: x.id, on: false }); reload(); });
  };
  const recommend = async (on: boolean) => { await post("/api/hauler/recommend", { on }); reload(); if (on) toast("Passed to Europress", () => recommend(false)); };
  return (
    <>
      <Bar title={todo.length ? `${todo.length} full loads to plan` : "Every full load is planned"} sub="Compactors reaching the pickup fill level (80 %) within 3 days" />
      <div className="canvas">
        <div className="kpis">
          <Kpi label="Tonnes to collect" value={`${tonnes(todo).toFixed(0)} t`} sub={`${todo.length} compactors`} tag="estimate" />
          <Kpi label="Confirmed" value={done.length} sub={done.length ? `${tonnes(done).toFixed(1)} t planned` : "None yet"} tone={done.length ? "good" : undefined} />
          <Kpi label="Came early last year" value={int(e.early)} sub={`${pct(e.share_pct)} of ${int(e.pickups)} pickups`} tag="estimate" />
          <Kpi label="Billed for those visits" value={eur(e.visit_eur)} sub="Lost under a price per tonne" tag="estimate" />
        </div>
        <div className="loads-grid">
          <div className="stack-col">
            <Panel title="Regions" flush>
              <ul className="select-list">
                <li><button className={cls("region-row", !region && "select-on")} onClick={() => setRegion(null)}><strong>All regions</strong><span>{tonnes(todo).toFixed(1)} t</span></button></li>
                {regions.map(([r, xs]) => <li key={r}><button className={cls("region-row", region === r && "select-on")} onClick={() => setRegion(r)}><strong>{r}</strong><span>{xs.length} · {tonnes(xs).toFixed(1)} t</span></button></li>)}
              </ul>
            </Panel>
            {nw.compactors > 0 && (
              <Panel title={`${nw.compactors} compactors you can't plan by weight`}>
                <p className="fine">{nw.customers} customers. New Europress compactors include weighing at no extra cost.</p>
                {h.recommended
                  ? <div className="inline-done"><span className="tone-good strong">Passed to Europress</span><button className="link-btn" onClick={() => recommend(false)}>Undo</button></div>
                  : <button className="btn btn-block" onClick={() => recommend(true)}>Send to Europress as a lead</button>}
              </Panel>
            )}
          </div>
          <Panel title={region ?? "All regions"} meta={<span className="fine">Soonest first</span>} flush className="p-work">
            {shown.length === 0 ? <div className="empty-mini"><Icon name="check" />Nothing left to plan here.</div> : (
              <ul className="work">
                {shown.map((x: any) => (
                  <li key={x.id} className="work-row">
                    <Compactor share={x.fill_pct} size="small" />
                    <div className="work-name"><strong>{x.site}, {x.material.toLowerCase()}</strong><span className="fine">{x.container_m3} m³{region ? "" : ` · ${x.region}`}</span></div>
                    <div className="work-kg"><strong>{pct(x.fill_pct)} full</strong><span className="fine">{kg(x.mass_kg)}</span></div>
                    <div className={x.days_to_full < 0.5 ? "work-when work-now" : "work-when"}>{x.days_to_full < 0.5 ? "Ready now" : `${x.days_to_full.toFixed(1)} days`}</div>
                    <button className="btn btn-small" onClick={() => mark(x, true)}>Confirm</button>
                  </li>
                ))}
              </ul>
            )}
          </Panel>
        </div>
      </div>
    </>
  );
}

function WeightCheck({ h, reload }: any) {
  const toast = useToast();
  const s = h.weight_stats;
  const [sel, setSel] = useState<string | null>(null);
  const todo = h.trucks.filter((t: any) => !h.checked.includes(t.truck));
  const selected = todo.find((t: any) => t.truck === sel) ?? todo[0];
  const done = h.trucks.filter((t: any) => h.checked.includes(t.truck));
  const mark = async (id: string, on: boolean) => {
    await post("/api/hauler/trucks", { id, on }); reload();
    if (on) toast(`Truck ${id} marked as weighed`, () => mark(id, false));
  };
  return (
    <>
      <Bar title={todo.length > 1 ? `${todo.length} trucks to weigh empty` : todo.length === 1 ? "1 truck to weigh empty" : "Your tickets and the compactors agree"} sub="Ticket weights compared with compactor weights. Billing stays on your weighbridge." />
      <div className="canvas">
        <div className="kpis kpis-3">
          <Kpi label="Pickups compared" value={int(s.pickups)} sub="Single loads with no side waste" />
          <Kpi label="Median difference" value={pct(s.median_pct, 1)} sub="Ticket to compactor" />
          <Kpi label="Within ±10 %" value={pct(s.within10_pct)} sub="Of pickups compared" />
        </div>
        <div className="loads-grid">
          <Panel title="Trucks" flush>
            <ul className="select-list">
              {todo.map((t: any) => (
                <li key={t.truck}><button className={cls("region-row", selected?.truck === t.truck && "select-on")} onClick={() => setSel(t.truck)}><strong>{t.truck}</strong><span>{int(Math.abs(t.median_diff_kg))} kg</span></button></li>
              ))}
              {done.map((t: any) => (
                <li key={t.truck} className="done-row"><Icon name="check" /><span>{t.truck}</span><button className="link-btn" onClick={() => mark(t.truck, false)}>Undo</button></li>
              ))}
            </ul>
          </Panel>
          {selected ? (
            <Panel title={`Truck ${selected.truck}`} meta={<button className="btn btn-primary btn-small" onClick={() => mark(selected.truck, true)}>Mark as weighed</button>} className="p-work">
              <div className="truck-head">
                <div className="truck-num"><strong>{int(Math.abs(selected.median_diff_kg))} kg</strong><span>{selected.median_diff_kg < 0 ? "tickets above compactors" : "compactors above tickets"}, median</span></div>
                <p className="muted">{selected.pickups} pickups at {selected.compactors} compactors. Likely cause: outdated truck tare.</p>
              </div>
              <div className="table-wrap"><table className="tight">
                <thead><tr><th>Date</th><th>Ticket</th><th className="num">Ticket</th><th className="num">Compactor</th><th className="num">Difference</th></tr></thead>
                <tbody>{selected.recent.map((r: any) => <tr key={r.ticket_id}><td>{date(r.date)}</td><td className="fine">{r.ticket_id}</td><td className="num">{kg(r.ticket_kg)}</td><td className="num">{kg(r.compactor_kg)}</td><td className="num">{r.diff_kg > 0 ? "+" : "−"}{int(Math.abs(r.diff_kg))} kg</td></tr>)}</tbody>
              </table></div>
            </Panel>
          ) : <div className="empty"><Icon name="check" /><h2>Nothing to check</h2><p>All flagged trucks weighed.</p></div>}
        </div>
      </div>
    </>
  );
}
