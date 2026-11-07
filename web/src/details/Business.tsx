import { useMemo, useState } from 'react'
import { bundle } from '../bundle'
import { cashFlows, summarise, type PricingParams } from '../pricing/model'
import { Slider } from '../components/ui'

/** Detail: the business, the fee decision and the SMART integration (PRICING.md). Slider maths: web/src/pricing/model.ts. */
const eur = (v: number) => `${v < 0 ? '−' : ''}${Math.abs(v) >= 1e6 ? `€${(Math.abs(v) / 1e6).toFixed(2)} M` : `€${Math.round(Math.abs(v)).toLocaleString('en')}`}`
const LEVER: Record<string, string> = {
  pricing_risk: 'Operator: pricing risk removed', avoidable_trips: 'Customer: avoidable half-empty visits',
  expensive_tonnes: 'Customer: tonnes priced above peers', invoice_differences: 'Customer: invoice above contract',
  contamination: 'Customer: wrong material in the compactor', contract_visibility: 'Customer: is the contract kept?',
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
  schema: 'openweight.lift_order.v1 (illustrative)', synthetic: true, device_id: 'CMP-00280', operator_id: 'OP-E',
  trigger: 'WEIGHT', estimated_net_kg: 1850, sigma_kg: 63, fill_pct: 86, window: { earliest: '2026-11-10T06:00', latest: '2026-11-11T18:00' },
  billing_basis: "operator's certified weighbridge", fee_basis: 'per weighed device per month (not per tonne)',
}

export function Business() {
  const pr = bundle.pricing
  const v = bundle.value_per_device
  const [p, setP] = useState<PricingParams>(pr.params)
  const [fee, setFee] = useState(pr.recommended_fee_eur_per_month)
  const set = (k: keyof PricingParams) => (x: number) => setP({ ...p, [k]: x })
  const cfs = useMemo(() => cashFlows(p, fee), [p, fee])
  const r = useMemo(() => summarise(cfs, p.discount_rate), [cfs, p.discount_rate])
  const [capLo, capHi] = pr.h7_cost.capex_eur
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
            <div className="text-sm font-medium text-slate-900">Europress over {p.years} years: H7 on every new compactor ({p.new_units_per_year.toLocaleString('en')} a year)</div>
            <span className="rounded bg-rose-100 px-2 py-0.5 text-xs font-medium text-rose-800">hypothetical</span>
          </div>
          <div className="grid gap-3 sm:grid-cols-4">
            {[
              [`NPV at ${Math.round(100 * p.discount_rate)} %`, eur(r.npv_eur)],
              ['Pays back in', r.payback_year === null ? 'never' : `year ${r.payback_year}`],
              ['Deepest cash position', eur(r.deepest_eur)],
              [`Cumulative, year ${p.years}`, eur(r.cumulative_eur)],
            ].map(([k, val]) => (
              <div key={k} className="rounded-lg bg-slate-50 p-3"><div className="text-xs text-slate-500">{k}</div><div className="text-2xl font-semibold tabular-nums">{val}</div></div>
            ))}
          </div>
          <div className="flex h-24 items-end gap-1" aria-label="Cash flow per year">
            {cfs.map((c, i) => {
              const m = Math.max(...cfs.map(Math.abs)) || 1
              return (
                <div key={i} className="flex h-full flex-1 flex-col justify-center">
                  <div className="flex h-1/2 items-end"><div className="w-full rounded-t bg-teal-700" style={{ height: `${c > 0 ? (100 * c) / m : 0}%` }} /></div>
                  <div className="flex h-1/2 items-start"><div className="w-full rounded-b bg-rose-600" style={{ height: `${c < 0 ? (-100 * c) / m : 0}%` }} /></div>
                </div>
              )
            })}
          </div>
          <p className="text-sm text-slate-600">
            Customer pays <b>€0</b>. Cash flow per year above; the model is the team document's (LIITE §6.3), with the H7 cost from Part 1.
            Break-even fee with Part 1's mid cost: €{pr.scenarios['base (Part 1 installed cost)'].break_even_fee}/month; at €{pr.recommended_fee_eur_per_month} the H7 must cost
            at most €{pr.max_h7_capex_eur[String(pr.recommended_fee_eur_per_month)]?.toLocaleString('en')}.
          </p>
        </div>
        <div className="space-y-3 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <Slider label="Operator fee per device / month" value={fee} min={10} max={60} step={1} fmt={(x) => `€${x}`} onChange={setFee} />
          <Slider label="H7 cost per new unit (capex)" value={p.h7_capex_eur} min={500} max={capHi} step={25} fmt={(x) => `€${x.toLocaleString('en')}`} onChange={set('h7_capex_eur')} />
          <Slider label="Weighed units with a paying operator" value={p.adoption} min={0.2} max={1} step={0.05} fmt={(x) => `${Math.round(100 * x)} %`} onChange={set('adoption')} />
          <Slider label="Tender package price" value={p.package_eur} min={0} max={1000} step={50} fmt={(x) => `€${x}`} onChange={set('package_eur')} />
          <Slider label="Extra machine sales" value={p.sales_growth} min={0} max={0.15} step={0.01} fmt={(x) => `+${Math.round(100 * x)} %`} onChange={set('sales_growth')} />
          <p className="text-xs text-slate-500">H7 capex (Part 1, factory fit, without the 6-year upkeep): €{capLo.toLocaleString('en')}–{capHi.toLocaleString('en')}; team document €825.</p>
          <button type="button" onClick={() => { setP(pr.params); setFee(pr.recommended_fee_eur_per_month) }} className="text-xs text-slate-500 underline">reset</button>
        </div>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="mb-3 text-sm font-medium text-slate-900">How it plugs into SMART</div>
        <div className="grid items-start gap-3 lg:grid-cols-[1fr_auto_1.2fr_auto_1fr]">
          <div className="space-y-3">
            <Box title="Compactor (Europress)" lines={['fill level, ram pressure, cycles (today)', 'weight: hydraulic self-lift on every new unit']} />
            <Box title="Operator weighbridge (optional)" lines={['shared tickets', 'used only to calibrate and cross-check']} tone="amber" />
          </div>
          <div className="self-center text-2xl text-slate-400">→</div>
          <Box title="SMART cloud + OpenWeight engine" tone="teal" lines={['fleet self-calibration of every sensor', 'site tonnage forecasts (±10 %)', 'weight-triggered lift orders', 'contract and invoice cross-check', 'AI-summarized customer reports (numbers checked)']} />
          <div className="self-center text-2xl text-slate-400">→</div>
          <div className="space-y-3">
            <Box title="Operators (paying)" tone="violet" lines={['forecast API to price per kg', 'lift orders when full', 'fee per weighed device per month']} />
            <Box title="Customers (free)" lines={['report: what happened, what to decide', 'is the contract kept?', 'tender proposal — human approves']} />
          </div>
        </div>
        <pre className="mt-4 max-h-56 overflow-auto rounded bg-slate-900 p-3 text-xs text-slate-100">{JSON.stringify(LIFT_ORDER, null, 2)}</pre>
        <p className="mt-1 text-xs text-slate-500">Example lift order to an operator (illustrative; extends the starter kit's smve.recommendation.v0 mock). Billing stays on the certified weighbridge.</p>
      </div>
    </section>
  )
}
