"""Wave AS8 AS-DUAL-HITL: product pillars + generative gate status."""

from __future__ import annotations

from typing import Any, Mapping

from aq_product_hitl_ops import (
    APP_SURFACES,
    claim_is_honest,
    generative_claim_unlocked,
)
from ap_session_ops import AP0_PACK
from ar_dual_hitl_ops import apps_ok

__all__ = [
    "DUAL_HITL_ID",
    "DUAL_HITL_THESIS",
    "HONEST_CLAIM",
    "APP_SURFACES",
    "APP_SMOKE_PACK",
    "claim_is_honest",
    "generative_claim_unlocked",
    "apps_ok",
    "decide_as_dual_hitl",
]

DUAL_HITL_ID = "AS-DUAL-HITL"
DUAL_HITL_THESIS = (
    "Final dual-arm HITL: AS product pillars + generative gate status; "
    "product pass; gen claim only if AS7 H-NANOGEN3 PROMOTE"
)
HONEST_CLAIM = (
    "AF packaged stack + AQ product layer — not open chat LM"
)


def _one_app(surface: str) -> dict[str, str]:
    for p in AP0_PACK:
        if str(p["app_id"]) == surface:
            return {
                "id": f"AS-APP-{surface}",
                "app_id": surface,
                "source_id": str(p["source_id"]),
                "question": str(p["question"]),
                "gold": str(p["gold"]),
            }
    raise ValueError(f"no AP0 item for surface {surface}")


APP_SMOKE_PACK: tuple[dict[str, str], ...] = tuple(
    _one_app(s) for s in APP_SURFACES
)


def _core_kill(name: str, dec: str) -> str | None:
    if str(dec).startswith("PROMOTE"):
        return None
    if str(dec).startswith("KILL"):
        return f"KILL ({name}: {dec})"
    return f"KILL ({name} not PROMOTE: {dec})"


def decide_as_dual_hitl(
    *,
    askabstain_decision: str,
    shipui_decision: str,
    advsafe_decision: str,
    metrics_decision: str,
    paraext2_decision: str,
    apps_pass: bool,
    nanogen3_decision: str,
    claim: str,
) -> str:
    """
    GIVEN AS product pillars + AS7 status + ship claim
    WHEN applying pesquisa §5 AS8 gate
    THEN PROMOTE iff core product PROMOTE + soft deepen PROMOTE + honest claim;
         HOLD on soft deepen defects; KILL on core/claim/gen-lock fail.
    """
    for name, dec in (
        ("askabstain", askabstain_decision),
        ("shipui", shipui_decision),
        ("advsafe", advsafe_decision),
        ("metrics", metrics_decision),
    ):
        err = _core_kill(name, dec)
        if err:
            return err
    if not apps_pass:
        return "KILL (apps smoke missing TRUE_HIT on known/howto/long-doc)"
    if not claim_is_honest(claim):
        return "KILL (dishonest ship claim)"
    nano = str(nanogen3_decision)
    if nano != "PROMOTE" and generative_claim_unlocked(claim):
        return "KILL (generative claim while AS7 HOLD)"
    soft = [
        f"{name}:{dec}"
        for name, dec in (("paraext2", paraext2_decision),)
        if not str(dec).startswith("PROMOTE")
    ]
    if soft:
        return f"HOLD (product soft: {','.join(soft)})"
    return "PROMOTE"
