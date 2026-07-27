"""Wave AO0 SESSION: freeze 10 held-out HITL asks (≠ AB…AN)."""

from __future__ import annotations

from typing import Mapping, Sequence

from ab_session_ops import AB0_PACK
from ac_session_ops import AC0_PACK
from ad_session_ops import AD0_PACK
from ae_session_ops import AE0_PACK
from af_session_ops import AF0_PACK
from ag_session_ops import AG0_PACK
from ah_session_ops import AH0_PACK
from ai_session_ops import AI0_PACK
from aj_session_ops import AJ0_PACK
from ak_session_ops import AK0_PACK
from al_session_ops import AL0_PACK
from am_session_ops import AM0_PACK
from an_session_ops import AN0_PACK

__all__ = [
    "AO0_ID",
    "AO0_N",
    "AO0_PACK",
    "AO0_APP_IDS",
    "AO0_MIX",
    "AO0_THESIS",
    "missing_pack_source_ids",
    "pack_app_counts",
    "mix_ok",
    "unique_trial_ids",
    "overlaps_prior_questions",
    "decide_ao0_session",
]

AO0_ID = "AO0-SESSION"
AO0_N = 10
AO0_THESIS = (
    "Wave AO OPEN: freeze 10 held-out HITL asks "
    "(≠ AB · ≠ AC · ≠ AD · ≠ AE · ≠ AF · ≠ AG · ≠ AH · ≠ AI · ≠ AJ · "
    "≠ AK · ≠ AL · ≠ AM · ≠ AN); next AO1 H-GENCORE"
)

AO0_APP_IDS: frozenset[str] = frozenset(
    {"known-ask", "howto", "long-doc"}
)

# Mix: 3 known · 5 howto · 2 long-doc (same app mix as AN0).
AO0_MIX: Mapping[str, int] = {
    "known-ask": 3,
    "howto": 5,
    "long-doc": 2,
}

# Frozen held-out phrasing (.local/wave-ao/SESSION.md). Same list AO1–AO5.
AO0_PACK: tuple[dict[str, str], ...] = (
    {
        "id": "AO-HITL-01",
        "app_id": "known-ask",
        "source_id": "bip-0039",
        "question": "BIP-39: for 224-bit ENT, how many mnemonic words?",
        "gold": "21",
    },
    {
        "id": "AO-HITL-02",
        "app_id": "known-ask",
        "source_id": "bip-0032",
        "question": (
            "BIP-32 extended-key serialization: how many bytes is the "
            "version field?"
        ),
        "gold": "4",
    },
    {
        "id": "AO-HITL-03",
        "app_id": "known-ask",
        "source_id": "bip-0141",
        "question": (
            "BIP-141: what is the maximum witness program length L "
            "in bytes (≤ N)?"
        ),
        "gold": "40",
    },
    {
        "id": "AO-HITL-04",
        "app_id": "howto",
        "source_id": "python-tutorial-datastructures",
        "question": (
            "Return how many times value `x` appears in list `a` — "
            "one method call."
        ),
        "gold": "a.count(x)",
    },
    {
        "id": "AO-HITL-05",
        "app_id": "howto",
        "source_id": "python-tutorial-control",
        "question": (
            "Which keyword starts a Python loop that repeats while a "
            "condition is true?"
        ),
        "gold": "while",
    },
    {
        "id": "AO-HITL-06",
        "app_id": "howto",
        "source_id": "python-tutorial-classes",
        "question": (
            "Name the built-in that returns a proxy object for "
            "cooperative multiple inheritance (tutorial)."
        ),
        "gold": "super",
    },
    {
        "id": "AO-HITL-07",
        "app_id": "howto",
        "source_id": "rust-book-ch03-02",
        "question": (
            "From Rust's data-types chapter: which letter prefixes "
            "unsigned integer type names?"
        ),
        "gold": "u",
    },
    {
        "id": "AO-HITL-08",
        "app_id": "howto",
        "source_id": "rust-book-ch05-01",
        "question": (
            "Rust structs chapter: which keyword starts a struct type "
            "definition?"
        ),
        "gold": "struct",
    },
    {
        "id": "AO-HITL-09",
        "app_id": "long-doc",
        "source_id": "bitcoin-rest",
        "question": (
            "Bitcoin Core REST: which GET path pattern returns a full "
            "block by hash (include encoding suffixes)?"
        ),
        "gold": "GET /rest/block/<BLOCK-HASH>.<bin|hex|json>",
    },
    {
        "id": "AO-HITL-10",
        "app_id": "long-doc",
        "source_id": "rfc791",
        "question": (
            "RFC 791: how many bits is the Time to Live (TTL) field of "
            "the Internet header?"
        ),
        "gold": "8",
    },
)


