"""Wave AR1 H-ABSTAIN: refuse junk DECODE → NO_ANSWER / ABSTAIN."""

from __future__ import annotations

import re
from typing import Any, Mapping, MutableMapping, Sequence

from ar_session_ops import AR0_ADVREG_PACK, AR0_MODES, map_ar_product_mode
from asksmart_ops import is_period_collapse

__all__ = [
    "ABSTAIN_ID",
    "ABSTAIN_THESIS",
    "NO_ANSWER",
    "MIN_OOD_ABSTAIN_RATE",
    "ABSTAIN_OOD_PACK",
    "ABSTAIN_KNOWN_ASK",
    "is_junk_decode",
    "should_abstain",
    "apply_abstain",
    "mode_labeled",
    "is_false_hit_completion",
    "abstain_stats",
    "decide_abstain",
]

ABSTAIN_ID = "H-ABSTAIN"
NO_ANSWER = "NO_ANSWER"
MIN_OOD_ABSTAIN_RATE = 0.8
ABSTAIN_THESIS = (
    "Refuse junk DECODE on OOD/miss → NO_ANSWER / ABSTAIN; "
    "OOD abstain↑; false-hit still 0; modes labeled LOOKUP|PEAK|DECODE|ABSTAIN"
)

ABSTAIN_KNOWN_ASK = (
    "Write a short Python function named add that returns "
    "the sum of two integers a and b."
)

# OOD + period/empty traps from AR0 advreg (expect ABSTAIN after junk gate).
ABSTAIN_OOD_PACK: tuple[dict[str, str], ...] = tuple(
    dict(p)
    for p in AR0_ADVREG_PACK
    if str(p.get("kind")) == "ood"
    or str(p.get("id")) in {"AR-ADVREG-18", "AR-ADVREG-19"}
)

_WORD = re.compile(r"[A-Za-z0-9_]{3,}")
_FILLER = frozenset(
    {
        "really",
        "everything",
        "something",
        "looking",
        "followed",
        "getting",
        "finally",
        "quickly",
        "now",
        "just",
        "which",
        "that",
        "back",
        "even",
    }
)
# Real code markers — not bare "let " (TinyStories "let and" false-exempt).
_CODEISH = re.compile(
    r"(?:^|\W)(?:def |class |struct |fn |return |BIP)"
    r"|\blet\s+[A-Za-z_][A-Za-z0-9_]*\s*="
)


def is_junk_decode(text: str) -> bool:
    """
    GIVEN a DECODE completion
    WHEN checking TinyStories garbage / empty / period-collapse
    THEN True iff product should refuse (NO_ANSWER).
    """
    t = str(text or "")
    if is_period_collapse(t):
        return True
    stripped = t.strip()
    if not stripped:
        return True
    if "\ufffd" in t or "�" in t:
        return True
    words = _WORD.findall(stripped)
    if len(words) < 2:
        return True
    low = {w.lower() for w in words}
    if len(low & _FILLER) >= 3 and _CODEISH.search(stripped) is None:
        return True
    return False


def should_abstain(*, raw_mode: str, completion: str) -> bool:
    """
    GIVEN raw mode + completion
    WHEN applying AR0 abstention protocol
    THEN True iff DECODE/UNKNOWN junk (LOOKUP/PEAK never abstained here).
    """
    product = map_ar_product_mode(raw_mode)
    if product in {"LOOKUP", "PEAK"}:
        return False
    if product == "ABSTAIN":
        return True
    return is_junk_decode(completion)


def apply_abstain(payload: MutableMapping[str, Any]) -> dict[str, Any]:
    """
    GIVEN ASK payload
    WHEN junk DECODE detected
    THEN set completion=NO_ANSWER, mode=NO_ANSWER, product_mode=ABSTAIN.
    """
    out = dict(payload)
    raw = str(out.get("mode", "") or "")
    comp = str(out.get("completion", "") or "")
    if should_abstain(raw_mode=raw, completion=comp):
        out["pre_abstain_completion"] = comp
        out["pre_abstain_mode"] = raw
        out["completion"] = NO_ANSWER
        out["mode"] = "NO_ANSWER"
        out["product_mode"] = "ABSTAIN"
        out["abstained"] = True
        return out
    out["product_mode"] = map_ar_product_mode(raw)
    out["abstained"] = False
    return out


def mode_labeled(payload: Mapping[str, Any]) -> bool:
    """True iff product_mode is exactly one of AR0 modes."""
    return str(payload.get("product_mode", "") or "") in AR0_MODES


def is_false_hit_completion(
    *,
    completion: str,
    product_mode: str,
    bank_golds: Sequence[str],
) -> bool:
    """
    GIVEN post-abstain completion on OOD/miss
    WHEN checking silent wrong gold
    THEN True iff LOOKUP or exact bank gold returned (≠ NO_ANSWER).
    """
    if product_mode == "LOOKUP":
        return True
    text = str(completion or "").strip()
    if not text or text == NO_ANSWER:
        return False
    golds = {g.strip() for g in bank_golds if str(g).strip()}
    return text in golds


def abstain_stats(
    *,
    ood_abstained: Sequence[bool],
    known_lookup_ok: bool,
    n_false_hit: int,
    modes_labeled: bool,
) -> dict[str, Any]:
    """
    GIVEN OOD abstain flags + known LOOKUP control + FH
    WHEN summarizing AR1
    THEN rates + pass flags for decide.
    """
    n = len(ood_abstained)
    n_abs = int(sum(1 for x in ood_abstained if x))
    rate = (float(n_abs) / float(n)) if n else 0.0
    return {
        "ood_n": n,
        "ood_abstained_n": n_abs,
        "ood_abstain_rate": round(rate, 4),
        "min_ood_abstain_rate": MIN_OOD_ABSTAIN_RATE,
        "pass_ood_abstain": rate >= MIN_OOD_ABSTAIN_RATE,
        "known_lookup_ok": bool(known_lookup_ok),
        "n_false_hit": int(n_false_hit),
        "pass_false_hit": int(n_false_hit) == 0,
        "modes_labeled": bool(modes_labeled),
    }


def decide_abstain(stats: Mapping[str, Any]) -> str:
    """
    GIVEN H-ABSTAIN stats
    WHEN applying pesquisa §5 AR1 gate
    THEN PROMOTE iff OOD abstain↑ · FH 0 · known LOOKUP ok · modes labeled.
    """
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
    return "PROMOTE"
