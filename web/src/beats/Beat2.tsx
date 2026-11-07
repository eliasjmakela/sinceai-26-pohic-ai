import { useState } from 'react'
import { CartesianGrid, ReferenceLine, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis } from 'recharts'
import { bundle } from '../bundle'
import { FigureValue } from '../components/FigureValue'
import { Markdownish } from '../components/Markdownish'

/** Beat 2 — the customer's free view (PRODUCT.md §4). */
export function Beat2() {
  const h = bundle.hero
  const [approved, setApproved] = useState<string | null>(null)
  const pts = h.lifts.filter((l) => l.fill_pct !== null).map((l) => ({ x: Date.parse(l.date), y: l.fill_pct, ...l }))
  const low = pts.filter((p) => (p.y ?? 0) < 60)
  const ok = pts.filter((p) => (p.y ?? 0) >= 60)
  const fmtDate = (t: number) => new Date(t).toLocaleDateString('en-GB', { month: 'short' })
  return (
    <section className="space-y-6">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="text-sm font-medium uppercase tracking-wide text-teal-700">Customer view · free</div>
          <h1 className="text-4xl font-bold text-slate-900">{h.customer_name}</h1>
          <p className="mt-2 text-lg text-slate-600">{h.devices.length} compactors in region {h.region}. One year, every visit.</p>
        </div>
      </header>

      <div className="grid gap-4 sm:grid-cols-4">
        <FigureValue figure={h.figures.lifts} label="truck visits in 12 months" />
        <FigureValue figure={h.figures.low_fill_share_pct} label="of visits emptied a container under 60 % full" />
        <FigureValue figure={h.figures.cost_per_t_today} label="paid per tonne today" />
        <FigureValue figure={h.figures.cost_per_t_after} label="per tonne in a per-kg tender" />
      </div>

      <div className="grid gap-4 lg:grid-cols-5">
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm lg:col-span-3">
          <div className="mb-3 text-sm text-slate-500">How full each container was when the truck came</div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ left: -10, right: 10 }}>
                <CartesianGrid stroke="#e2e8f0" />
                <XAxis type="number" dataKey="x" domain={['dataMin', 'dataMax']} tickFormatter={fmtDate} tick={{ fontSize: 12 }} />
                <YAxis type="number" dataKey="y" domain={[0, 100]} unit=" %" tick={{ fontSize: 12 }} />
                <ReferenceLine y={60} stroke="#94a3b8" strokeDasharray="4 4" />
                <Tooltip formatter={(v) => `${v}`} labelFormatter={() => ''} />
                <Scatter data={ok} fill="#0f766e" isAnimationActive={false} name="60 % full or more" />
                <Scatter data={low} fill="#d97706" isAnimationActive={false} name="under 60 % full" />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-2 flex gap-4 text-xs text-slate-500">
            <span><span className="mr-1 inline-block h-2 w-2 rounded-full bg-teal-700" />60 % full or more</span>
            <span><span className="mr-1 inline-block h-2 w-2 rounded-full bg-amber-600" />under 60 % full</span>
          </div>
        </div>

        <div className="rounded-xl border border-violet-200 bg-violet-50/50 p-5 shadow-sm lg:col-span-2">
          <div className="mb-3 flex items-center justify-between gap-2">
            <div className="text-sm font-medium text-slate-900">Your waste report</div>
            <span className="rounded bg-violet-100 px-2 py-0.5 text-xs font-medium text-violet-800">AI-summarized</span>
          </div>
          {h.report.text ? <Markdownish text={h.report.text} /> : <p className="text-slate-500">No report.</p>}
          <p className="mt-4 border-t border-violet-100 pt-3 text-xs text-slate-500">
            {h.report.label} · check: {h.report.status === 'checked' ? 'all numbers match the data ✓' : `unmatched: ${h.report.unmatched_numbers?.join(', ')}`}
          </p>
        </div>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="text-sm font-medium text-slate-900">Proposal: tender your collection on per-kg terms</div>
            <div className="text-sm text-slate-600">
              Weight-triggered lifts, a per-kg price, billing on the certified weighbridge as today. Requires your approval; nothing is sent automatically.
            </div>
          </div>
          {approved ? (
            <button type="button" onClick={() => setApproved(null)} className="text-sm text-slate-500 underline">reset demo</button>
          ) : (
            <button type="button" onClick={() => setApproved(new Date().toISOString())}
              className="rounded-lg bg-teal-700 px-5 py-2 font-medium text-white">Approve tender brief</button>
          )}
        </div>
        {approved && (
          <div className="mt-4 grid gap-4 lg:grid-cols-3">
            <div className="text-sm text-slate-600">
              <div className="font-medium text-slate-900">Audit log</div>
              <div>Approved by: facility manager (demo)</div>
              <div>Action: TENDER_PER_KG, draft brief created</div>
              <div>Reversal: keep today's contract; a tender only invites bids</div>
            </div>
            <pre className="max-h-64 overflow-auto rounded bg-slate-900 p-3 text-xs text-slate-100 lg:col-span-2">
              {JSON.stringify(h.proposal, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </section>
  )
}
