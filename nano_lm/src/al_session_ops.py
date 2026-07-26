"""Wave AL0 SESSION: freeze 10 held-out HITL asks (≠ AB…AK)."""

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

__all__ = [
    "AL0_ID",
    "AL0_N",
    "AL0_PACK",
    "AL0_APP_IDS",
    "AL0_MIX",
    "AL0_THESIS",
    "missing_pack_source_ids",
    "pack_app_counts",
    "mix_ok",
    "unique_trial_ids",
    "overlaps_prior_questions",
    "decide_al0_session",
]

AL0_ID = "AL0-SESSION"
AL0_N = 10
AL0_THESIS = (
    "Wave AL OPEN: freeze 10 held-out HITL asks "
    "(≠ AB · ≠ AC · ≠ AD · ≠ AE · ≠ AF · ≠ AG · ≠ AH · ≠ AI · ≠ AJ · ≠ AK); "
    "next AL1 H-GENFRESH"
)

AL0_APP_IDS: frozenset[str] = frozenset(
    {"known-ask", "howto", "long-doc"}
)

# Mix from .local/wave-al/SESSION.md: 3 known · 5 howto · 2 long-doc.
AL0_MIX: Mapping[str, int] = {
    "known-ask": 3,
    "howto": 5,
    "long-doc": 2,
}

# Frozen held-out phrasing (.local/wave-al/SESSION.md). Same list AL1–AL5.
AL0_PACK: tuple[dict[str, str], ...] = (
    {
        "id": "AL-HITL-01",
        "app_id": "known-ask",
        "source_id": "bip-0039",
        "question": "BIP-39: for 256-bit ENT, how many mnemonic words?",
        "gold": "24",
    },
    {
        "id": "AL-HITL-02",
        "app_id": "known-ask",
        "source_id": "bip-0032",
        "question": (
            "BIP-32 extended-key serialization: how many bytes is the "
            "parent fingerprint field?"
        ),
        "gold": "4",
    },
    {
        "id": "AL-HITL-03",
        "app_id": "known-ask",
        "source_id": "bip-0141",
        "question": (
            "BIP-141: what hex value MUST the 1-byte witness serialization "
            "flag be?"
        ),
        "gold": "0x01",
    },
    {
        "id": "AL-HITL-04",
        "app_id": "howto",
        "source_id": "python-tutorial-datastructures",
        "question": "Reverse list `a` in place — one method call.",
        "gold": "a.reverse()",
    },
    {
        "id": "AL-HITL-05",
        "app_id": "howto",
        "source_id": "python-tutorial-control",
        "question": (
            "Which keyword introduces Python structural pattern matching "
            "(match Statements)?"
        ),
        "gold": "match",
    },
    {
        "id": "AL-HITL-06",
        "app_id": "howto",
        "source_id": "python-tutorial-classes",
        "question": (
            "Name the built-in that deletes a named attribute from an "
            "object (listed with getattr/setattr)."
        ),
        "gold": "delattr",
    },
    {
        "id": "AL-HITL-07",
        "app_id": "howto",
        "source_id": "rust-book-ch03-02",
        "question": (
            "From Rust's data-types chapter: how many bytes is a Boolean "
            "value?"
        ),
        "gold": "1",
    },
    {
        "id": "AL-HITL-08",
        "app_id": "howto",
        "source_id": "rust-book-ch05-01",
        "question": (
            "Rust structs chapter: what name is given to structs that have "
            "no fields (like `()`)?"
        ),
        "gold": "unit-like structs",
    },
    {
        "id": "AL-HITL-09",
        "app_id": "long-doc",
        "source_id": "bitcoin-rest",
        "question": (
            "Bitcoin Core REST: which GET path returns deployment info as "
            "JSON (no blockhash)?"
        ),
        "gold": "GET /rest/deploymentinfo.json",
    },
    {
        "id": "AL-HITL-10",
        "app_id": "long-doc",
        "source_id": "rfc791",
        "question": (
            "RFC 791: how many bits is the Time to Live field of the "
            "Internet header?"
        ),
        "gold": "8",
    },
)


