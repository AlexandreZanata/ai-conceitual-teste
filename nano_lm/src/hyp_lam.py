"""H-LAM: Lamarckian write-back (inherit learned phenotype)."""

from __future__ import annotations

from typing import Any

from hyp_bal import run_plastic_evo


def run_h_lam(**kwargs: Any) -> dict[str, Any]:
    """Same plastic loop as H-BAL, but inherit phenotype after lifetime GD."""
    return run_plastic_evo(
        inherit_mode="lamarck", hypothesis="H-LAM", **kwargs
    )
