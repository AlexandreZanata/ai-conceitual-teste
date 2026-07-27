"""Wave AN0 SESSION: freeze 10 held-out HITL asks (≠ AB…AM)."""

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

__all__ = [
    "AN0_ID",
    "AN0_N",
    "AN0_PACK",
    "AN0_APP_IDS",
    "AN0_MIX",
    "AN0_THESIS",
    "missing_pack_source_ids",
    "pack_app_counts",
    "mix_ok",
    "unique_trial_ids",
    "overlaps_prior_questions",
    "decide_an0_session",
]

AN0_ID = "AN0-SESSION"
AN0_N = 10
AN0_THESIS = (
    "Wave AN OPEN: freeze 10 held-out HITL asks "
    "(≠ AB · ≠ AC · ≠ AD · ≠ AE · ≠ AF · ≠ AG · ≠ AH · ≠ AI · ≠ AJ · "
    "≠ AK · ≠ AL · ≠ AM); next AN1 H-GENEDGE"
)

AN0_APP_IDS: frozenset[str] = frozenset(
    {"known-ask", "howto", "long-doc"}
)

# Mix: 3 known · 5 howto · 2 long-doc (same app mix as AM0).
AN0_MIX: Mapping[str, int] = {
    "known-ask": 3,
    "howto": 5,
    "long-doc": 2,
}

# Frozen held-out phrasing (.local/wave-an/SESSION.md). Same list AN1–AN5.
AN0_PACK: tuple[dict[str, str], ...] = (
    {
        "id": "AN-HITL-01",
        "app_id": "known-ask",
        "source_id": "bip-0039",
        "question": "BIP-39: for 192-bit ENT, how many mnemonic words?",
        "gold": "18",
    },
    {
        "id": "AN-HITL-02",
        "app_id": "known-ask",
        "source_id": "bip-0032",
        "question": (
            "BIP-32 extended-key serialization: how many bytes is the "
            "child number field?"
        ),
        "gold": "4",
    },
    {
        "id": "AN-HITL-03",
        "app_id": "known-ask",
        "source_id": "bip-0141",
        "question": (
            "BIP-141 P2WSH: what is the maximum witnessScript size "
            "in bytes (≤ N)?"
        ),
        "gold": "10000",
    },
    {
        "id": "AN-HITL-04",
        "app_id": "howto",
        "source_id": "python-tutorial-datastructures",
        "question": (
            "Remove the first item equal to value `x` from list `a` — "
            "one method call."
        ),
        "gold": "a.remove(x)",
    },
    {
        "id": "AN-HITL-05",
        "app_id": "howto",
        "source_id": "python-tutorial-control",
        "question": (
            "Which built-in produces an arithmetic progression of "
            "numbers commonly used with for loops?"
        ),
        "gold": "range",
    },
    {
        "id": "AN-HITL-06",
        "app_id": "howto",
        "source_id": "python-tutorial-classes",
        "question": (
            "Name the instance attribute that stores writable "
            "attributes as a dictionary."
        ),
        "gold": "__dict__",
    },
    {
        "id": "AN-HITL-07",
        "app_id": "howto",
        "source_id": "rust-book-ch03-02",
        "question": (
            "From Rust's data-types chapter: name the two primitive "
            "compound types."
        ),
        "gold": "tuples and arrays",
    },
    {
        "id": "AN-HITL-08",
        "app_id": "howto",
        "source_id": "rust-book-ch05-01",
        "question": (
            "Rust structs chapter: what name is given to structs that "
            "look like tuples but carry a type name?"
        ),
        "gold": "tuple structs",
    },
    {
        "id": "AN-HITL-09",
        "app_id": "long-doc",
        "source_id": "bitcoin-rest",
        "question": (
            "Bitcoin Core REST: which GET path pattern returns "
            "blockheaders (include encoding suffixes)?"
        ),
        "gold": "GET /rest/headers/<BLOCK-HASH>.<bin|hex|json>",
    },
    {
        "id": "AN-HITL-10",
        "app_id": "long-doc",
        "source_id": "rfc791",
        "question": (
            "RFC 791: how many bits is the Total Length field of the "
            "Internet header?"
        ),
        "gold": "16",
    },
)


