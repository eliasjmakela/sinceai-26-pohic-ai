"""FullLoad premature-lift rule (Task B, family PREMATURE_UNJUSTIFIED). Public tables only, no labels.

A lift is flagged as an *unjustified premature lift* when the container was emptied while it held little
material, and nothing public explains the early lift. "Little material" is measured by **weight first**:

  load share = device_estimated_collected_kg / the device's typical full payload
  (full payload as in `trips.py`: median of collected kg x 100 / fill % over the device's own lifts with
  fill >= 40 %; devices with fewer than 3 such lifts have no payload)

  low load   = load share < LOW_LOAD_SHARE,
               or, only where no load share exists (no device weight or no payload), fill before lift < LOW_FILL_PCT

Arms, one per way an early lift happens (original_trigger_type, so rescheduled lifts keep their reason):
  1. SCHEDULED    low load, and the device is not already at the slowest schedule its material's maximum
                  interval allows (then the lift is required: hygiene / fire safety; same test as kit B2)
  2. ON_CALL_ORDER  load share < LOW_LOAD_SHARE although the fill sensor triggered the order: the weight shows the
                  fill reading was high while the container was not (e.g. bridging). Needs a device weight; the fill
                  fallback is not used here because the fill reading is what is in doubt.
  3. (variant, OFF by default) CUSTOMER_REQUEST on an on-call device, low load, and the site is closed the next day
                  (weekend or a closure in `site_calendar`): a "to be safe" order before a closure. It is off because
                  some customer requests are justified for reasons the public data cannot show (the challenge asks not
                  to flag explained early lifts); on the TRAIN period it adds recall but flags 13 explained lifts.
                  `INCLUDE_PRE_CLOSURE_REQUESTS` switches it on; validate.py scores both.
Never flagged (they explain an early lift): MAX_INTERVAL_RULE, CUSTOMER_REQUEST_PRE_CLOSURE, DECOMMISSION,
AD_HOC_CUSTOMER (e.g. after an overflow); scheduled lifts at the minimum allowed frequency.

Thresholds (constants, no search; arm 3 on/off was decided on the train period, never on validation):
  LOW_LOAD_SHARE = 0.40 -- the kit B2 rule's 40 % fill cut, applied to weight instead of fill (the one choice).
  LOW_FILL_PCT   = 40   -- the same cut, used only as the fallback when there is no device weight.

Limitations: the payload is the device's typical payload over the whole visible window (a production version
would use a trailing window); the default rule cannot see precautionary customer requests (arm 3 is the
trade-off); device weight carries sensor drift, and a payload can be under-estimated for a device that is
almost always lifted early. A flag is a prompt for a human, not a finding of fault.
"""
from __future__ import annotations

import duckdb
import numpy as np
import pandas as pd

from .figures import Figure
from .trips import MIN_PAYLOAD_LIFTS, device_trips

LOW_LOAD_SHARE = 0.40   # kit B2's 40 % fill cut, applied to the device weight (one documented choice, not tuned)
LOW_FILL_PCT = 40       # same cut on fill; fallback only where no device weight / payload exists
EXPLAINED_TRIGGERS = ("MAX_INTERVAL_RULE", "CUSTOMER_REQUEST_PRE_CLOSURE", "DECOMMISSION", "AD_HOC_CUSTOMER")
SCHEDULE_OPTIONS_PER_WEEK = (5.0, 3.0, 2.0, 1.0, 0.5, 0.25)   # schedule frequencies offered (as in kit B2)
INCLUDE_PRE_CLOSURE_REQUESTS = False   # arm 3 off: it flags justified customer requests too (see docstring)
FAMILY = "PREMATURE_UNJUSTIFIED"
ARMS = ("SCHEDULED_LOW_LOAD", "ORDER_WEIGHT_LOW", "PRE_CLOSURE_REQUEST")

RULE = ("Flag a lift when the device weight shows a load under 40 % of the device's typical full payload "
        "(fill under 40 % where no weight exists) and no public reason explains it: scheduled lifts above the "
        "minimum frequency, and fill-triggered orders whose weight stays low. Maximum-interval, pre-closure, "
        "decommission, ad-hoc and customer-requested lifts are not flagged.")
SOURCES = ("collection_events.device_estimated_collected_kg", "collection_events.device_fill_pct_before",
           "collection_events.original_trigger_type", "collection_events.status", "collection_events.actual_at",
           "devices.collection_policy", "devices.fixed_schedule_per_week",
           "material_classes.max_days_between_collections", "site_calendar.is_open")
ASSUMPTIONS = ("Typical full payload from the device's own lifts with fill >= 40 % (see trips model)",
               "A flag is a prompt for human review, not a finding against the operator or the customer",
               "Customer-requested lifts are not flagged: they can have reasons the data cannot show")