def missing_pack_source_ids(known: set[str]) -> list[str]:
    """
    GIVEN curated source_ids
    WHEN checking AL0 pack provenance
    THEN return pack source_ids absent from the registry.
    """
    return sorted(
        {
            str(p["source_id"])
            for p in AL0_PACK
            if str(p["source_id"]) not in known
        }
    )


def pack_app_counts(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> dict[str, int]:
    """
    GIVEN AL0 pack
    WHEN counting app_id
    THEN return {app_id: count}.
    """
    rows = pack if pack is not None else AL0_PACK
    out: dict[str, int] = {}
    for item in rows:
        key = str(item["app_id"])
        out[key] = out.get(key, 0) + 1
    return out


def mix_ok(pack: Sequence[Mapping[str, str]] | None = None) -> bool:
    """
    GIVEN AL0 pack
    WHEN checking app mix
    THEN True iff counts match AL0_MIX and every app_id is known.
    """
    counts = pack_app_counts(pack)
    if set(counts) != set(AL0_MIX):
        return False
    return all(counts.get(k) == v for k, v in AL0_MIX.items())


def unique_trial_ids(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    """
    GIVEN AL0 pack
    WHEN checking trial ids
    THEN True iff N distinct non-empty ids.
    """
    rows = pack if pack is not None else AL0_PACK
    ids = [str(p.get("id", "")).strip() for p in rows]
    return len(ids) == AL0_N and all(ids) and len(set(ids)) == AL0_N


def overlaps_prior_questions(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> list[str]:
    """
    GIVEN AL0 pack + AB0…AK0 packs
    WHEN checking held-out rule
    THEN return AL ids whose question text equals a prior-wave question.
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
    )
    rows = pack if pack is not None else AL0_PACK
    return [
        str(p["id"])
        for p in rows
        if str(p.get("question", "")).strip() in prior
    ]


def decide_al0_session(
    *,
    known_sources: set[str],
    trials_dir_ready: bool,
    pack: Sequence[Mapping[str, str]] | None = None,
) -> str:
    """
    GIVEN curated registry + trials dir flag + pack
    WHEN applying AL0 SESSION gate
    THEN PROMOTE iff N=10, unique ids, mix, sources, ≠AB…AK Qs, trials ready.
    """
    rows = list(pack) if pack is not None else list(AL0_PACK)
    if len(rows) != AL0_N:
        return f"KILL (pack size {len(rows)} != {AL0_N})"
    if not unique_trial_ids(rows):
        return "KILL (trial ids missing or duplicated)"
    if not mix_ok(rows):
        return f"KILL (app mix {pack_app_counts(rows)} != {dict(AL0_MIX)})"
    clash = overlaps_prior_questions(rows)
    if clash:
        return (
            "KILL (verbatim AB/AC/AD/AE/AF/AG/AH/AI/AJ/AK questions: "
            f"{','.join(clash)})"
        )
    miss = missing_pack_source_ids(known_sources)
    if miss:
        return f"KILL (unknown source_id: {','.join(miss)})"
    for item in rows:
        if str(item.get("app_id", "")) not in AL0_APP_IDS:
            return f"KILL (bad app_id: {item.get('app_id')})"
        if not str(item.get("question", "")).strip():
            return f"KILL (empty question: {item.get('id')})"
        if not str(item.get("gold", "")).strip():
            return f"KILL (empty gold: {item.get('id')})"
        if not str(item.get("id", "")).startswith("AL-HITL-"):
            return f"KILL (bad trial id prefix: {item.get('id')})"
    if not trials_dir_ready:
        return "KILL (results/nano-lm/wave-al/trials/ not ready)"
    return f"PROMOTE ({AL0_ID}: {AL0_THESIS})"
