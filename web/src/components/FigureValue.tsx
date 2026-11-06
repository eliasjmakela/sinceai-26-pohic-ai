import { useState } from 'react'
import type { Figure } from '../bundle'

const TAG_STYLE: Record<Figure['tag'], string> = {
  observed: 'bg-emerald-100 text-emerald-800',
  estimated: 'bg-sky-100 text-sky-800',
  simulated: 'bg-amber-100 text-amber-800',
  hypothetical: 'bg-rose-100 text-rose-800',
}

export function format(f: Figure): string {
  if (f.value === null) return 'cannot be computed'
  const n = f.value
  if (f.unit === 'EUR') return `€${(n / 1e6).toFixed(2)} M`
  if (f.unit === '%') return `${n.toFixed(1)} %`
  if (f.unit === 't') return `${Math.round(n).toLocaleString('en')} t`
  return n.toLocaleString('en')
}

/** A number with its evidence tag; click opens the receipt (formula, sources, assumptions). */
export function FigureValue({ figure, label }: { figure: Figure; label: string }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <button type="button" onClick={() => setOpen(!open)} className="w-full text-left">
        <div className="text-sm text-slate-500">{label}</div>
        <div className="mt-1 text-4xl font-semibold tabular-nums text-slate-900">
          {format(figure)}
          {figure.sigma !== null && <span className="ml-2 text-lg text-slate-500">± {figure.sigma}</span>}
        </div>
        <span className={`mt-2 inline-block rounded px-2 py-0.5 text-xs font-medium ${TAG_STYLE[figure.tag]}`}>
          {figure.tag}
        </span>
      </button>
      {open && (
        <dl className="mt-3 space-y-1 border-t border-slate-100 pt-3 text-xs text-slate-600">
          <dt className="font-medium">Formula</dt>
          <dd>{figure.formula}</dd>
          <dt className="font-medium">Sources</dt>
          <dd>{figure.sources.join(', ')}</dd>
          {figure.assumptions.length > 0 && (
            <>
              <dt className="font-medium">Assumptions</dt>
              <dd>
                <ul className="list-disc pl-4">
                  {figure.assumptions.map((a) => <li key={a}>{a}</li>)}
                </ul>
              </dd>
            </>
          )}
        </dl>
      )}
    </div>
  )
}
