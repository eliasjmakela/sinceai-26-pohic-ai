import { useMemo, useState } from 'react'
import { bundle } from '../bundle'
import { simulateBusiness, type BizParams } from '../business/model'

/** Beat 6 — the business and the SMART integration (PRODUCT.md §4). Slider maths: web/src/business/model.ts. */
const eur = (v: number) => `${v < 0 ? '−' : ''}${Math.abs(v) >= 1e6 ? `€${(Math.abs(v) / 1e6).toFixed(2)} M` : `€${Math.round(Math.abs(v)).toLocaleString('en')}`}`
const LEVER: Record<string, string> = {
  pricing_risk: 'Operator: pricing risk removed', avoidable_trips: 'Customer: avoidable half-empty visits',
  expensive_tonnes: 'Customer: tonnes priced above peers', invoice_differences: 'Customer: invoice above contract',
  contamination: 'Customer: wrong material in the compactor', contract_visibility: 'Customer: is the contract kept?',
}

function Slider(props: { label: string; value: number; min: number; max: number; step: number; fmt: (v: number) => string; onChange: (v: number) => void }) {
  return (
    <label className="block text-sm text-slate-600">
      <span className="flex justify-between"><span>{props.label}</span><span className="font-medium tabular-nums text-slate-900">{props.fmt(props.value)}</span></span>
      <input type="range" className="w-full accent-teal-700" min={props.min} max={props.max} step={props.step} value={props.value}
        onChange={(e) => props.onChange(Number(e.target.value))} />
    </label>
  )
}

function Box({ title, lines, tone = 'slate' }: { title: string; lines: string[]; tone?: 'slate' | 'teal' | 'violet' | 'amber' }) {
  const c = { slate: 'border-slate-300 bg-white', teal: 'border-teal-600 bg-teal-50', violet: 'border-violet-300 bg-violet-50', amber: 'border-amber-300 bg-amber-50' }[tone]
  return (
    <div className={`rounded-lg border-2 p-3 text-sm ${c}`}>
      <div className="font-semibold text-slate-900">{title}</div>
      <ul className="mt-1 list-disc pl-4 text-slate-600">{lines.map((l) => <li key={l}>{l}</li>)}</ul>
    </div>
  )
}

const LIFT_ORDER = {
  schema: 'fullload.lift_order.v1 (illustrative)', synthetic: true, device_id: 'CMP-00280', operator_id: 'OP-E',
  trigger: 'WEIGHT', estimated_net_kg: 1850, sigma_kg: 63, fill_pct: 86, window: { earliest: '2026-11-10T06:00', latest: '2026-11-11T18:00' },
  billing_basis: "operator's certified weighbridge", fee_basis: 'verified tonnes (cross-checked against the weighbridge ticket)',
}

