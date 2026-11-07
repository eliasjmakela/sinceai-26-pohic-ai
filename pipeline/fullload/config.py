"""The single place where paths are decided.

Environment variables (both optional):
  FULLLOAD_KIT   starter kit root (default: resources/Europress_SMART_Material_Value_Engine_v1.0.1)
  FULLLOAD_DATA  data package: "competition" (default), "quickstart", or a path to a `public/` folder
Worktrees and agents set these to absolute paths in the main checkout.
"""
from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PIPELINE_ROOT = REPO_ROOT / "pipeline"
PARAMS_PATH = Path(__file__).resolve().parent / "params.yaml"
BUNDLE_PATH = REPO_ROOT / "pipeline" / "out" / "bundle.json"

_DEFAULT_KIT = REPO_ROOT / "resources" / "Europress_SMART_Material_Value_Engine_v1.0.1"
PROFILES = ("competition", "quickstart")

# Material streams left out of the business claims (decision 7 Nov): biowaste gives little back-pressure and is the
# hardest stream to weigh, so the service starts without it. Observed fleet facts (beat 0) keep every stream.
EXCLUDED_MATERIALS = ("biowaste",)


def kit_root() -> Path:
    root = Path(os.environ.get("FULLLOAD_KIT", _DEFAULT_KIT))
    if not (root / "src" / "europress_data").is_dir():
        raise FileNotFoundError(f"Starter kit not found at {root}. Set FULLLOAD_KIT or see README setup.")
    return root


def data_root(data: str | None = None) -> Path:
    """Resolve a profile name or path to a data package `public/` folder."""
    data = data or os.environ.get("FULLLOAD_DATA", "competition")
    root = kit_root() / "data" / data / "public" if data in PROFILES else Path(data)
    if not (root / "reference").is_dir():
        raise FileNotFoundError(f"Data package not found at {root}.")
    return root


def profile_name(root: Path) -> str:
    """'competition' / 'quickstart' if the root is a kit profile, else the folder path (recorded in the bundle)."""
    return root.parent.name if root.name == "public" and root.parent.name in PROFILES else str(root)
