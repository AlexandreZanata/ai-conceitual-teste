"""Wave AQ7 AQ-PRODUCT-HITL: final product verify (no gen uplift if AQ6 HOLD)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ap_session_ops import AP0_PACK

__all__ = [
    "PRODUCT_HITL_ID",
    "PRODUCT_HITL_THESIS",
    "HONEST_CLAIM",
    "APP_SURFACES",
    "APP_SMOKE_PACK",
    "claim_is_honest",
    "generative_claim_unlocked",
    "apps_ok",
    "decide_aq_product_hitl",
]

PRODUCT_HITL_ID = "AQ-PRODUCT-HITL"
PRODUCT_HITL_THESIS = (
    "Final product verify: paraphrase + adversary + apps + modes; "
    "product metrics pass; generative claim only if AQ6 PROMOTE"
)
HONEST_CLAIM = (
    "AF packaged stack + AQ product layer — not open chat LM"
)
APP_SURFACES: tuple[str, ...] = ("known-ask", "howto", "long-doc")


def _one_app(surface: str) -> dict[str, str]:
    for p in AP0_PACK:
        if str(p["app_id"]) == surface:
            return {
                "id": f"AQ-APP-{surface}",
                "app_id": surface,
                "source_id": str(p["source_id"]),
                "question": str(p["question"]),
                "gold": str(p["gold"]),
            }
    raise ValueError(f"no AP0 item for surface {surface}")


APP_SMOKE_PACK: tuple[dict[str, str], ...] = tuple(
    _one_app(s) for s in APP_SURFACES
)


def claim_is_honest(claim: str) -> bool:
    """
    GIVEN a ship claim string
    WHEN checking AQ7 honesty
    THEN reject open-chat / mini-AGI / generative uplift wording.
    """
    low = str(claim).lower()
    if "not open chat" in low or "not open-chat" in low:
        return "packaged" in low or "product layer" in low or "af " in low
    banned = (
        "open chat",
        "open-chat",
        "mini-agi",
        "mini agi",
        "gpt-class",
        "generative ship",
        "unlocked generative",
    )
    if any(b in low for b in banned):
        return False
    return "packaged" in low or "product layer" in low


def generative_claim_unlocked(claim: str) -> bool:
    """True if claim language asserts generative / open-chat competence."""
    low = str(claim).lower()
    if "not open chat" in low or "not open-chat" in low:
        return False
    markers = (
        "open chat",
        "open-chat",
        "mini-agi",
        "generative unlocked",
        "ablated promote",
        "true-gen unlocked",
    )
    return any(m in low for m in markers)


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


def decide_aq_product_hitl(
    *,
    para_decision: str,
    adv_decision: str,
    mode_decision: str,
    apps_pass: bool,
    nanogen_decision: str,
    claim: str,
) -> str:
    """
    GIVEN pillar decisions + AQ6 status + ship claim
    WHEN applying pesquisa §5 AQ7 gate
    THEN PROMOTE iff product pillars pass and claim honest under AQ6 lock.
    """
    for name, dec in (
        ("parahit", para_decision),
        ("advfp", adv_decision),
        ("modeui", mode_decision),
    ):
        if str(dec).startswith("KILL"):
            return f"KILL ({name}: {dec})"
    if not apps_pass:
        return "KILL (apps smoke missing TRUE_HIT on known/howto/long-doc)"
    if not claim_is_honest(claim):
        return "KILL (dishonest ship claim)"
    nano = str(nanogen_decision)
    if nano != "PROMOTE" and generative_claim_unlocked(claim):
        return "KILL (generative claim while AQ6 HOLD)"
    soft = [
        name
        for name, dec in (
            ("parahit", para_decision),
            ("advfp", adv_decision),
            ("modeui", mode_decision),
        )
        if not str(dec).startswith("PROMOTE")
    ]
    if soft:
        return f"HOLD (product soft: {','.join(soft)})"
    return "PROMOTE"
