import type { Figure } from './bundle'

/** Display a Figure's value in its unit. */
export function format(f: Figure): string {
  if (f.value === null) return 'cannot be computed'
  const n = f.value
  if (f.unit === 'EUR') return n >= 1e6 ? `€${(n / 1e6).toFixed(2)} M` : `€${Math.round(n).toLocaleString('en')}`
  if (f.unit === 'EUR/t') return `€${n.toFixed(2)}/t`
  if (f.unit === '%') return `${n.toFixed(1)} %`
  if (f.unit === 't') return `${Math.round(n).toLocaleString('en')} t`
  return n.toLocaleString('en')
}
