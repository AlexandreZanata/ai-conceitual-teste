"""Wave AK0 SESSION: freeze 10 held-out HITL asks (≠ AB…AJ)."""

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

__all__ = [
    "AK0_ID",
    "AK0_N",
    "AK0_PACK",
    "AK0_APP_IDS",
    "AK0_MIX",
    "AK0_THESIS",
    "missing_pack_source_ids",
    "pack_app_counts",
    "mix_ok",
    "unique_trial_ids",
    "overlaps_prior_questions",
    "decide_ak0_session",
]

AK0_ID = "AK0-SESSION"
AK0_N = 10
AK0_THESIS = (
    "Wave AK OPEN: freeze 10 held-out HITL asks "
    "(≠ AB · ≠ AC · ≠ AD · ≠ AE · ≠ AF · ≠ AG · ≠ AH · ≠ AI · ≠ AJ); "
    "next AK1 H-GENTRUE"
)

AK0_APP_IDS: frozenset[str] = frozenset(
    {"known-ask", "howto", "long-doc"}
)

# Mix from .local/wave-ak/SESSION.md: 3 known · 5 howto · 2 long-doc.
AK0_MIX: Mapping[str, int] = {
    "known-ask": 3,
    "howto": 5,
    "long-doc": 2,
}

# Frozen held-out phrasing (.local/wave-ak/SESSION.md). Same list AK1–AK5.
AK0_PACK: tuple[dict[str, str], ...] = (
    {
        "id": "AK-HITL-01",
        "app_id": "known-ask",
        "source_id": "bip-0039",
        "question": (
            "BIP-39: what is the allowed ENT size range in bits "
            "(write low-high)?"
        ),
        "gold": "128-256",
    },
    {
        "id": "AK-HITL-02",
        "app_id": "known-ask",
        "source_id": "bip-0032",
        "question": "BIP-32: how many bytes long is the chain code?",
        "gold": "32",
    },
    {
        "id": "AK-HITL-03",
        "app_id": "known-ask",
        "source_id": "bip-0141",
        "question": (
            "BIP-141: what hex value MUST the 1-byte witness serialization "
            "marker be?"
        ),
        "gold": "0x00",
    },
    {
        "id": "AK-HITL-04",
        "app_id": "howto",
        "source_id": "python-tutorial-datastructures",
        "question": "Remove all items from list `a` — one method call.",
        "gold": "a.clear()",
    },
    {
        "id": "AK-HITL-05",
        "app_id": "howto",
        "source_id": "python-tutorial-control",
        "question": (
            "Which statement breaks out of the innermost enclosing for "
            "or while loop?"
        ),
        "gold": "break",
    },
    {
        "id": "AK-HITL-06",
        "app_id": "howto",
        "source_id": "python-tutorial-classes",
        "question": (
            "Name the built-in that fetches a named attribute from an "
            "object (listed with setattr/delattr)."
        ),
        "gold": "getattr",
    },
    {
        "id": "AK-HITL-07",
        "app_id": "howto",
        "source_id": "rust-book-ch03-02",
        "question": (
            "From Rust's data-types chapter: what type name is used for "
            "Boolean values?"
        ),
        "gold": "bool",
    },
    {
        "id": "AK-HITL-08",
        "app_id": "howto",
        "source_id": "rust-book-ch05-01",
        "question": (
            "To read a field of a Rust struct instance, which access "
            "notation is used?"
        ),
        "gold": "dot notation",
    },
    {
        "id": "AK-HITL-09",
        "app_id": "long-doc",
        "source_id": "bitcoin-rest",
        "question": (
            "Bitcoin Core REST: which GET path returns mempool info "
            "as JSON?"
        ),
        "gold": "GET /rest/mempool/info.json",
    },
    {
        "id": "AK-HITL-10",
        "app_id": "long-doc",
        "source_id": "rfc791",
        "question": (
            "RFC 791: how many bits is the Version field of the "
            "Internet header?"
        ),
        "gold": "4",
    },
)


def missing_pack_source_ids(known: set[str]) -> list[str]:
    """
    GIVEN curated source_ids
    WHEN checking AK0 pack provenance
    THEN return pack source_ids absent from the registry.
    """
    return sorted(
        {
            str(p["source_id"])
            for p in AK0_PACK
            if str(p["source_id"]) not in known
        }
    )


def pack_app_counts(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> dict[str, int]:
    """
    GIVEN AK0 pack
    WHEN counting app_id
    THEN return {app_id: count}.
    """
    rows = pack if pack is not None else AK0_PACK
    out: dict[str, int] = {}
    for item in rows:
        key = str(item["app_id"])
        out[key] = out.get(key, 0) + 1
    return out


def mix_ok(pack: Sequence[Mapping[str, str]] | None = None) -> bool:
    """
    GIVEN AK0 pack
    WHEN checking app mix
    THEN True iff counts match AK0_MIX and every app_id is known.
    """
    counts = pack_app_counts(pack)
    if set(counts) != set(AK0_MIX):
        return False
    return all(counts.get(k) == v for k, v in AK0_MIX.items())


def unique_trial_ids(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    """
    GIVEN AK0 pack
    WHEN checking trial ids
    THEN True iff N distinct non-empty ids.
    """
    rows = pack if pack is not None else AK0_PACK
    ids = [str(p.get("id", "")).strip() for p in rows]
    return len(ids) == AK0_N and all(ids) and len(set(ids)) == AK0_N


def overlaps_prior_questions(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> list[str]:
    """
    GIVEN AK0 pack + AB0…AJ0 packs
    WHEN checking held-out rule
    THEN return AK ids whose question text equals a prior-wave question.
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
    )
    rows = pack if pack is not None else AK0_PACK
    return [
        str(p["id"])
        for p in rows
        if str(p.get("question", "")).strip() in prior
    ]


def decide_ak0_session(
    *,
    known_sources: set[str],
    trials_dir_ready: bool,
    pack: Sequence[Mapping[str, str]] | None = None,
) -> str:
    """
    GIVEN curated registry + trials dir flag + pack
    WHEN applying AK0 SESSION gate
    THEN PROMOTE iff N=10, unique ids, mix, sources, ≠AB…AJ Qs, trials ready.
    """
    rows = list(pack) if pack is not None else list(AK0_PACK)
    if len(rows) != AK0_N:
        return f"KILL (pack size {len(rows)} != {AK0_N})"
    if not unique_trial_ids(rows):
        return "KILL (trial ids missing or duplicated)"
    if not mix_ok(rows):
        return f"KILL (app mix {pack_app_counts(rows)} != {dict(AK0_MIX)})"
    clash = overlaps_prior_questions(rows)
    if clash:
        return (
            "KILL (verbatim AB/AC/AD/AE/AF/AG/AH/AI/AJ questions: "
            f"{','.join(clash)})"
        )
    miss = missing_pack_source_ids(known_sources)
    if miss:
        return f"KILL (unknown source_id: {','.join(miss)})"
    for item in rows:
        if str(item.get("app_id", "")) not in AK0_APP_IDS:
            return f"KILL (bad app_id: {item.get('app_id')})"
        if not str(item.get("question", "")).strip():
            return f"KILL (empty question: {item.get('id')})"
        if not str(item.get("gold", "")).strip():
            return f"KILL (empty gold: {item.get('id')})"
        if not str(item.get("id", "")).startswith("AK-HITL-"):
            return f"KILL (bad trial id prefix: {item.get('id')})"
    if not trials_dir_ready:
        return "KILL (results/nano-lm/wave-ak/trials/ not ready)"
    return f"PROMOTE ({AK0_ID}: {AK0_THESIS})"
