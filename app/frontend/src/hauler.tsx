import { useEffect, useMemo, useState } from "react";
import { Route, Routes } from "react-router-dom";
import { ApiError, post, useData } from "./api";
import { ForecastChart, TonnesRange } from "./charts";
import { Bar, Compactor, Drawer, Icon, Kpi, Loading, Panel, Shell, Tabs, Tag, cls, date, eur, eur2, int, kg, pct, shortDate, t1, useToast } from "./ui";

export function HaulerPortal() {
  const { data: h, error, reload } = useData("/api/hauler");
  const { data: t } = useData("/api/hauler/tender", 3000);
  const nav = [
    { to: "/waste-company", label: "Tenders", icon: "tender", end: true, badge: null },
  ];
  return (
    <Shell who={h?.operator.name ?? ""} sub={h ? `${h.fleet.length} weighed compactors` : ""} portal="Waste company" nav={nav} liveLabel={h ? `Live · ${date(h.as_of)}` : "Live"}>
      {!h ? <div className="canvas"><Loading error={error} /></div> : (
        <Routes>
          <Route index element={<Tenders t={t} h={h} />} />
        </Routes>
      )}
    </Shell>
  );
}

function Tenders({ t, h }: any) {
  if (!t) return <div className="canvas"><Loading /></div>;
  const n = t.notice;
  return (
    <>
      <Bar title={`${n.compactors} compactors in ${n.region}, price per tonne`} sub={`${n.materials.join(", ")} · ${n.term_years}-year contract · tender request uploaded ${shortDate(n.uploaded)}`}>
        <span className="chip chip-ask">{`Offers by ${shortDate(n.offers_due)}`}</span>
      </Bar>
      <div className="canvas">
        {t.consent ? <Pack t={t} n={n} prospects={h.prospects} /> : (
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

function Pack({ t, n, prospects }: any) {
  const { data: p, error } = useData("/api/hauler/tender/pack");
  const [tab, setTab] = useState("price");
  if (error instanceof ApiError && error.status === 403) return null;
  if (!p) return <Loading error={error} />;
  return (
    <>
      <Tabs value={tab} onChange={setTab} items={[{ id: "price", label: "Your price" }, { id: "compactors", label: "The compactors" }, { id: "forecast", label: "Forecast" }]} />
      {tab === "price" && <Calculator p={p} t={t} n={n} prospects={prospects} />}
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

function Calculator({ p, t, n, prospects }: any) {
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
      <Panel title="Plan your offer" className="p-offer" meta={<button className="link-btn" onClick={() => setCosts(true)}>Your costs</button>}>
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
      <Prospects rows={prospects} />
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

function Prospects({ rows }: any) {
  const lowest = rows.filter((r: any) => r.fit === "Lowest bid");
  return (
    <Panel title="Potential customers" className="p-prospects">
      <p className="muted">Customers in your region you don't serve yet, ranked by what you could earn. Estimated on your own costs and the weights they share. Names appear when a customer opens a tender.</p>
      <div className="prospect-kpis">
        <div><strong>{lowest.length}</strong><span>where your bid would be lowest</span></div>
        <div><strong>{eur(lowest.reduce((a: number, r: any) => a + (r.margin_eur ?? 0), 0))}</strong><span>margin a year if you win them <Tag kind="simulated" /></span></div>
      </div>
      <ul className="prospects">
        {rows.map((r: any) => (
          <li key={r.id} className={cls("prospect", r.fit !== "Lowest bid" && "prospect-muted")}>
            <div className="prospect-top">
              <strong>{r.sector}</strong>
              <span className={cls("chip", r.fit === "Lowest bid" ? "chip-good" : "")}>{r.fit === "Lowest bid" ? "Your bid lowest" : "Others bid lower"}</span>
            </div>
            <div className="fine">{r.compactors} compactors · {t1(r.tonnes)} a year · {r.materials.join(", ").toLowerCase()}</div>
            <dl className="prospect-figs">
              <div><dt>Contract ends</dt><dd>{r.contract_end ? date(r.contract_end) : "–"}</dd></div>
              <div><dt>Your price</dt><dd>{eur2(r.price_t)}/t</dd></div>
              <div><dt>A year</dt><dd>{eur(r.annual_eur)}</dd></div>
              <div><dt>Margin</dt><dd className={r.margin_eur ? "tone-good" : ""}>{r.margin_eur ? `${eur(r.margin_eur)} · ${pct(r.margin_pct)}` : "–"}</dd></div>
            </dl>
          </li>
        ))}
      </ul>
      <p className="fine">From the market simulation on synthetic data. <Tag kind="simulated" /></p>
    </Panel>
  );
}
