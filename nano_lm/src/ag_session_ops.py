"""Wave AG0 SESSION: freeze 10 held-out HITL asks (≠ AB…AF)."""

from __future__ import annotations

from typing import Mapping, Sequence

from ab_session_ops import AB0_PACK
from ac_session_ops import AC0_PACK
from ad_session_ops import AD0_PACK
from ae_session_ops import AE0_PACK
from af_session_ops import AF0_PACK

__all__ = [
    "AG0_ID",
    "AG0_N",
    "AG0_PACK",
    "AG0_APP_IDS",
    "AG0_MIX",
    "AG0_THESIS",
    "missing_pack_source_ids",
    "pack_app_counts",
    "mix_ok",
    "unique_trial_ids",
    "overlaps_prior_questions",
    "decide_ag0_session",
]

AG0_ID = "AG0-SESSION"
AG0_N = 10
AG0_THESIS = (
    "Wave AG OPEN: freeze 10 held-out HITL asks "
    "(≠ AB · ≠ AC · ≠ AD · ≠ AE · ≠ AF); next AG1 H-ANTIFP"
)

AG0_APP_IDS: frozenset[str] = frozenset(
    {"known-ask", "howto", "long-doc"}
)

# Mix from .local/wave-ag/SESSION.md: 3 known · 5 howto · 2 long-doc.
AG0_MIX: Mapping[str, int] = {
    "known-ask": 3,
    "howto": 5,
    "long-doc": 2,
}

# Frozen held-out phrasing (.local/wave-ag/SESSION.md). Same list AG1–AG5.
AG0_PACK: tuple[dict[str, str], ...] = (
    {
        "id": "AG-HITL-01",
        "app_id": "known-ask",
        "source_id": "bip-0032",
        "question": (
            "BIP-32: from which child index threshold are keys labeled "
            "hardened? Give the hex value."
        ),
        "gold": (
            "Indices ≥ 0x80000000 (2^31) are hardened child keys."
        ),
    },
    {
        "id": "AG-HITL-02",
        "app_id": "known-ask",
        "source_id": "bip-0039",
        "question": (
            "For BIP-39 with 128-bit ENT, how many checksum bits and how "
            "many mnemonic words?"
        ),
        "gold": (
            "4 checksum bits and 12 words "
            "(CS = ENT/32; MS = (ENT+CS)/11)."
        ),
    },
    {
        "id": "AG-HITL-03",
        "app_id": "known-ask",
        "source_id": "bip-0340",
        "question": (
            "BIP-340: Schnorr signature size and curve — one sentence."
        ),
        "gold": (
            "BIP-340 standardizes 64-byte Schnorr signatures over "
            "secp256k1."
        ),
    },
    {
        "id": "AG-HITL-04",
        "app_id": "howto",
        "source_id": "python-tutorial-datastructures",
        "question": (
            "Extend list `nums` with every item from iterable `more` — "
            "one method call."
        ),
        "gold": "nums.extend(more)",
    },
    {
        "id": "AG-HITL-05",
        "app_id": "howto",
        "source_id": "python-tutorial-io",
        "question": (
            "From an open text file `f`, read all remaining lines into a "
            "list — one call."
        ),
        "gold": "f.readlines()",
    },
    {
        "id": "AG-HITL-06",
        "app_id": "howto",
        "source_id": "rust-book-ch03",
        "question": (
            "Without `mut`, what compile error appears if you assign "
            "twice to `x`?"
        ),
        "gold": "cannot assign twice to immutable variable `x`",
    },
    {
        "id": "AG-HITL-07",
        "app_id": "howto",
        "source_id": "bitcoin-json-rpc",
        "question": (
            "What Content-Type do Bitcoin Core JSON-RPC curl examples use?"
        ),
        "gold": "application/json",
    },
    {
        "id": "AG-HITL-08",
        "app_id": "howto",
        "source_id": "bitcoin-rest",
        "question": (
            "REST path that returns a block hash by height — include "
            "encoding suffixes."
        ),
        "gold": "GET /rest/blockhashbyheight/<HEIGHT>.<bin|hex|json>",
    },
    {
        "id": "AG-HITL-09",
        "app_id": "long-doc",
        "source_id": "bip-0141",
        "question": (
            "BIP-141 coinbase witness commitment: which opcode starts "
            "that script?"
        ),
        "gold": "OP_RETURN (0x6a)",
    },
    {
        "id": "AG-HITL-10",
        "app_id": "long-doc",
        "source_id": "rfc8949",
        "question": (
            "RFC 8949: expand the CBOR acronym in plain words."
        ),
        "gold": "Concise Binary Object Representation",
    },
)


