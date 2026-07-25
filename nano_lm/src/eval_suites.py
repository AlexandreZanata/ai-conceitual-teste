"""Phase E5 fixed eval YAML suites (prompts committed; corpora regenerable)."""

from __future__ import annotations

from pathlib import Path

from matrix_common import ROOT

# Heldout / frontier suites — do NOT replace H-PROG / H-BTC formal packs.
E5_PROG_HELDOUT = ROOT / "prompts/e5_prog_heldout.yaml"
E5_BTC_HELDOUT = ROOT / "prompts/e5_btc_heldout.yaml"
FRONTIER_PROMPTS = ROOT / "prompts/frontier_prompts.yaml"

EVAL_SUITE_PATHS: tuple[Path, ...] = (
    E5_PROG_HELDOUT,
    E5_BTC_HELDOUT,
    FRONTIER_PROMPTS,
)

# Official H-PROG / H-BTC packs remain the Wave W claim surfaces.
CLAIM_PACK_PATHS: tuple[Path, ...] = (
    ROOT / "prompts/prog_prompts.yaml",
    ROOT / "prompts/btc_prompts.yaml",
)
