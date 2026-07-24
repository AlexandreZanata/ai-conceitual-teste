"""Matrix hypothesis wave — champions only (CURL / EARLY / POOL parents)."""

from __future__ import annotations

from typing import Any

import torch


def run_hypotheses(c: dict[str, Any], device: torch.device, rows: list) -> None:
    """
    Dead hyp runners purged. Champion tips have dedicated npm smoke scripts.
    Matrix keeps B0–B4 (+ decode ops); tips are not re-run here.
    """
    _ = (c, device, rows)
