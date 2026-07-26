"""Wave AI0 SESSION: freeze 10 held-out HITL asks (≠ AB…AH)."""

from __future__ import annotations

from typing import Mapping, Sequence

from ab_session_ops import AB0_PACK
from ac_session_ops import AC0_PACK
from ad_session_ops import AD0_PACK
from ae_session_ops import AE0_PACK
from af_session_ops import AF0_PACK
from ag_session_ops import AG0_PACK
from ah_session_ops import AH0_PACK

__all__ = [
    "AI0_ID",
    "AI0_N",
    "AI0_PACK",
    "AI0_APP_IDS",
    "AI0_MIX",
    "AI0_THESIS",
    "missing_pack_source_ids",
    "pack_app_counts",
    "mix_ok",
    "unique_trial_ids",
    "overlaps_prior_questions",
    "decide_ai0_session",
]

AI0_ID = "AI0-SESSION"
AI0_N = 10
AI0_THESIS = (
    "Wave AI OPEN: freeze 10 held-out HITL asks "
    "(≠ AB · ≠ AC · ≠ AD · ≠ AE · ≠ AF · ≠ AG · ≠ AH); next AI1 H-GENPLUS"
)

AI0_APP_IDS: frozenset[str] = frozenset(
    {"known-ask", "howto", "long-doc"}
)

# Mix from .local/wave-ai/SESSION.md: 3 known · 5 howto · 2 long-doc.
AI0_MIX: Mapping[str, int] = {
    "known-ask": 3,
    "howto": 5,
    "long-doc": 2,
}

# Frozen held-out phrasing (.local/wave-ai/SESSION.md). Same list AI1–AI5.
AI0_PACK: tuple[dict[str, str], ...] = (
    {
        "id": "AI-HITL-01",
        "app_id": "known-ask",
        "source_id": "bip-0032",
        "question": (
            "BIP-32 extended-key serialization before Base58: how many "
            "bytes is the binary structure?"
        ),
        "gold": "78",
    },
    {
        "id": "AI-HITL-02",
        "app_id": "known-ask",
        "source_id": "bip-0340",
        "question": (
            "BIP-340 chooses the (R, s) Schnorr formulation mainly to "
            "enable which verification speedup?"
        ),
        "gold": "Batch verification",
    },
    {
        "id": "AI-HITL-03",
        "app_id": "known-ask",
        "source_id": "bip-0141",
        "question": (
            "BIP-141: version byte 0 with a 20-byte witness program is "
            "interpreted as which program type (acronym)?"
        ),
        "gold": "P2WPKH",
    },
    {
        "id": "AI-HITL-04",
        "app_id": "howto",
        "source_id": "python-tutorial-datastructures",
        "question": (
            "Insert value `x` at the front of list `a` — one method call."
        ),
        "gold": "a.insert(0, x)",
    },
    {
        "id": "AI-HITL-05",
        "app_id": "howto",
        "source_id": "python-tutorial-control",
        "question": (
            "In Python's if-ladder, what two-word phrase is `elif` short for?"
        ),
        "gold": "else if",
    },
    {
        "id": "AI-HITL-06",
        "app_id": "howto",
        "source_id": "python-tutorial-classes",
        "question": (
            "Name the built-in that checks whether one class is a subclass "
            "of another (tutorial inheritance section)."
        ),
        "gold": "issubclass",
    },
    {
        "id": "AI-HITL-07",
        "app_id": "howto",
        "source_id": "rust-book-ch03-02",
        "question": (
            "From Rust's data-types chapter: which floating-point type is "
            "the default?"
        ),
        "gold": "f64",
    },
    {
        "id": "AI-HITL-08",
        "app_id": "howto",
        "source_id": "rust-book-ch04-01",
        "question": (
            "Rust ownership chapter: stack push/pop order — expand the "
            "LIFO acronym."
        ),
        "gold": "last in, first out",
    },
    {
        "id": "AI-HITL-09",
        "app_id": "long-doc",
        "source_id": "bitcoin-rest",
        "question": (
            "Bitcoin Core REST: which GET path returns chaininfo as JSON "
            "only?"
        ),
        "gold": "GET /rest/chaininfo.json",
    },
    {
        "id": "AI-HITL-10",
        "app_id": "long-doc",
        "source_id": "bip-0001",
        "question": (
            "BIP-1: name the three BIP Type header values (comma-separated)."
        ),
        "gold": "Standards Track, Informational, Process",
    },
)


