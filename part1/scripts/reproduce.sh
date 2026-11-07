#!/usr/bin/env bash
# Regenerate every calculation, data-derived number and figure of Part 1 (v1 + weighing v2 + H7).
#   part1/scripts/reproduce.sh [<data/<profile>/public>]
# Default data root: $FULLLOAD_DATA, else the competition package in the main checkout's resources/.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PART1="$(dirname "$HERE")"
PY="$PART1/.venv/bin/python"
DATA="${1:-${FULLLOAD_DATA:-/home/eliasjmakela/Documents/sinceai26-haaste/resources/Europress_SMART_Material_Value_Engine_v1.0.1/data/competition/public}}"
# 1. first-principles calculations (no data)
cd "$PART1/calc"
"$PY" loads.py > /dev/null
"$PY" temperature.py > /dev/null
"$PY" error_accumulation.py > /dev/null
"$PY" h7_hydraulic.py > /dev/null
"$PY" installed_cost.py > /dev/null
# 2. data-backed analyses (synthetic data, fixed seeds)
cd "$HERE"
"$PY" charge_sum.py "$DATA"
"$PY" self_calibration.py "$DATA"
"$PY" fusion.py "$DATA"
# 3. tiers (reads installed_cost.json + self_calibration.json), v1 analyses, figures, interface check
"$PY" tiers.py
"$PY" accuracy_value.py "$DATA"
"$PY" drift_watch.py "$DATA"
"$PY" cost_figure.py
"$PY" check_interface.py
