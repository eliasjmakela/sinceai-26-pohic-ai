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

export interface Bundle {
  schema_version: 1
  provenance: { kit_version: string; data: string; synthetic: boolean }
  fleet: Fleet
  forecast: Record<string, unknown>
  trips: Record<string, unknown>
  market: Market
}

// Statically imported so the demo has no runtime fetch. The pipeline test checks tags and sources.
export const bundle = raw as unknown as Bundle
