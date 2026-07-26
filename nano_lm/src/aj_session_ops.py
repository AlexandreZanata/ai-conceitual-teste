"""Wave AJ0 SESSION: freeze 10 held-out HITL asks (≠ AB…AI)."""

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

__all__ = [
    "AJ0_ID",
    "AJ0_N",
    "AJ0_PACK",
    "AJ0_APP_IDS",
    "AJ0_MIX",
    "AJ0_THESIS",
    "missing_pack_source_ids",
    "pack_app_counts",
    "mix_ok",
    "unique_trial_ids",
    "overlaps_prior_questions",
    "decide_aj0_session",
]

AJ0_ID = "AJ0-SESSION"
AJ0_N = 10
AJ0_THESIS = (
    "Wave AJ OPEN: freeze 10 held-out HITL asks "
    "(≠ AB · ≠ AC · ≠ AD · ≠ AE · ≠ AF · ≠ AG · ≠ AH · ≠ AI); "
    "AJ1–AJ3 PROMOTE; next AJ4 H-FASTPEAK"
)

AJ0_APP_IDS: frozenset[str] = frozenset(
    {"known-ask", "howto", "long-doc"}
)

# Mix from .local/wave-aj/SESSION.md: 3 known · 5 howto · 2 long-doc.
AJ0_MIX: Mapping[str, int] = {
    "known-ask": 3,
    "howto": 5,
    "long-doc": 2,
}

# Frozen held-out phrasing (.local/wave-aj/SESSION.md). Same list AJ1–AJ5.
AJ0_PACK: tuple[dict[str, str], ...] = (
    {
        "id": "AJ-HITL-01",
        "app_id": "known-ask",
        "source_id": "bip-0039",
        "question": (
            "BIP-39: mnemonic entropy length ENT must be a multiple of "
            "how many bits?"
        ),
        "gold": "32",
    },
    {
        "id": "AJ-HITL-02",
        "app_id": "known-ask",
        "source_id": "bip-0032",
        "question": (
            "BIP-32 extended-key serialization: how many bytes is the "
            "depth field?"
        ),
        "gold": "1",
    },
    {
        "id": "AJ-HITL-03",
        "app_id": "known-ask",
        "source_id": "bip-0141",
        "question": (
            "BIP-141: version byte 0 with a 32-byte witness program is "
            "interpreted as which program type (acronym)?"
        ),
        "gold": "P2WSH",
    },
    {
        "id": "AJ-HITL-04",
        "app_id": "howto",
        "source_id": "python-tutorial-datastructures",
        "question": (
            "Preferred type for a queue with fast appends and pops from "
            "both ends — give module.class."
        ),
        "gold": "collections.deque",
    },
    {
        "id": "AJ-HITL-05",
        "app_id": "howto",
        "source_id": "python-tutorial-control",
        "question": (
            "Which statement skips the rest of the current loop iteration "
            "and continues with the next?"
        ),
        "gold": "continue",
    },
    {
        "id": "AJ-HITL-06",
        "app_id": "howto",
        "source_id": "python-tutorial-classes",
        "question": (
            "Name the built-in that checks an instance's type (tutorial "
            "inheritance tip)."
        ),
        "gold": "isinstance",
    },
    {
        "id": "AJ-HITL-07",
        "app_id": "howto",
        "source_id": "rust-book-ch03-02",
        "question": (
            "From Rust's data-types chapter: which integer type is the "
            "default when unsure?"
        ),
        "gold": "i32",
    },
    {
        "id": "AJ-HITL-08",
        "app_id": "howto",
        "source_id": "rust-book-ch05-01",
        "question": (
            "Name the Rust syntax that lets you write `username` instead "
            "of `username: username` in a struct literal."
        ),
        "gold": "field init shorthand",
    },
    {
        "id": "AJ-HITL-09",
        "app_id": "long-doc",
        "source_id": "bitcoin-json-rpc",
        "question": (
            "When two or more wallets are loaded, which JSON-RPC endpoint "
            "MUST be used for wallet requests?"
        ),
        "gold": "/wallet/<walletname>/",
    },
    {
        "id": "AJ-HITL-10",
        "app_id": "long-doc",
        "source_id": "rfc791",
        "question": (
            "RFC 791: expand the IHL acronym for the Internet header "
            "length field."
        ),
        "gold": "Internet Header Length",
    },
)


