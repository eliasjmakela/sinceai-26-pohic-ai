#!/usr/bin/env bash
# Regenerate every data-derived number and figure of Part 1.
#   part1/scripts/reproduce.sh [<data/<profile>/public>]
# Default data root: $FULLLOAD_DATA, else the competition package in the main checkout's resources/.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PART1="$(dirname "$HERE")"
PY="$PART1/.venv/bin/python"
DATA="${1:-${FULLLOAD_DATA:-/home/eliasjmakela/Documents/sinceai26-haaste/resources/Europress_SMART_Material_Value_Engine_v1.0.1/data/competition/public}}"
cd "$HERE"
"$PY" tiers.py
"$PY" accuracy_value.py "$DATA"
"$PY" drift_watch.py "$DATA"
"$PY" check_interface.py