def lift_features(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """One row per completed or partial lift with the rule's inputs. Sorted by collection_id."""
    f = con.execute("""
        SELECT c.collection_id, c.device_id, c.site_id, c.operator_id, c.status, c.original_trigger_type,
               c.device_fill_pct_before, c.device_estimated_collected_kg, c.actual_at,
               d.collection_policy, d.fixed_schedule_per_week, d.material_stream, m.max_days_between_collections,
               coalesce(NOT s.is_open, false) OR dayofweek(CAST(timezone('Europe/Helsinki', c.actual_at) AS DATE) + 1) IN (0, 6)
                   AS closed_next_day
        FROM collection_events c
        JOIN devices d USING (device_id) JOIN material_classes m USING (material_stream)
        LEFT JOIN site_calendar s ON s.site_id = c.site_id
             AND s.date = CAST(timezone('Europe/Helsinki', c.actual_at) AS DATE) + 1
        WHERE c.status IN ('COMPLETED', 'PARTIAL')
        ORDER BY c.collection_id""").df()
    pay = device_trips(con)
    pay = pay.loc[pay.n_payload_lifts >= MIN_PAYLOAD_LIFTS, ["device_id", "full_payload_kg"]]
    f = f.merge(pay, on="device_id", how="left")
    f["load_share"] = f.device_estimated_collected_kg / f.full_payload_kg.where(f.full_payload_kg > 0)
    min_per_week = 7.0 / f.max_days_between_collections
    cur = f.fixed_schedule_per_week.fillna(0.0)
    # at minimum frequency: no slower schedule option still meets the material's maximum interval
    f["at_min_frequency"] = [pol != "ON_CALL" and not any(mf - 1e-9 <= o < fr for o in SCHEDULE_OPTIONS_PER_WEEK)
                             for pol, fr, mf in zip(f.collection_policy, cur, min_per_week)]
    return f.sort_values("collection_id", ignore_index=True)


def flag_lifts(con: duckdb.DuckDBPyConnection, include_requests: bool = INCLUDE_PRE_CLOSURE_REQUESTS) -> pd.DataFrame:
    """lift_features plus `arm` (the matching arm, or None) and `flagged` (arm matched and switched on)."""
    f = lift_features(con)
    no_weight = f.load_share.isna()
    weight_low = (~no_weight & (f.load_share < LOW_LOAD_SHARE)).astype(bool)
    low = (weight_low | (no_weight & (f.device_fill_pct_before < LOW_FILL_PCT))).astype(bool)
    trig = f.original_trigger_type
    arms = [
        ("SCHEDULED_LOW_LOAD", (trig == "SCHEDULED") & low & ~f.at_min_frequency),
        ("ORDER_WEIGHT_LOW", (trig == "ON_CALL_ORDER") & weight_low),
        ("PRE_CLOSURE_REQUEST", (trig == "CUSTOMER_REQUEST") & (f.collection_policy == "ON_CALL") & low
         & f.closed_next_day.astype(bool)),
    ]
    f["arm"] = np.select([m.to_numpy() for _, m in arms], [a for a, _ in arms], default=None)
    f.loc[trig.isin(EXPLAINED_TRIGGERS), "arm"] = None
    f["flagged"] = f.arm.notna() & (include_requests | (f.arm != "PRE_CLOSURE_REQUEST"))
    return f


def predictions(con: duckdb.DuckDBPyConnection, include_requests: bool = INCLUDE_PRE_CLOSURE_REQUESTS) -> pd.DataFrame:
    """Flagged lifts in the kit's Task B submission format (entity_type, entity_id, label_family)."""
    f = flag_lifts(con, include_requests)
    ids = f.loc[f.flagged, "collection_id"]
    return pd.DataFrame({"entity_type": "collection", "entity_id": ids.to_numpy(), "label_family": FAMILY})


def premature_facts(con: duckdb.DuckDBPyConnection) -> dict:
    f = flag_lifts(con)
    n, k = len(f), int(f.flagged.sum())
    examples = tuple(f.loc[f.flagged, "collection_id"].head(5))

    def fig(value, unit, formula):
        return Figure(value, unit, "estimated", formula, SOURCES, row_ids=examples, assumptions=ASSUMPTIONS).to_dict()

    by_policy = []
    for pol, g in f.groupby("collection_policy", sort=True):
        by_policy.append({"collection_policy": pol, "lifts": int(len(g)), "flagged_lifts": int(g.flagged.sum()),
                          "flagged_share_pct": round(100 * float(g.flagged.mean()), 1),
                          "by_arm": {a: int((g.flagged & (g.arm == a)).sum()) for a in ARMS}})
    return {
        "rule": RULE,
        "thresholds": {"low_load_share": LOW_LOAD_SHARE, "low_fill_pct_fallback": LOW_FILL_PCT,
                       "include_pre_closure_requests": INCLUDE_PRE_CLOSURE_REQUESTS},
        "flagged_lifts": fig(k, "count", "count of completed/partial lifts matching one rule arm"),
        "flagged_share_pct": fig(round(100 * k / n, 1) if n else None, "%",
                                 "flagged lifts / completed and partial lifts"),
        "by_policy": by_policy,
    }