def missing_pack_source_ids(known: set[str]) -> list[str]:
    """
    GIVEN curated source_ids
    WHEN checking AO0 pack provenance
    THEN return pack source_ids absent from the registry.
    """
    return sorted(
        {
            str(p["source_id"])
            for p in AO0_PACK
            if str(p["source_id"]) not in known
        }
    )


def pack_app_counts(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> dict[str, int]:
    """
    GIVEN AO0 pack
    WHEN counting app_id
    THEN return {app_id: count}.
    """
    rows = pack if pack is not None else AO0_PACK
    out: dict[str, int] = {}
    for item in rows:
        key = str(item["app_id"])
        out[key] = out.get(key, 0) + 1
    return out


def mix_ok(pack: Sequence[Mapping[str, str]] | None = None) -> bool:
    """
    GIVEN AO0 pack
    WHEN checking app mix
    THEN True iff counts match AO0_MIX and every app_id is known.
    """
    counts = pack_app_counts(pack)
    if set(counts) != set(AO0_MIX):
        return False
    return all(counts.get(k) == v for k, v in AO0_MIX.items())


def unique_trial_ids(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    """
    GIVEN AO0 pack
    WHEN checking trial ids
    THEN True iff N distinct non-empty ids.
    """
    rows = pack if pack is not None else AO0_PACK
    ids = [str(p.get("id", "")).strip() for p in rows]
    return len(ids) == AO0_N and all(ids) and len(set(ids)) == AO0_N


def overlaps_prior_questions(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> list[str]:
    """
    GIVEN AO0 pack + AB0…AN0 packs
    WHEN checking held-out rule
    THEN return AO ids whose question text equals a prior-wave question.
    """
    prior = (
        {str(p["question"]).strip() for p in AB0_PACK}
        | {str(p["question"]).strip() for p in AC0_PACK}
        | {str(p["question"]).strip() for p in AD0_PACK}
        | {str(p["question"]).strip() for p in AE0_PACK}
        | {str(p["question"]).strip() for p in AF0_PACK}
        | {str(p["question"]).strip() for p in AG0_PACK}
        | {str(p["question"]).strip() for p in AH0_PACK}
        | {str(p["question"]).strip() for p in AI0_PACK}
        | {str(p["question"]).strip() for p in AJ0_PACK}
        | {str(p["question"]).strip() for p in AK0_PACK}
        | {str(p["question"]).strip() for p in AL0_PACK}
        | {str(p["question"]).strip() for p in AM0_PACK}
        | {str(p["question"]).strip() for p in AN0_PACK}
    )
    rows = pack if pack is not None else AO0_PACK
    return [
        str(p["id"])
        for p in rows
        if str(p.get("question", "")).strip() in prior
    ]


def decide_ao0_session(
    *,
    known_sources: set[str],
    trials_dir_ready: bool,
    pack: Sequence[Mapping[str, str]] | None = None,
) -> str:
    """
    GIVEN curated registry + trials dir flag + pack
    WHEN applying AO0 SESSION gate
    THEN PROMOTE iff N=10, unique ids, mix, sources, ≠AB…AN Qs, trials ready.
    """
    rows = list(pack) if pack is not None else list(AO0_PACK)
    if len(rows) != AO0_N:
        return f"KILL (pack size {len(rows)} != {AO0_N})"
    if not unique_trial_ids(rows):
        return "KILL (trial ids missing or duplicated)"
    if not mix_ok(rows):
        return f"KILL (app mix {pack_app_counts(rows)} != {dict(AO0_MIX)})"
    clash = overlaps_prior_questions(rows)
    if clash:
        return (
            "KILL (verbatim AB…AN questions: "
            f"{','.join(clash)})"
        )
    miss = missing_pack_source_ids(known_sources)
    if miss:
        return f"KILL (unknown source_id: {','.join(miss)})"
    for item in rows:
        if str(item.get("app_id", "")) not in AO0_APP_IDS:
            return f"KILL (bad app_id: {item.get('app_id')})"
        if not str(item.get("question", "")).strip():
            return f"KILL (empty question: {item.get('id')})"
        if not str(item.get("gold", "")).strip():
            return f"KILL (empty gold: {item.get('id')})"
        if not str(item.get("id", "")).startswith("AO-HITL-"):
            return f"KILL (bad trial id prefix: {item.get('id')})"
    if not trials_dir_ready:
        return "KILL (results/nano-lm/wave-ao/trials/ not ready)"
    return f"PROMOTE ({AO0_ID}: {AO0_THESIS})"
