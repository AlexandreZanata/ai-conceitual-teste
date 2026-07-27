"""Wave AR6 AR-DUAL-HITL: product pillars + generative gate status."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from aq_product_hitl_ops import (
    APP_SURFACES,
    claim_is_honest,
    generative_claim_unlocked,
)
from ap_session_ops import AP0_PACK

__all__ = [
    "DUAL_HITL_ID",
    "DUAL_HITL_THESIS",
    "HONEST_CLAIM",
    "APP_SURFACES",
    "APP_SMOKE_PACK",
    "claim_is_honest",
    "generative_claim_unlocked",
    "apps_ok",
    "decide_ar_dual_hitl",
]

DUAL_HITL_ID = "AR-DUAL-HITL"
DUAL_HITL_THESIS = (
    "Final dual-arm HITL: AR product pillars + generative gate status; "
    "product pass; gen claim only if AR5 H-NANOGEN2 PROMOTE"
)
HONEST_CLAIM = (
    "AF packaged stack + AQ product layer — not open chat LM"
)


def _one_app(surface: str) -> dict[str, str]:
    for p in AP0_PACK:
        if str(p["app_id"]) == surface:
            return {
                "id": f"AR-APP-{surface}",
                "app_id": surface,
                "source_id": str(p["source_id"]),
                "question": str(p["question"]),
                "gold": str(p["gold"]),
            }
    raise ValueError(f"no AP0 item for surface {surface}")


APP_SMOKE_PACK: tuple[dict[str, str], ...] = tuple(
    _one_app(s) for s in APP_SURFACES
)


def apps_ok(trials: Sequence[Mapping[str, Any]]) -> bool:
    """
    GIVEN known/howto/longdoc LOOKUP trials
    WHEN validating app surfaces
    THEN True iff each surface present with TRUE_HIT.
    """
    by_app = {str(t.get("app_id", "")): t for t in trials}
    if set(APP_SURFACES) - set(by_app):
        return False
    for surface in APP_SURFACES:
        if str(by_app[surface].get("lookup_kind", "")) != "TRUE_HIT":
            return False
    return True


def _core_kill(name: str, dec: str) -> str | None:
    if str(dec).startswith("PROMOTE"):
        return None
    if str(dec).startswith("KILL"):
        return f"KILL ({name}: {dec})"
    return f"KILL ({name} not PROMOTE: {dec})"


def decide_ar_dual_hitl(
    *,
    abstain_decision: str,
    shipdemo_decision: str,
    paraext_decision: str,
    advreg_decision: str,
    apps_pass: bool,
    nanogen2_decision: str,
    claim: str,
) -> str:
    """
    GIVEN AR product pillars + AR5 status + ship claim
    WHEN applying pesquisa §5 AR6 gate
    THEN PROMOTE iff core product PROMOTE + soft deepen PROMOTE + honest claim;
         HOLD on soft deepen defects; KILL on core/claim/gen-lock fail.
    """
    for name, dec in (
        ("abstain", abstain_decision),
        ("shipdemo", shipdemo_decision),
    ):
        err = _core_kill(name, dec)
        if err:
            return err
    if not apps_pass:
        return "KILL (apps smoke missing TRUE_HIT on known/howto/long-doc)"
    if not claim_is_honest(claim):
        return "KILL (dishonest ship claim)"
    nano = str(nanogen2_decision)
    if nano != "PROMOTE" and generative_claim_unlocked(claim):
        return "KILL (generative claim while AR5 HOLD)"
    soft = [
        f"{name}:{dec}"
        for name, dec in (
            ("paraext", paraext_decision),
            ("advreg", advreg_decision),
        )
        if not str(dec).startswith("PROMOTE")
    ]
    if soft:
        return f"HOLD (product soft: {','.join(soft)})"
    return "PROMOTE"