def missing_pack_source_ids(known: set[str]) -> list[str]:
    """
    GIVEN curated source_ids
    WHEN checking AG0 pack provenance
    THEN return pack source_ids absent from the registry.
    """
    return sorted(
        {
            str(p["source_id"])
            for p in AG0_PACK
            if str(p["source_id"]) not in known
        }
    )


def pack_app_counts(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> dict[str, int]:
    """
    GIVEN AG0 pack
    WHEN counting app_id
    THEN return {app_id: count}.
    """
    rows = pack if pack is not None else AG0_PACK
    out: dict[str, int] = {}
    for item in rows:
        key = str(item["app_id"])
        out[key] = out.get(key, 0) + 1
    return out


def mix_ok(pack: Sequence[Mapping[str, str]] | None = None) -> bool:
    """
    GIVEN AG0 pack
    WHEN checking app mix
    THEN True iff counts match AG0_MIX and every app_id is known.
    """
    counts = pack_app_counts(pack)
    if set(counts) != set(AG0_MIX):
        return False
    return all(counts.get(k) == v for k, v in AG0_MIX.items())


def unique_trial_ids(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    """
    GIVEN AG0 pack
    WHEN checking trial ids
    THEN True iff N distinct non-empty ids.
    """
    rows = pack if pack is not None else AG0_PACK
    ids = [str(p.get("id", "")).strip() for p in rows]
    return len(ids) == AG0_N and all(ids) and len(set(ids)) == AG0_N


def overlaps_prior_questions(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> list[str]:
    """
    GIVEN AG0 pack + AB0…AF0 packs
    WHEN checking held-out rule
    THEN return AG ids whose question text equals a prior-wave question.
    """
    prior = (
        {str(p["question"]).strip() for p in AB0_PACK}
        | {str(p["question"]).strip() for p in AC0_PACK}
        | {str(p["question"]).strip() for p in AD0_PACK}
        | {str(p["question"]).strip() for p in AE0_PACK}
        | {str(p["question"]).strip() for p in AF0_PACK}
    )
    rows = pack if pack is not None else AG0_PACK
    return [
        str(p["id"])
        for p in rows
        if str(p.get("question", "")).strip() in prior
    ]


def decide_ag0_session(
    *,
    known_sources: set[str],
    trials_dir_ready: bool,
    pack: Sequence[Mapping[str, str]] | None = None,
) -> str:
    """
    GIVEN curated registry + trials dir flag + pack
    WHEN applying AG0 SESSION gate
    THEN PROMOTE iff N=10, unique ids, mix, sources, ≠AB…AF Qs, trials ready.
    """
    rows = list(pack) if pack is not None else list(AG0_PACK)
    if len(rows) != AG0_N:
        return f"KILL (pack size {len(rows)} != {AG0_N})"
    if not unique_trial_ids(rows):
        return "KILL (trial ids missing or duplicated)"
    if not mix_ok(rows):
        return f"KILL (app mix {pack_app_counts(rows)} != {dict(AG0_MIX)})"
    clash = overlaps_prior_questions(rows)
    if clash:
        return (
            "KILL (verbatim AB/AC/AD/AE/AF questions: "
            f"{','.join(clash)})"
        )
    miss = missing_pack_source_ids(known_sources)
    if miss:
        return f"KILL (unknown source_id: {','.join(miss)})"
    for item in rows:
        if str(item.get("app_id", "")) not in AG0_APP_IDS:
            return f"KILL (bad app_id: {item.get('app_id')})"
        if not str(item.get("question", "")).strip():
            return f"KILL (empty question: {item.get('id')})"
        if not str(item.get("gold", "")).strip():
            return f"KILL (empty gold: {item.get('id')})"
        if not str(item.get("id", "")).startswith("AG-HITL-"):
            return f"KILL (bad trial id prefix: {item.get('id')})"
    if not trials_dir_ready:
        return "KILL (results/nano-lm/wave-ag/trials/ not ready)"
    return f"PROMOTE ({AG0_ID}: {AG0_THESIS})"
