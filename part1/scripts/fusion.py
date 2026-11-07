"""H3: what the compactor's existing signals add to H1 (fill, press load, compaction-cycle count).

    python fusion.py <data/<profile>/public>   -> generated/fusion.{md,json}

1. T0 alone in the synthetic world: weight = k_device x fill_before x volume, k learned online from the device's
   previous tickets (median of the last 10 ratios), scored one step ahead. A second variant adds the press load
   index through a per-material linear correction fitted on the first half of the year, scored on the second.
2. Fusion: inverse-variance mix of the H2-calibrated H1 weight (simulated, mid parameters) and T0, on the same lifts.
3. Plate-jam detection: a jammed or bridged plate reads ~0 kg while the ram keeps cycling. Rule: 10 consecutive
   strokes with no weight change -> fault. The compaction-cycle counter says how fast that rule fires.
The synthetic fill and press index are simulated by the starter kit; real pressure curves were not available
(TOMMI Q8), so the T0 number is a property of the synthetic data, not of the real signal.
"""
from __future__ import annotations

import argparse
import json

import numpy as np

from common import GEN, check_public_root
from h1_sim import load_lifts, open_public, simulate
import self_calibration as sc

MIN_HIST = 5


def rms(x):
    x = np.asarray(x)
    return float(np.sqrt(np.mean(x ** 2)))


def robust_sigma(x):
    x = np.asarray(x)
    return float(1.4826 * np.median(np.abs(x - np.median(x))))


def t0_online(df):
    hist, pred = {}, np.full(len(df), np.nan)
    for i, r in enumerate(df.itertuples(index=False)):
        base = (r.fill_before or 0) / 100 * r.volume_m3
        h = hist.setdefault(r.device_id, [])
        if base > 0 and len(h) >= MIN_HIST:
            pred[i] = np.median(h[-10:]) * base
        if base > 0:
            h.append(r.ticket_kg / base)
    return pred


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("public")
    a = ap.parse_args(argv)
    con = open_public(check_public_root(a.public))
    df = load_lifts(con)
    df = df[df.fill_before.notna()].reset_index(drop=True)
    df["t0"] = t0_online(df)
    ok = df.t0.notna()
    e_t0 = (df.t0[ok] / df.ticket_kg[ok] - 1).to_numpy()
    res = {"t0_fill_only": {"lifts": int(ok.sum()), "rms_pct": round(100 * rms(e_t0), 1),
                            "median_abs_pct": round(100 * float(np.median(np.abs(e_t0))), 1),
                            "p90_abs_pct": round(100 * float(np.quantile(np.abs(e_t0), 0.9)), 1),
                            "robust_sigma_pct": round(100 * robust_sigma(e_t0), 1)}}
    per_mat = {}
    for mat, g in df[ok].groupby("material_stream"):
        e = g.t0 / g.ticket_kg - 1
        per_mat[mat] = round(100 * float(np.median(np.abs(e))), 1)
    res["t0_fill_only"]["median_abs_pct_by_material"] = per_mat

    # variant: + press load index (per-material linear correction of log residual, fit on H1 of the year)
    d2 = df[ok & df.press_index.notna()].copy()
    d2["lr"] = np.log(d2.ticket_kg / d2.t0)
    cut = d2.actual_at.quantile(0.5)
    e2 = []
    for mat, g in d2.groupby("material_stream"):
        tr, te = g[g.actual_at <= cut], g[g.actual_at > cut]
        if len(tr) < 30 or len(te) < 10:
            continue
        b = np.polyfit(tr.press_index, tr.lr, 1)
        e2 += list(np.exp(np.log(te.t0) + np.polyval(b, te.press_index)) / te.ticket_kg - 1)
    e1 = (d2[d2.actual_at > cut].t0 / d2[d2.actual_at > cut].ticket_kg - 1).to_numpy()
    res["t0_plus_press_index"] = {"lifts": len(e2), "rms_pct": round(100 * rms(e2), 1),
                                  "median_abs_pct": round(100 * float(np.median(np.abs(e2))), 1),
                                  "same_lifts_fill_only_rms_pct": round(100 * rms(e1), 1),
                                  "same_lifts_fill_only_median_abs_pct": round(100 * float(np.median(np.abs(e1))), 1)}

    # fusion with H1 + H2 (mid)
    sc.grp_of.clear()
    s = simulate(df, "mid", sc.SEED + 1)
    arr = sc.run(s, "mid")
    e_h1 = arr[:, 3]
    seen = arr[:, 0] >= 3
    both = ok.to_numpy() & seen
    eh, e0 = e_h1[both], (df.t0 / df.ticket_kg - 1).to_numpy()[both]
    s1, s0 = robust_sigma(eh), robust_sigma(e0)
    w = s0 ** 2 / (s0 ** 2 + s1 ** 2)
    # gate: use T0 only when it agrees with H1 within 3 combined sigma (T0 has heavy outliers: fill faults, residue)
    agree = np.abs(e0 - eh) < 3 * np.hypot(s0, s1)
    fused = np.where(agree, w * eh + (1 - w) * e0, eh)
    res["fusion_h1_h2_mid"] = {"lifts": int(both.sum()), "h1_rms_pct": round(100 * rms(eh), 2),
                               "t0_robust_sigma_pct": round(100 * s0, 2), "h1_robust_sigma_pct": round(100 * s1, 2),
                               "weight_on_h1": round(w, 3), "share_t0_used": round(float(agree.mean()), 3),
                               "fused_rms_pct": round(100 * rms(fused), 2)}

    # jam detection speed from the cycle counter
    cpd = con.execute("""SELECT d.material_stream, avg(s.compaction_cycles)::DOUBLE AS cycles_per_day
                         FROM telemetry_daily_summary s JOIN devices d USING (device_id)
                         GROUP BY ALL ORDER BY 1""").df()
    res["jam_detection"] = {r.material_stream: {"cycles_per_day": round(r.cycles_per_day, 1),
                                                "hours_to_10_strokes": round(24 * 10 / r.cycles_per_day, 1)}
                            for r in cpd.itertuples()}
    (GEN / "fusion.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")

    f, p2, fu = res["t0_fill_only"], res["t0_plus_press_index"], res["fusion_h1_h2_mid"]
    jd = res["jam_detection"]
    md = ["| Signal | What it gives (synthetic data) |", "|---|---|",
          f"| T0: fill × volume × learned density (fill only) | median abs error {f['median_abs_pct']} %, robust σ {f['robust_sigma_pct']} %, p90 {f['p90_abs_pct']} %, but RMS {f['rms_pct']} % (heavy outliers) over {f['lifts']} lifts |",
          f"| T0 + press load index | median abs error {p2['median_abs_pct']} % vs {p2['same_lifts_fill_only_median_abs_pct']} % fill-only on the same {p2['lifts']} lifts (second half of the year) |",
          f"| H1 + H2 fused with T0 (inverse variance) | RMS {fu['h1_rms_pct']} % → {fu['fused_rms_pct']} % (weight on H1 {fu['weight_on_h1']}, T0 used on {fu['share_t0_used']:.0%} of lifts after an agreement gate) |",
          "| Compaction-cycle counter → plate-jam alarm (10 strokes with no weight change) | "
          + ", ".join(f"{m.replace('_', ' ')} {v['hours_to_10_strokes']} h" for m, v in jd.items()) + " |"]
    (GEN / "fusion.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))
    print(json.dumps(per_mat))


if __name__ == "__main__":
    main()
