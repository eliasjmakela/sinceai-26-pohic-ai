// TypeScript mirror of pipeline/fullload/market.py `simulate` (the Python file is the reference and documents the
// model). Keep both in step: `npm run parity` checks this file against the cases the pipeline writes into the bundle.

export interface Account {
  customer_id: string
  incumbent: string
  devices: number
  trip_cents: number
  tonne_cents: number
  actual_lifts: number
  weight_lifts: number
  kg: number
}

export interface Params {
  cost_share: number
  min_margin: number
  risk_z: number
  new_entrants: number
  entrant_cost_advantage: number
  cost_spread: number
  density_benefit: number
  europress_fee_cents_per_t: number
  sigma_sensor: number
}

export interface Row {
  customer_id: string
  incumbent: string
  tonnes: number
  lifts_before: number
  lifts_after: number
  price_before: number
  contestable_today: boolean
  contestable_after: boolean
  winner_after: string
  price_after: number
  keeps_today: boolean
  operator_margin_before: number
  operator_margin_after: number
  europress_fee: number
}

export interface Summary {
  accounts: number
  tonnes: number
  customer_cost_before: number
  customer_cost_after: number
  cost_per_t_before: number
  cost_per_t_after: number
  lifts_before: number
  lifts_after: number
  t_per_lift_before: number
  t_per_lift_after: number
  share_before: Record<string, number>
  share_after: Record<string, number>
  hhi_before: number
  hhi_after: number
  accounts_switched: number
  accounts_contestable_today: number
  accounts_contestable_after: number
  accounts_keep_today: number
  operator_margin_before: number
  operator_margin_after: number
  europress_fee: number
}

export function fnv1a(text: string): number {
  let h = 0x811c9dc5
  for (const b of new TextEncoder().encode(text)) {
    h = Math.imul(h ^ b, 0x01000193) >>> 0
  }
  return h >>> 0
}

export function routeFit(operator: string, customerId: string): number {
  return (2 * fnv1a(`${operator}|${customerId}`)) / 2 ** 32 - 1
}

const sum = (xs: number[]) => xs.reduce((a, b) => a + b, 0)

export function simulate(accs: Account[], operators: string[], sigmaInc: number, sigmaEnt: number, p: Params) {
  const entrants = Array.from({ length: p.new_entrants }, (_, i) => `NEW-${i + 1}`)
  const sigmaAfter = Math.sqrt(sigmaInc ** 2 + p.sigma_sensor ** 2)
  const totalKg = sum(accs.map((a) => a.kg))
  const density: Record<string, number> = {}
  for (const o of [...operators, ...entrants]) density[o] = 0
  for (const a of accs) density[a.incumbent] += a.kg / totalKg

  const rows: Row[] = accs.map((a) => {
    const today = a.trip_cents + a.tonne_cents
    const t = a.kg / 1000
    const challengers = [...operators.filter((o) => o !== a.incumbent), ...entrants]
    const eff = (o: string) => {
      const base = o.startsWith('NEW-') ? 1 - p.entrant_cost_advantage : 1.0
      return base * (1 + p.cost_spread * routeFit(o, a.customer_id)) * (1 - p.density_benefit * density[o])
    }
    const rel: Record<string, number> = {}
    for (const o of [a.incumbent, ...challengers]) rel[o] = eff(o) / eff(a.incumbent)

    const costBefore = p.cost_share * today
    const bidsBefore = challengers.map((o) => costBefore * rel[o] * (1 + p.min_margin) * (1 + p.risk_z * sigmaEnt))
    const bestChallengerBefore = bidsBefore.length ? Math.min(...bidsBefore) : Infinity

    const costAfter =
      p.cost_share * ((a.trip_cents * a.weight_lifts) / a.actual_lifts + a.tonne_cents) + p.europress_fee_cents_per_t * t
    const bidsAfter: [string, number][] = [a.incumbent, ...challengers].map((o) => [
      o,
      costAfter * rel[o] * (1 + p.min_margin) * (1 + p.risk_z * sigmaAfter),
    ])
    const ranked = [...bidsAfter].sort(
      (x, y) =>
        x[1] - y[1] ||
        Number(x[0] !== a.incumbent) - Number(y[0] !== a.incumbent) ||
        (x[0] < y[0] ? -1 : x[0] > y[0] ? 1 : 0),
    )
    let [winner, winBid] = ranked[0]
    const second = ranked.length > 1 ? ranked[1][1] : today
    const challengerBids = bidsAfter.filter(([o]) => o !== a.incumbent).map(([, b]) => b)
    const bestChallengerAfter = challengers.length ? Math.min(...challengerBids) : Infinity
    const keepsToday = winBid > today
    const priceAfter = keepsToday ? today : Math.max(winBid, Math.min(second, today))
    if (keepsToday) winner = a.incumbent
    return {
      customer_id: a.customer_id,
      incumbent: a.incumbent,
      tonnes: t,
      lifts_before: a.actual_lifts,
      price_before: today,
      contestable_today: bestChallengerBefore < today,
      contestable_after: bestChallengerAfter < today,
      winner_after: winner,
      price_after: priceAfter,
      keeps_today: keepsToday,
      lifts_after: keepsToday ? a.actual_lifts : a.weight_lifts,
      operator_margin_before: today - costBefore,
      operator_margin_after: keepsToday ? today - costBefore : priceAfter - costAfter * rel[winner],
      europress_fee: keepsToday ? 0 : p.europress_fee_cents_per_t * t,
    }
  })
  return { rows, summary: summarise(rows, [...operators, ...entrants]), sigmaAfter }
}

const hhi = (shares: Record<string, number>) => sum(Object.values(shares).map((s) => (100 * s) ** 2))

export function summarise(rows: Row[], allOps: string[]): Summary {
  const t = sum(rows.map((r) => r.tonnes))
  const share = (key: 'incumbent' | 'winner_after') => {
    const out: Record<string, number> = {}
    for (const o of allOps) out[o] = 0
    for (const r of rows) out[r[key]] += r.tonnes / t
    return out
  }
  const before = share('incumbent')
  const after = share('winner_after')
  const pb = sum(rows.map((r) => r.price_before))
  const pa = sum(rows.map((r) => r.price_after))
  const lb = sum(rows.map((r) => r.lifts_before))
  const la = sum(rows.map((r) => r.lifts_after))
  const count = (f: (r: Row) => boolean) => rows.filter(f).length
  return {
    accounts: rows.length,
    tonnes: t,
    customer_cost_before: pb,
    customer_cost_after: pa,
    cost_per_t_before: pb / t,
    cost_per_t_after: pa / t,
    lifts_before: lb,
    lifts_after: la,
    t_per_lift_before: t / lb,
    t_per_lift_after: t / la,
    share_before: before,
    share_after: after,
    hhi_before: hhi(before),
    hhi_after: hhi(after),
    accounts_switched: count((r) => r.winner_after !== r.incumbent),
    accounts_contestable_today: count((r) => r.contestable_today),
    accounts_contestable_after: count((r) => r.contestable_after),
    accounts_keep_today: count((r) => r.keeps_today),
    operator_margin_before: sum(rows.map((r) => r.operator_margin_before)),
    operator_margin_after: sum(rows.map((r) => r.operator_margin_after)),
    europress_fee: sum(rows.map((r) => r.europress_fee)),
  }
}