def missing_pack_source_ids(known: set[str]) -> list[str]:
    """
    GIVEN curated source_ids
    WHEN checking AN0 pack provenance
    THEN return pack source_ids absent from the registry.
    """
    return sorted(
        {
            str(p["source_id"])
            for p in AN0_PACK
            if str(p["source_id"]) not in known
        }
    )


def pack_app_counts(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> dict[str, int]:
    """
    GIVEN AN0 pack
    WHEN counting app_id
    THEN return {app_id: count}.
    """
    rows = pack if pack is not None else AN0_PACK
    out: dict[str, int] = {}
    for item in rows:
        key = str(item["app_id"])
        out[key] = out.get(key, 0) + 1
    return out


def mix_ok(pack: Sequence[Mapping[str, str]] | None = None) -> bool:
    """
    GIVEN AN0 pack
    WHEN checking app mix
    THEN True iff counts match AN0_MIX and every app_id is known.
    """
    counts = pack_app_counts(pack)
    if set(counts) != set(AN0_MIX):
        return False
    return all(counts.get(k) == v for k, v in AN0_MIX.items())


def unique_trial_ids(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    """
    GIVEN AN0 pack
    WHEN checking trial ids
    THEN True iff N distinct non-empty ids.
    """
    rows = pack if pack is not None else AN0_PACK
    ids = [str(p.get("id", "")).strip() for p in rows]
    return len(ids) == AN0_N and all(ids) and len(set(ids)) == AN0_N


def overlaps_prior_questions(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> list[str]:
    """
    GIVEN AN0 pack + AB0…AM0 packs
    WHEN checking held-out rule
    THEN return AN ids whose question text equals a prior-wave question.
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
    )
    rows = pack if pack is not None else AN0_PACK
    return [
        str(p["id"])
        for p in rows
        if str(p.get("question", "")).strip() in prior
    ]


def decide_an0_session(
    *,
    known_sources: set[str],
    trials_dir_ready: bool,
    pack: Sequence[Mapping[str, str]] | None = None,
) -> str:
    """
    GIVEN curated registry + trials dir flag + pack
    WHEN applying AN0 SESSION gate
    THEN PROMOTE iff N=10, unique ids, mix, sources, ≠AB…AM Qs, trials ready.
    """
    rows = list(pack) if pack is not None else list(AN0_PACK)
    if len(rows) != AN0_N:
        return f"KILL (pack size {len(rows)} != {AN0_N})"
    if not unique_trial_ids(rows):
        return "KILL (trial ids missing or duplicated)"
    if not mix_ok(rows):
        return f"KILL (app mix {pack_app_counts(rows)} != {dict(AN0_MIX)})"
    clash = overlaps_prior_questions(rows)
    if clash:
        return (
            "KILL (verbatim AB…AM questions: "
            f"{','.join(clash)})"
        )
    miss = missing_pack_source_ids(known_sources)
    if miss:
        return f"KILL (unknown source_id: {','.join(miss)})"
    for item in rows:
        if str(item.get("app_id", "")) not in AN0_APP_IDS:
            return f"KILL (bad app_id: {item.get('app_id')})"
        if not str(item.get("question", "")).strip():
            return f"KILL (empty question: {item.get('id')})"
        if not str(item.get("gold", "")).strip():
            return f"KILL (empty gold: {item.get('id')})"
        if not str(item.get("id", "")).startswith("AN-HITL-"):
            return f"KILL (bad trial id prefix: {item.get('id')})"
    if not trials_dir_ready:
        return "KILL (results/nano-lm/wave-an/trials/ not ready)"
    return f"PROMOTE ({AN0_ID}: {AN0_THESIS})"