export function Beat6() {
  const b = bundle.business
  const v = bundle.value_per_device
  const [p, setP] = useState<BizParams>(b.params)
  const set = (k: keyof BizParams) => (x: number) => setP({ ...p, [k]: x })
  const r = useMemo(() => simulateBusiness(p), [p])
  const h1 = b.installed_cost_ranges.H1_factory_fit
  return (
    <section className="space-y-6">
      <header>
        <div className="text-sm font-medium uppercase tracking-wide text-teal-700">The business</div>
        <h1 className="text-4xl font-bold text-slate-900">Operators pay. Customers get it free. Europress sells more machines.</h1>
        <p className="mt-2 text-lg text-slate-600">Europress funds the weighing; the network's coverage is what creates the value.</p>
      </header>

      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="mb-3 text-sm text-slate-500">Value per device per year, from our pipeline vs the business team's independent estimate (fleet averages, synthetic; do not add up — levers overlap)</div>
        <table className="w-full text-sm tabular-nums">
          <thead className="text-left text-slate-500"><tr><th className="py-1">Value</th><th>Needs the weight?</th><th>Our pipeline</th><th>Business team</th></tr></thead>
          <tbody>
            {v.rows.map((row) => (
              <tr key={row.lever} className="border-t border-slate-100 align-top">
                <td className="py-1 pr-2">{LEVER[row.lever] ?? row.lever}</td>
                <td className="pr-2 text-slate-600">{row.needs_weight}</td>
                <td className="pr-2">
                  {row.ours ? (row.ours_range ? `€${row.ours_range[0].toLocaleString('en')}–${row.ours_range[1].toLocaleString('en')}` : `€${row.ours.value?.toLocaleString('en')}`) : <span className="text-slate-400">{row.note}</span>}
                  {row.ours && <span className="ml-2 rounded bg-slate-100 px-1.5 text-xs text-slate-600">{row.ours.tag}</span>}
                </td>
                <td>{row.team !== null ? `€${row.team.toLocaleString('en')}` : '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="mt-2 text-xs text-slate-500">{v.note}</p>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="space-y-3 rounded-xl border border-slate-200 bg-white p-5 shadow-sm lg:col-span-2">
          <div className="flex items-center justify-between">
            <div className="text-sm font-medium text-slate-900">Europress, {p.devices_total.toLocaleString('en')} devices</div>
            <span className="rounded bg-rose-100 px-2 py-0.5 text-xs font-medium text-rose-800">hypothetical</span>
          </div>
          <div className="grid gap-3 sm:grid-cols-3">
            {[
              ['Weighing investment (one-off)', eur(r.investment)],
              ['Service revenue / year', eur(r.service_revenue)],
              ['Extra machine sales margin / year', eur(r.extra_sales_margin)],
              ['Operating cost / year', eur(-r.opex)],
              ['Net / year', eur(r.net_per_year)],
              ['Payback', r.payback_years === null ? 'never' : `${r.payback_years.toFixed(1)} years`],
            ].map(([k, val]) => (
              <div key={k} className="rounded-lg bg-slate-50 p-3"><div className="text-xs text-slate-500">{k}</div><div className="text-2xl font-semibold tabular-nums">{val}</div></div>
            ))}
          </div>
          <p className="text-sm text-slate-600">
            Customer pays: <b>€0</b>. Fee per covered device: {eur(r.fee_per_device_year)}/year. Over {p.horizon_years} years: {eur(r.cumulative_net_horizon)} after the investment.
          </p>
        </div>
        <div className="space-y-3 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="inline-flex rounded-lg border border-slate-300 p-1 text-xs font-medium">
            {(['per_device_month', 'per_tonne'] as const).map((m) => (
              <button key={m} type="button" onClick={() => setP({ ...p, fee_mode: m })}
                className={`rounded-md px-3 py-1 ${p.fee_mode === m ? 'bg-teal-700 text-white' : 'text-slate-600'}`}>{m === 'per_device_month' ? 'fee per device' : 'fee per tonne'}</button>
            ))}
          </div>
          {p.fee_mode === 'per_device_month'
            ? <Slider label="Fee per device / month" value={p.fee_eur_per_device_month} min={0} max={60} step={1} fmt={(x) => `€${x}`} onChange={set('fee_eur_per_device_month')} />
            : <Slider label="Fee per verified tonne" value={p.fee_eur_per_t} min={0} max={10} step={0.5} fmt={(x) => `€${x.toFixed(1)}`} onChange={set('fee_eur_per_t')} />}
          <Slider label="Devices with a paying operator" value={p.paying_coverage} min={0.1} max={1} step={0.05} fmt={(x) => `${Math.round(100 * x)} %`} onChange={set('paying_coverage')} />
          <Slider label="Hopper weighing cost / device" value={p.h1_cost_eur} min={0} max={h1[1]} step={50} fmt={(x) => `€${x.toLocaleString('en')}`} onChange={set('h1_cost_eur')} />
          <Slider label="Devices with hopper weighing" value={p.h1_share} min={0} max={1} step={0.05} fmt={(x) => `${Math.round(100 * x)} %`} onChange={set('h1_share')} />
          <Slider label="Extra machine sales" value={p.sales_growth} min={0} max={0.15} step={0.01} fmt={(x) => `+${Math.round(100 * x)} %`} onChange={set('sales_growth')} />
          <p className="text-xs text-slate-500">Hopper cost: business team €500; Part 1 installed cost (factory-fit) €{h1[0].toLocaleString('en')}–{h1[1].toLocaleString('en')}.</p>
          <button type="button" onClick={() => setP(b.params)} className="text-xs text-slate-500 underline">reset</button>
        </div>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="mb-3 text-sm font-medium text-slate-900">How it plugs into SMART</div>
        <div className="grid items-start gap-3 lg:grid-cols-[1fr_auto_1.2fr_auto_1fr]">
          <div className="space-y-3">
            <Box title="Compactor (Europress)" lines={['fill level, ram pressure, cycles (today)', 'weight: virtual + hopper plate (new)']} />
            <Box title="Operator weighbridge (optional)" lines={['shared tickets', 'used only to calibrate and cross-check']} tone="amber" />
          </div>
          <div className="self-center text-2xl text-slate-400">→</div>
          <Box title="SMART cloud + FullLoad engine" tone="teal" lines={['fleet self-calibration of every sensor', 'site tonnage forecasts (±10 %)', 'weight-triggered lift orders', 'contract and invoice cross-check', 'AI-summarized customer reports (numbers checked)']} />
          <div className="self-center text-2xl text-slate-400">→</div>
          <div className="space-y-3">
            <Box title="Operators (paying)" tone="violet" lines={['forecast API to price per kg', 'lift orders when full', 'fee per verified tonne / device']} />
            <Box title="Customers (free)" lines={['report: what happened, what to decide', 'is the contract kept?', 'tender proposal — human approves']} />
          </div>
        </div>
        <pre className="mt-4 max-h-56 overflow-auto rounded bg-slate-900 p-3 text-xs text-slate-100">{JSON.stringify(LIFT_ORDER, null, 2)}</pre>
        <p className="mt-1 text-xs text-slate-500">Example lift order to an operator (illustrative; extends the starter kit's smve.recommendation.v0 mock). Billing stays on the certified weighbridge.</p>
      </div>
    </section>
  )
}