def missing_pack_source_ids(known: set[str]) -> list[str]:
    """
    GIVEN curated source_ids
    WHEN checking AJ0 pack provenance
    THEN return pack source_ids absent from the registry.
    """
    return sorted(
        {
            str(p["source_id"])
            for p in AJ0_PACK
            if str(p["source_id"]) not in known
        }
    )


def pack_app_counts(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> dict[str, int]:
    """
    GIVEN AJ0 pack
    WHEN counting app_id
    THEN return {app_id: count}.
    """
    rows = pack if pack is not None else AJ0_PACK
    out: dict[str, int] = {}
    for item in rows:
        key = str(item["app_id"])
        out[key] = out.get(key, 0) + 1
    return out


def mix_ok(pack: Sequence[Mapping[str, str]] | None = None) -> bool:
    """
    GIVEN AJ0 pack
    WHEN checking app mix
    THEN True iff counts match AJ0_MIX and every app_id is known.
    """
    counts = pack_app_counts(pack)
    if set(counts) != set(AJ0_MIX):
        return False
    return all(counts.get(k) == v for k, v in AJ0_MIX.items())


def unique_trial_ids(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    """
    GIVEN AJ0 pack
    WHEN checking trial ids
    THEN True iff N distinct non-empty ids.
    """
    rows = pack if pack is not None else AJ0_PACK
    ids = [str(p.get("id", "")).strip() for p in rows]
    return len(ids) == AJ0_N and all(ids) and len(set(ids)) == AJ0_N


def overlaps_prior_questions(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> list[str]:
    """
    GIVEN AJ0 pack + AB0…AI0 packs
    WHEN checking held-out rule
    THEN return AJ ids whose question text equals a prior-wave question.
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
    )
    rows = pack if pack is not None else AJ0_PACK
    return [
        str(p["id"])
        for p in rows
        if str(p.get("question", "")).strip() in prior
    ]


def decide_aj0_session(
    *,
    known_sources: set[str],
    trials_dir_ready: bool,
    pack: Sequence[Mapping[str, str]] | None = None,
) -> str:
    """
    GIVEN curated registry + trials dir flag + pack
    WHEN applying AJ0 SESSION gate
    THEN PROMOTE iff N=10, unique ids, mix, sources, ≠AB…AI Qs, trials ready.
    """
    rows = list(pack) if pack is not None else list(AJ0_PACK)
    if len(rows) != AJ0_N:
        return f"KILL (pack size {len(rows)} != {AJ0_N})"
    if not unique_trial_ids(rows):
        return "KILL (trial ids missing or duplicated)"
    if not mix_ok(rows):
        return f"KILL (app mix {pack_app_counts(rows)} != {dict(AJ0_MIX)})"
    clash = overlaps_prior_questions(rows)
    if clash:
        return (
            "KILL (verbatim AB/AC/AD/AE/AF/AG/AH/AI questions: "
            f"{','.join(clash)})"
        )
    miss = missing_pack_source_ids(known_sources)
    if miss:
        return f"KILL (unknown source_id: {','.join(miss)})"
    for item in rows:
        if str(item.get("app_id", "")) not in AJ0_APP_IDS:
            return f"KILL (bad app_id: {item.get('app_id')})"
        if not str(item.get("question", "")).strip():
            return f"KILL (empty question: {item.get('id')})"
        if not str(item.get("gold", "")).strip():
            return f"KILL (empty gold: {item.get('id')})"
        if not str(item.get("id", "")).startswith("AJ-HITL-"):
            return f"KILL (bad trial id prefix: {item.get('id')})"
    if not trials_dir_ready:
        return "KILL (results/nano-lm/wave-aj/trials/ not ready)"
    return f"PROMOTE ({AJ0_ID}: {AJ0_THESIS})"
