// Types for web/public/data/bundle.json, written by `fullload build` (pipeline/fullload/export.py).
// Keep in sync with the pipeline: change schema_version on both sides together.
import raw from '../public/data/bundle.json'

export type Tag = 'observed' | 'estimated' | 'simulated' | 'hypothetical'

export interface Figure {
  value: number | null
  unit: string
  tag: Tag
  formula: string
  sources: string[]
  sigma: number | null
  row_ids: string[]
  assumptions: string[]
}

export interface Fleet {
  devices: Figure
  devices_with_weighing: Figure
  gross_charges_eur: Figure
  trip_charges_eur: Figure
  trip_share_pct: Figure
  tonne_charges_eur: Figure
  tonnes_per_year: Figure
  low_fill_lift_share_pct: Figure
  fill_at_lift_histogram: { bin_pct: number; lifts: number }[]
  fill_by_trigger: { trigger_type: string; lifts: number; median_fill_pct: number }[]
}

export interface Market {
  region: string
  operators: string[]
  sigma_inc: number
  sigma_ent: number
  params: import('./market/model').Params
  inputs: import('./market/model').Account[]
  headline: Record<string, Figure>
}

export interface HeroLift { date: string; device_id: string; fill_pct: number | null; kg: number | null; trigger: string; flagged: boolean }
export interface HeroDevice { device_id: string; site: string; material: string; policy: string; schedule_per_week: number | null;
  container_m3: number; equipment: string; lifts: number; weight_triggered_lifts: number; tonnes: number; median_fill_at_lift_pct: number | null }
export interface Hero {
  customer_id: string
  customer_name: string
  sector: string
  region: string
  devices: HeroDevice[]
  lifts: HeroLift[]
  figures: Record<string, Figure>
  facts: Record<string, number | string>
  report: { status: string; text: string | null; label?: string; unmatched_numbers?: string[] }
  proposal: Record<string, unknown>
  operator_view: {
    devices: { device_id: string; actual_t_per_month: number; own_forecast_t_per_month: number; peer_forecast_t_per_month: number; own_error_pct: number; peer_error_pct: number }[]
    own_error_median_pct: number
    peer_error_median_pct: number
    sigma_inc: number
    sigma_ent: number
    price_today_eur: number
    bids_before_eur: Record<string, number>
    bids_after_eur: Record<string, number>
    incumbent: string
    winner_after: string
    price_after_eur: number
  }
}

export interface Bundle {
  schema_version: 1
  provenance: { kit_version: string; data: string; synthetic: boolean }
  fleet: Fleet
  forecast: Record<string, unknown>
  trips: Record<string, unknown>
  market: Market
  hero: Hero
}

// Statically imported so the demo has no runtime fetch. The pipeline test checks tags and sources.
export const bundle = raw as unknown as Bundle