def missing_pack_source_ids(known: set[str]) -> list[str]:
    """
    GIVEN curated source_ids
    WHEN checking AI0 pack provenance
    THEN return pack source_ids absent from the registry.
    """
    return sorted(
        {
            str(p["source_id"])
            for p in AI0_PACK
            if str(p["source_id"]) not in known
        }
    )


def pack_app_counts(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> dict[str, int]:
    """
    GIVEN AI0 pack
    WHEN counting app_id
    THEN return {app_id: count}.
    """
    rows = pack if pack is not None else AI0_PACK
    out: dict[str, int] = {}
    for item in rows:
        key = str(item["app_id"])
        out[key] = out.get(key, 0) + 1
    return out


def mix_ok(pack: Sequence[Mapping[str, str]] | None = None) -> bool:
    """
    GIVEN AI0 pack
    WHEN checking app mix
    THEN True iff counts match AI0_MIX and every app_id is known.
    """
    counts = pack_app_counts(pack)
    if set(counts) != set(AI0_MIX):
        return False
    return all(counts.get(k) == v for k, v in AI0_MIX.items())


def unique_trial_ids(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    """
    GIVEN AI0 pack
    WHEN checking trial ids
    THEN True iff N distinct non-empty ids.
    """
    rows = pack if pack is not None else AI0_PACK
    ids = [str(p.get("id", "")).strip() for p in rows]
    return len(ids) == AI0_N and all(ids) and len(set(ids)) == AI0_N


def overlaps_prior_questions(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> list[str]:
    """
    GIVEN AI0 pack + AB0…AH0 packs
    WHEN checking held-out rule
    THEN return AI ids whose question text equals a prior-wave question.
    """
    prior = (
        {str(p["question"]).strip() for p in AB0_PACK}
        | {str(p["question"]).strip() for p in AC0_PACK}
        | {str(p["question"]).strip() for p in AD0_PACK}
        | {str(p["question"]).strip() for p in AE0_PACK}
        | {str(p["question"]).strip() for p in AF0_PACK}
        | {str(p["question"]).strip() for p in AG0_PACK}
        | {str(p["question"]).strip() for p in AH0_PACK}
    )
    rows = pack if pack is not None else AI0_PACK
    return [
        str(p["id"])
        for p in rows
        if str(p.get("question", "")).strip() in prior
    ]


def decide_ai0_session(
    *,
    known_sources: set[str],
    trials_dir_ready: bool,
    pack: Sequence[Mapping[str, str]] | None = None,
) -> str:
    """
    GIVEN curated registry + trials dir flag + pack
    WHEN applying AI0 SESSION gate
    THEN PROMOTE iff N=10, unique ids, mix, sources, ≠AB…AH Qs, trials ready.
    """
    rows = list(pack) if pack is not None else list(AI0_PACK)
    if len(rows) != AI0_N:
        return f"KILL (pack size {len(rows)} != {AI0_N})"
    if not unique_trial_ids(rows):
        return "KILL (trial ids missing or duplicated)"
    if not mix_ok(rows):
        return f"KILL (app mix {pack_app_counts(rows)} != {dict(AI0_MIX)})"
    clash = overlaps_prior_questions(rows)
    if clash:
        return (
            "KILL (verbatim AB/AC/AD/AE/AF/AG/AH questions: "
            f"{','.join(clash)})"
        )
    miss = missing_pack_source_ids(known_sources)
    if miss:
        return f"KILL (unknown source_id: {','.join(miss)})"
    for item in rows:
        if str(item.get("app_id", "")) not in AI0_APP_IDS:
            return f"KILL (bad app_id: {item.get('app_id')})"
        if not str(item.get("question", "")).strip():
            return f"KILL (empty question: {item.get('id')})"
        if not str(item.get("gold", "")).strip():
            return f"KILL (empty gold: {item.get('id')})"
        if not str(item.get("id", "")).startswith("AI-HITL-"):
            return f"KILL (bad trial id prefix: {item.get('id')})"
    if not trials_dir_ready:
        return "KILL (results/nano-lm/wave-ai/trials/ not ready)"
    return f"PROMOTE ({AI0_ID}: {AI0_THESIS})"
