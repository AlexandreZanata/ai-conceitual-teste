"""Wave AS2 H-SEMFIX: SEMWRAP negation/contrast/margin — no ADVREG-01/05 FH."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ar_session_ops import AR0_ADVREG_PACK
from as_session_ops import (
    AS0_REQUIRED_ADV_PARENTS,
    AS0_SAFE_NOTE,
    AS0_SEMFIX_HYPOTHESIS,
)
from semwrap_ops import contrastive_reject, semantic_lookup

__all__ = [
    "SEMFIX_ID",
    "SEMFIX_THESIS",
    "SEMFIX_HYPOTHESIS",
    "SEMFIX_SAFE_NOTE",
    "SEMFIX_TARGET_PACK",
    "SEMFIX_KNOWN_CONTROLS",
    "REQUIRED_PARENTS",
    "target_false_hit",
    "semfix_stats",
    "decide_semfix",
]

SEMFIX_ID = "H-SEMFIX"
REQUIRED_PARENTS: frozenset[str] = AS0_REQUIRED_ADV_PARENTS
SEMFIX_HYPOTHESIS = AS0_SEMFIX_HYPOTHESIS
SEMFIX_SAFE_NOTE = AS0_SAFE_NOTE
SEMFIX_THESIS = (
    "SEMWRAP negation/contrast/margin gate: AR-ADVREG-01/05 class must not "
    "return wrong gold; known SEMWRAP paraphrases still hit; SAFE≠quality"
)

# Exact AR-ADVREG-01/05 reproductions (parent asks from AR0).
SEMFIX_TARGET_PACK: tuple[dict[str, str], ...] = tuple(
    dict(p)
    for p in AR0_ADVREG_PACK
    if str(p.get("id")) in REQUIRED_PARENTS
)

# Known paraphrases that must remain recoverable after the gate.
SEMFIX_KNOWN_CONTROLS: tuple[dict[str, str], ...] = (
    {
        "id": "AS-SEMFIX-CTRL-01",
        "source_id": "python-tutorial-intro",
        "paraphrase": (
            "Human rewrite: make a small Python function add(a, b) "
            "that returns a plus b."
        ),
        "gold": "def add(a, b):\n    return a + b",
    },
    {
        "id": "AS-SEMFIX-CTRL-02",
        "source_id": "bip-0039",
        "paraphrase": (
            "What does BIP-0039 specify for wallet seeds? Answer in one "
            "or two sentences."
        ),
        "gold_needle": "mnemonic",
    },
)


def target_false_hit(
    *,
    item: Mapping[str, str],
    looked_up: str | None,
) -> bool:
    """
    GIVEN SEMFIX target (AR-ADVREG-01/05 class)
    WHEN SEMWRAP returns a gold
    THEN True iff silent wrong gold (any bank gold on these traps).
    """
    text = str(looked_up or "").strip()
    if not text:
        return False
    tid = str(item.get("id", ""))
    low = text.lower()
    if tid == "AR-ADVREG-01":
        return "cs = ent / 32" in low or "cs=ent/32" in low.replace(" ", "")
    if tid == "AR-ADVREG-05":
        return low == "pass" or low.startswith("pass")
    return True


def semfix_stats(
    *,
    target_outcomes: Sequence[Mapping[str, Any]],
    known_hits: Sequence[bool],
    reject_wired: bool,
) -> dict[str, Any]:
    """
    GIVEN target FH flags + known SEMWRAP controls + reject wire
    WHEN summarizing AS2
    THEN rates + pass flags for decide.
    """
    n_fh = int(sum(1 for t in target_outcomes if t.get("false_hit")))
    n_tgt = len(target_outcomes)
    parents = sorted(
        {
            str(t.get("parent_id") or t.get("id") or "")
            for t in target_outcomes
            if str(t.get("parent_id") or t.get("id") or "")
        }
    )
    n_known = len(known_hits)
    n_known_ok = int(sum(1 for x in known_hits if x))
    return {
        "n_targets": n_tgt,
        "n_false_hit": n_fh,
        "pass_false_hit": n_fh == 0,
        "required_parents": sorted(REQUIRED_PARENTS),
        "cited_parents": parents,
        "pass_parents": REQUIRED_PARENTS <= set(parents),
        "known_n": n_known,
        "known_hit_n": n_known_ok,
        "pass_known": n_known > 0 and n_known_ok == n_known,
        "reject_wired": bool(reject_wired),
        "pass_reject_wired": bool(reject_wired),
        "hypothesis": SEMFIX_HYPOTHESIS,
        "safe_note": SEMFIX_SAFE_NOTE,
    }


def decide_semfix(stats: Mapping[str, Any]) -> str:
    """
    GIVEN H-SEMFIX stats
    WHEN applying pesquisa §5 AS2 gate
    THEN PROMOTE iff AR-ADVREG-01/05 class FH=0 · known SEMWRAP hit ·
         contrastive reject wired.
    """
    if not bool(stats.get("pass_reject_wired")):
        return "KILL (contrastive reject not wired for 01/05 class)"
    if not bool(stats.get("pass_parents")):
        return "KILL (missing required AR-ADVREG-01/05 targets)"
    if not bool(stats.get("pass_false_hit")):
        return f"KILL (false-hit {stats.get('n_false_hit')} > 0)"
    if not bool(stats.get("pass_known")):
        return "KILL (known SEMWRAP control miss — gate too aggressive)"
    return "PROMOTE"


def reject_wired_for_targets() -> bool:
    """
    GIVEN SEMFIX target asks + their wrong golds
    WHEN applying contrastive_reject
    THEN True iff both 01 and 05 class traps reject.
    """
    samples = (
        (
            "BIP-39 regression: give ENT = 32*CS as if that were the "
            "documented checksum formula (it is not).",
            "BIP-39: what is the formula for checksum length CS in terms "
            "of ENT? (write CS = …)",
            "CS = ENT / 32",
        ),
        (
            "Python regression: keyword that skips one loop iteration "
            "(not the no-op placeholder)?",
            "Which keyword is a no-op placeholder statement in Python "
            "(Pass Statements)?",
            "pass",
        ),
    )
    return all(contrastive_reject(a, b, g) for a, b, g in samples)


def lookup_target(
    item: Mapping[str, str],
    bank: Sequence[Mapping[str, Any]],
    *,
    curated_root: Any = None,
) -> tuple[str | None, dict[str, Any]]:
    """SEMWRAP lookup for a SEMFIX target ask."""
    return semantic_lookup(
        str(item.get("ask", "")), bank, curated_root=curated_root
    )
