"""H2: the fleet calibrates itself from shared weighbridge tickets. Learning curve on the synthetic lift sequence.

    python self_calibration.py <data/<profile>/public>  -> generated/self_calibration.{md,json}, figures/learning_curve.svg

Every lift is processed in time order across the whole fleet. Before a lift's ticket is used, the device's
corrected weight is scored against the synthetic truth (one-step-ahead, out-of-sample). Then the ticket updates
the estimators. Error is RMS of (corrected / true - 1) grouped by how many tickets that device had seen.

Estimators of a device's log gain theta (corrected = raw / exp(theta)):
  none          theta = 0 (raw H1 sum after test-weight commissioning)
  device only   Kalman filter on the device's own tickets; prior mean 0, prior sd 10 %
  fleet (H2)    the same Kalman filter, but the prior mean is the running mean log ratio of OTHER devices of the
                same material and machine type (devices borrow strength), and the prior sd is the observed
                between-device spread (empirical Bayes; floored at 2 %).
Both filters add random-walk process noise for drift (sd per month as assumed in calc/h1_params.py). The
observation noise sd is learned online from the residuals (pooled; starts at 5 %).
Assumptions: the synthetic ticket mass is the truth; a shared ticket arrives before the next lift (no lag); one
fleet of H1 devices on every reference lift. Devices whose operator shares no tickets stay at their n = 0 point.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "calc"))
from h1_params import P  # noqa: E402

from common import GEN, INK, INK2, S1, S2, S3, check_public_root, save_svg, style  # noqa: E402
from h1_sim import load_lifts, open_public, simulate  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402

SEED = 11
LEVELS = ("low", "mid", "high")
NMAX = 30
PRIOR_SD_DEVICE = 0.10


class Kalman:
    def __init__(self, mean, var):
        self.m, self.v, self.t = mean, var, None

    def predict(self, t, q_per_month):
        if self.t is not None:
            months = max((t - self.t).total_seconds() / (30.4 * 86400), 0)
            self.v += q_per_month ** 2 * months
        self.t = t

    def update(self, y, r_var):
        k = self.v / (self.v + r_var)
        self.m += k * (y - self.m)
        self.v *= (1 - k)


def run(s, lvl):
    q = P["DRIFT_PER_MONTH"][lvl]
    dev_f, fleet_f = {}, {}
    grp_sum, grp_n = defaultdict(float), defaultdict(int)
    dev_sum, dev_n = defaultdict(float), defaultdict(int)
    resid = []
    rows = []
    for r in s.itertuples(index=False):
        d, g = r.device_id, (r.material_stream, r.equipment_class)
        r_var = max(np.var(resid[-2000:]) if len(resid) > 30 else 0.05 ** 2, 0.01 ** 2)
        if d not in dev_f:
            dev_f[d] = Kalman(0.0, PRIOR_SD_DEVICE ** 2)
            # fleet prior: other devices of the same group (their own mean log ratios)
            others = [dev_sum[o] / dev_n[o] for o in dev_n if o != d and dev_n[o] >= 3 and grp_of[o] == g]
            mu = grp_sum[g] / grp_n[g] if grp_n[g] else 0.0
            tau2 = max(np.var(others) - r_var / 5 if len(others) >= 3 else 0.05 ** 2, 0.02 ** 2)
            fleet_f[d] = Kalman(mu, tau2)
        n_seen = dev_n[d]
        for f in (dev_f[d], fleet_f[d]):
            f.predict(r.actual_at, q)
        true_ratio = r.m_hat / r.m_true
        rows.append((n_seen, true_ratio - 1, true_ratio / np.exp(dev_f[d].m) - 1, true_ratio / np.exp(fleet_f[d].m) - 1))
        # the ticket arrives: update everything
        y = np.log(r.m_hat / r.ticket_obs)
        resid.append(y - fleet_f[d].m)
        for f in (dev_f[d], fleet_f[d]):
            f.update(y, r_var)
        grp_sum[g] += y
        grp_n[g] += 1
        dev_sum[d] += y
        dev_n[d] += 1
        grp_of[d] = g
    return np.array(rows)


grp_of: dict = {}


def curve(arr):
    out = []
    for n in range(NMAX + 1):
        sel = arr[:, 0] == n if n < NMAX else arr[:, 0] >= NMAX
        if sel.sum() < 20:
            continue
        out.append({"n_tickets_seen": n if n < NMAX else f">={NMAX}", "lifts": int(sel.sum()),
                    "none_pct": round(100 * float(np.sqrt(np.mean(arr[sel, 1] ** 2))), 2),
                    "device_only_pct": round(100 * float(np.sqrt(np.mean(arr[sel, 2] ** 2))), 2),
                    "fleet_h2_pct": round(100 * float(np.sqrt(np.mean(arr[sel, 3] ** 2))), 2)})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("public")
    a = ap.parse_args(argv)
    con = open_public(check_public_root(a.public))
    lifts = load_lifts(con)
    no_share = int(con.execute("SELECT count(*) FROM devices d JOIN operators o USING (operator_id) "
                               "WHERE NOT o.weighbridge_data_shared").df().iloc[0, 0])
    res = {"n_lifts": int(len(lifts)), "n_devices": int(lifts.device_id.nunique()), "devices_without_ticket_sharing": no_share,
           "levels": {}}
    for i, lvl in enumerate(LEVELS):
        grp_of.clear()
        s = simulate(lifts, lvl, SEED + i)
        arr = run(s, lvl)
        c = curve(arr)
        steady = arr[arr[:, 0] >= 10]
        res["levels"][lvl] = {
            "curve": c,
            "n0": {k: c[0][k] for k in ("none_pct", "device_only_pct", "fleet_h2_pct")},
            "after_10_plus": {"none_pct": round(100 * float(np.sqrt(np.mean(steady[:, 1] ** 2))), 2),
                              "device_only_pct": round(100 * float(np.sqrt(np.mean(steady[:, 2] ** 2))), 2),
                              "fleet_h2_pct": round(100 * float(np.sqrt(np.mean(steady[:, 3] ** 2))), 2)},
            "after_1_to_3": {"none_pct": round(100 * float(np.sqrt(np.mean(arr[(arr[:, 0] >= 1) & (arr[:, 0] <= 3), 1] ** 2))), 2),
                             "device_only_pct": round(100 * float(np.sqrt(np.mean(arr[(arr[:, 0] >= 1) & (arr[:, 0] <= 3), 2] ** 2))), 2),
                             "fleet_h2_pct": round(100 * float(np.sqrt(np.mean(arr[(arr[:, 0] >= 1) & (arr[:, 0] <= 3), 3] ** 2))), 2)},
        }
    (GEN / "self_calibration.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")

    L = res["levels"]
    md = ["| H1 container-total RMS error (low / mid / high) | no calibration | device's own tickets only | fleet self-calibration (H2) |",
          "|---|---|---|---|"]
    for label, key in (("before the device's first ticket (n = 0)", "n0"), ("after 1–3 tickets", "after_1_to_3"),
                       ("after 10 or more tickets", "after_10_plus")):
        cells = []
        for k in ("none_pct", "device_only_pct", "fleet_h2_pct"):
            cells.append(" / ".join(f"{L[l][key][k]:.1f}" for l in LEVELS) + " %")
        md.append(f"| {label} | " + " | ".join(cells) + " |")
    (GEN / "self_calibration.md").write_text("\n".join(md) + "\n")

    style()
    fig, ax = plt.subplots(figsize=(8, 3.8))
    c = L["mid"]["curve"]
    xs = [p["n_tickets_seen"] if isinstance(p["n_tickets_seen"], int) else NMAX for p in c]
    ax.plot(xs, [p["none_pct"] for p in c], color=S2, label="no calibration")
    ax.plot(xs, [p["device_only_pct"] for p in c], color=S3, label="device's own tickets only")
    ax.plot(xs, [p["fleet_h2_pct"] for p in c], color=S1, linewidth=2.6, label="fleet self-calibration (H2)")
    lo = [q["fleet_h2_pct"] for q in L["low"]["curve"]][:len(xs)]
    hi = [q["fleet_h2_pct"] for q in L["high"]["curve"]][:len(xs)]
    n = min(len(lo), len(hi), len(xs))
    ax.fill_between(xs[:n], lo[:n], hi[:n], color=S1, alpha=0.15, linewidth=0, label="H2, low–high parameters")
    ax.set_xlabel(f"weighbridge tickets this device has seen (last point = {NMAX}+)")
    ax.set_ylabel("RMS error of container total, %")
    ax.set_ylim(0, max(p["none_pct"] for p in c) * 1.25)
    ax.set_title("H2: every shared ticket calibrates the fleet (H1 device, synthetic lifts, team-estimate errors)", loc="left")
    ax.legend(fontsize=8, loc="upper right")
    save_svg(fig, "learning_curve.svg")
    print("\n".join(md))
    print(json.dumps({l: L[l]["n0"] for l in LEVELS}))


if __name__ == "__main__":
    main()
