"""Wave AS1 H-ASKABSTAIN: ABSTAIN on default nano:z:ask / apps ask path."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from abstain_ops import (
    ABSTAIN_KNOWN_ASK,
    ABSTAIN_OOD_PACK,
    MIN_OOD_ABSTAIN_RATE,
    NO_ANSWER,
    abstain_stats,
    is_false_hit_completion,
    mode_labeled,
)
from as_session_ops import AS0_ASKABSTAIN_CHARTER, AS0_ANTI_FP, AS0_SAFE_NOTE

__all__ = [
    "ASKABSTAIN_ID",
    "ASKABSTAIN_THESIS",
    "ASKABSTAIN_OOD_PACK",
    "ASKABSTAIN_KNOWN_ASK",
    "MIN_OOD_ABSTAIN_RATE",
    "NO_ANSWER",
    "default_path_abstained",
    "askabstain_stats",
    "decide_askabstain",
    "ASKABSTAIN_CHARTER",
    "ASKABSTAIN_SAFE_NOTE",
    "ASKABSTAIN_ANTI_FP",
]

ASKABSTAIN_ID = "H-ASKABSTAIN"
ASKABSTAIN_THESIS = (
    "Wire ABSTAIN into default nano:z:ask / apps ask path; "
    "OOD→NO_ANSWER without runner-only gate; known LOOKUP preserved; FH 0"
)
ASKABSTAIN_OOD_PACK = ABSTAIN_OOD_PACK
ASKABSTAIN_KNOWN_ASK = ABSTAIN_KNOWN_ASK
ASKABSTAIN_CHARTER = AS0_ASKABSTAIN_CHARTER
ASKABSTAIN_SAFE_NOTE = AS0_SAFE_NOTE
ASKABSTAIN_ANTI_FP = AS0_ANTI_FP


def default_path_abstained(payload: Mapping[str, Any]) -> bool:
    """
    GIVEN a payload from default ask_once/ask_many (no extra apply_abstain)
    WHEN checking product honesty
    THEN True iff already NO_ANSWER / ABSTAIN on the default path.
    """
    return (
        bool(payload.get("abstained"))
        and str(payload.get("completion", "")) == NO_ANSWER
        and str(payload.get("product_mode", "")) == "ABSTAIN"
        and str(payload.get("mode", "")) == "NO_ANSWER"
    )


def askabstain_stats(
    *,
    ood_default_abstained: Sequence[bool],
    known_lookup_ok: bool,
    n_false_hit: int,
    modes_labeled: bool,
    default_path_wired: bool,
) -> dict[str, Any]:
    """
    GIVEN OOD default-path abstain flags + known LOOKUP + FH + wire flag
    WHEN summarizing AS1
    THEN rates + pass flags for decide.
    """
    base = abstain_stats(
        ood_abstained=ood_default_abstained,
        known_lookup_ok=known_lookup_ok,
        n_false_hit=n_false_hit,
        modes_labeled=modes_labeled,
    )
    base["default_path_wired"] = bool(default_path_wired)
    base["pass_default_path"] = bool(default_path_wired)
    base["charter_paths"] = list(ASKABSTAIN_CHARTER.get("paths", []))
    return base


def decide_askabstain(stats: Mapping[str, Any]) -> str:
    """
    GIVEN H-ASKABSTAIN stats
    WHEN applying pesquisa §5 AS1 gate
    THEN PROMOTE iff default path wired · OOD abstain↑ · FH 0 ·
         known LOOKUP ok · modes labeled.
    """
    if not bool(stats.get("pass_default_path")):
        return "KILL (abstain not wired into default ask path)"
    if not bool(stats.get("pass_ood_abstain")):
        return (
            f"KILL (ood abstain_rate {stats.get('ood_abstain_rate')} "
            f"< {MIN_OOD_ABSTAIN_RATE})"
        )
    if not bool(stats.get("pass_false_hit")):
        return f"KILL (false-hit {stats.get('n_false_hit')} > 0)"
    if not bool(stats.get("known_lookup_ok")):
        return "KILL (known-ask LOOKUP control failed)"
    if not bool(stats.get("modes_labeled")):
        return "KILL (unlabeled product_mode)"
    paths = stats.get("charter_paths") or []
    if "nano:z:ask" not in paths:
        return "KILL (charter missing nano:z:ask)"
    return "PROMOTE"


# Re-export FH helper for runner without pulling abstain_ops in tests only.
def askabstain_false_hit(
    *,
    completion: str,
    product_mode: str,
    bank_golds: Sequence[str],
) -> bool:
    """Delegate false-hit check (LOOKUP or exact bank gold on OOD)."""
    return is_false_hit_completion(
        completion=completion,
        product_mode=product_mode,
        bank_golds=bank_golds,
    )


def askabstain_mode_labeled(payload: Mapping[str, Any]) -> bool:
    """Delegate mode-labeled check (AR0 four modes)."""
    return mode_labeled(payload)
