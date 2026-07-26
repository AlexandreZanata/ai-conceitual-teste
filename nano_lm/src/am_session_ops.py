"""Wave AM0 SESSION: freeze 10 held-out HITL asks (≠ AB…AL)."""

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

__all__ = [
    "AM0_ID",
    "AM0_N",
    "AM0_PACK",
    "AM0_APP_IDS",
    "AM0_MIX",
    "AM0_THESIS",
    "missing_pack_source_ids",
    "pack_app_counts",
    "mix_ok",
    "unique_trial_ids",
    "overlaps_prior_questions",
    "decide_am0_session",
]

AM0_ID = "AM0-SESSION"
AM0_N = 10
AM0_THESIS = (
    "Wave AM OPEN: freeze 10 held-out HITL asks "
    "(≠ AB · ≠ AC · ≠ AD · ≠ AE · ≠ AF · ≠ AG · ≠ AH · ≠ AI · ≠ AJ · ≠ AK · ≠ AL); "
    "next AM1 H-GENTRUTH"
)

AM0_APP_IDS: frozenset[str] = frozenset(
    {"known-ask", "howto", "long-doc"}
)

# Mix from .local/wave-am/SESSION.md: 3 known · 5 howto · 2 long-doc.
AM0_MIX: Mapping[str, int] = {
    "known-ask": 3,
    "howto": 5,
    "long-doc": 2,
}

# Frozen held-out phrasing (.local/wave-am/SESSION.md). Same list AM1–AM5.
AM0_PACK: tuple[dict[str, str], ...] = (
    {
        "id": "AM-HITL-01",
        "app_id": "known-ask",
        "source_id": "bip-0039",
        "question": "BIP-39: for 160-bit ENT, how many mnemonic words?",
        "gold": "15",
    },
    {
        "id": "AM-HITL-02",
        "app_id": "known-ask",
        "source_id": "bip-0032",
        "question": (
            "BIP-32 extended-key serialization: how many bytes is the "
            "key data field (public or private)?"
        ),
        "gold": "33",
    },
    {
        "id": "AM-HITL-03",
        "app_id": "known-ask",
        "source_id": "bip-0141",
        "question": (
            "BIP-141: how many witness stack items MUST a version-0 "
            "P2WPKH input provide?"
        ),
        "gold": "2",
    },
    {
        "id": "AM-HITL-04",
        "app_id": "howto",
        "source_id": "python-tutorial-datastructures",
        "question": (
            "Return the zero-based index of value `x` in list `a` — "
            "one method call."
        ),
        "gold": "a.index(x)",
    },
    {
        "id": "AM-HITL-05",
        "app_id": "howto",
        "source_id": "python-tutorial-control",
        "question": (
            "Which clause on a for/while loop runs when the loop ends "
            "without break?"
        ),
        "gold": "else",
    },
    {
        "id": "AM-HITL-06",
        "app_id": "howto",
        "source_id": "python-tutorial-classes",
        "question": (
            "Name the built-in that sets a named attribute on an "
            "object (listed with getattr/delattr)."
        ),
        "gold": "setattr",
    },
    {
        "id": "AM-HITL-07",
        "app_id": "howto",
        "source_id": "rust-book-ch03-02",
        "question": (
            "From Rust's data-types chapter: how many bytes is a "
            "`char` value?"
        ),
        "gold": "4",
    },
    {
        "id": "AM-HITL-08",
        "app_id": "howto",
        "source_id": "rust-book-ch05-01",
        "question": (
            "Rust structs chapter: what are the named pieces of data "
            "inside a struct called?"
        ),
        "gold": "fields",
    },
    {
        "id": "AM-HITL-09",
        "app_id": "long-doc",
        "source_id": "bitcoin-rest",
        "question": (
            "Bitcoin Core REST: which GET path returns mempool "
            "contents as JSON?"
        ),
        "gold": "GET /rest/mempool/contents.json",
    },
    {
        "id": "AM-HITL-10",
        "app_id": "long-doc",
        "source_id": "rfc791",
        "question": (
            "RFC 791: how many bits is the IHL field of the "
            "Internet header?"
        ),
        "gold": "4",
    },
)


