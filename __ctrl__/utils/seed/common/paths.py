"""Path helpers for seed data (kit-agnostic: names derive from the checkout folder)."""

from __future__ import annotations

from pathlib import Path

# common/paths.py -> parents[3] = __ctrl__, parents[4] = kit root
CTRL_ROOT = Path(__file__).resolve().parents[3]
KIT_ROOT = CTRL_ROOT.parent
KIT_NAME = KIT_ROOT.name
CTRL_NAME = f"{KIT_NAME}-ctrl"
SEED_ROOT = CTRL_ROOT / "utils" / "seed"
STATE_ROOT = SEED_ROOT / ".state"