def missing_pack_source_ids(known: set[str]) -> list[str]:
    """
    GIVEN curated source_ids
    WHEN checking AM0 pack provenance
    THEN return pack source_ids absent from the registry.
    """
    return sorted(
        {
            str(p["source_id"])
            for p in AM0_PACK
            if str(p["source_id"]) not in known
        }
    )


def pack_app_counts(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> dict[str, int]:
    """
    GIVEN AM0 pack
    WHEN counting app_id
    THEN return {app_id: count}.
    """
    rows = pack if pack is not None else AM0_PACK
    out: dict[str, int] = {}
    for item in rows:
        key = str(item["app_id"])
        out[key] = out.get(key, 0) + 1
    return out


def mix_ok(pack: Sequence[Mapping[str, str]] | None = None) -> bool:
    """
    GIVEN AM0 pack
    WHEN checking app mix
    THEN True iff counts match AM0_MIX and every app_id is known.
    """
    counts = pack_app_counts(pack)
    if set(counts) != set(AM0_MIX):
        return False
    return all(counts.get(k) == v for k, v in AM0_MIX.items())


def unique_trial_ids(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    """
    GIVEN AM0 pack
    WHEN checking trial ids
    THEN True iff N distinct non-empty ids.
    """
    rows = pack if pack is not None else AM0_PACK
    ids = [str(p.get("id", "")).strip() for p in rows]
    return len(ids) == AM0_N and all(ids) and len(set(ids)) == AM0_N


def overlaps_prior_questions(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> list[str]:
    """
    GIVEN AM0 pack + AB0…AL0 packs
    WHEN checking held-out rule
    THEN return AM ids whose question text equals a prior-wave question.
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
    )
    rows = pack if pack is not None else AM0_PACK
    return [
        str(p["id"])
        for p in rows
        if str(p.get("question", "")).strip() in prior
    ]


def decide_am0_session(
    *,
    known_sources: set[str],
    trials_dir_ready: bool,
    pack: Sequence[Mapping[str, str]] | None = None,
) -> str:
    """
    GIVEN curated registry + trials dir flag + pack
    WHEN applying AM0 SESSION gate
    THEN PROMOTE iff N=10, unique ids, mix, sources, ≠AB…AL Qs, trials ready.
    """
    rows = list(pack) if pack is not None else list(AM0_PACK)
    if len(rows) != AM0_N:
        return f"KILL (pack size {len(rows)} != {AM0_N})"
    if not unique_trial_ids(rows):
        return "KILL (trial ids missing or duplicated)"
    if not mix_ok(rows):
        return f"KILL (app mix {pack_app_counts(rows)} != {dict(AM0_MIX)})"
    clash = overlaps_prior_questions(rows)
    if clash:
        return (
            "KILL (verbatim AB/AC/AD/AE/AF/AG/AH/AI/AJ/AK/AL questions: "
            f"{','.join(clash)})"
        )
    miss = missing_pack_source_ids(known_sources)
    if miss:
        return f"KILL (unknown source_id: {','.join(miss)})"
    for item in rows:
        if str(item.get("app_id", "")) not in AM0_APP_IDS:
            return f"KILL (bad app_id: {item.get('app_id')})"
        if not str(item.get("question", "")).strip():
            return f"KILL (empty question: {item.get('id')})"
        if not str(item.get("gold", "")).strip():
            return f"KILL (empty gold: {item.get('id')})"
        if not str(item.get("id", "")).startswith("AM-HITL-"):
            return f"KILL (bad trial id prefix: {item.get('id')})"
    if not trials_dir_ready:
        return "KILL (results/nano-lm/wave-am/trials/ not ready)"
    return f"PROMOTE ({AM0_ID}: {AM0_THESIS})"
