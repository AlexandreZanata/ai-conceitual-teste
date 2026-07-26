"""Wave AE0 SESSION: freeze 10 held-out HITL asks (≠ AB · ≠ AC · ≠ AD)."""

from __future__ import annotations

from typing import Mapping, Sequence

from ab_session_ops import AB0_PACK
from ac_session_ops import AC0_PACK
from ad_session_ops import AD0_PACK

__all__ = [
    "AE0_ID",
    "AE0_N",
    "AE0_PACK",
    "AE0_APP_IDS",
    "AE0_MIX",
    "AE0_THESIS",
    "missing_pack_source_ids",
    "pack_app_counts",
    "mix_ok",
    "unique_trial_ids",
    "overlaps_prior_questions",
    "decide_ae0_session",
]

AE0_ID = "AE0-SESSION"
AE0_N = 10
AE0_THESIS = (
    "Wave AE OPEN: freeze 10 held-out HITL asks (≠ AB · ≠ AC · ≠ AD); "
    "next AE1 H-CTXMAX"
)

AE0_APP_IDS: frozenset[str] = frozenset(
    {"known-ask", "howto", "long-doc"}
)

# Mix mirrors AD: ~3 known · ~3 howto · ~4 long-doc (CTXMAX-friendly).
AE0_MIX: Mapping[str, int] = {
    "known-ask": 3,
    "howto": 3,
    "long-doc": 4,
}

# Frozen held-out phrasing (.local/wave-ae/SESSION.md). Same list AE1–AE5.
AE0_PACK: tuple[dict[str, str], ...] = (
    {
        "id": "AE-HITL-01",
        "app_id": "known-ask",
        "source_id": "bip-0032",
        "question": (
            "On BIP-32 mainnet, what Base58 prefixes do serialized extended "
            "private vs public keys start with?"
        ),
        "gold": (
            "Extended private keys start with xprv; extended public keys "
            "start with xpub."
        ),
    },
    {
        "id": "AE-HITL-02",
        "app_id": "known-ask",
        "source_id": "bip-0039",
        "question": (
            "When BIP-39 turns a mnemonic into a binary seed via PBKDF2, "
            "what iteration count and PRF does it use?"
        ),
        "gold": (
            "2048 iterations with HMAC-SHA512 as the pseudo-random function."
        ),
    },
    {
        "id": "AE-HITL-03",
        "app_id": "known-ask",
        "source_id": "bip-0340",
        "question": (
            "In BIP-340, how many bytes encode a public key in this proposal?"
        ),
        "gold": "Public keys are encoded as 32 bytes.",
    },
    {
        "id": "AE-HITL-04",
        "app_id": "howto",
        "source_id": "python-tutorial-datastructures",
        "question": (
            "The Python tutorial warns against using a list as a queue — "
            "why are lists inefficient for FIFO?"
        ),
        "gold": (
            "Appends and pops at the end are fast, but inserts or pops from "
            "the beginning shift every element and are slow."
        ),
    },
    {
        "id": "AE-HITL-05",
        "app_id": "howto",
        "source_id": "rust-book-ch03",
        "question": (
            "In Rust’s variables chapter, what is shadowing — one sentence?"
        ),
        "gold": (
            "Shadowing means declaring a new variable with the same name as "
            "a previous one so the first is shadowed by the second."
        ),
    },
    {
        "id": "AE-HITL-06",
        "app_id": "howto",
        "source_id": "python-tutorial-io",
        "question": (
            "How do you start a Python formatted string literal (f-string)? "
            "One short rule."
        ),
        "gold": (
            "Begin the string with f or F before the opening quotation mark."
        ),
    },
    {
        "id": "AE-HITL-07",
        "app_id": "long-doc",
        "source_id": "bitcoin-rest",
        "question": (
            "What REST path pattern returns a Bitcoin Core transaction by "
            "hash, and which three encodings can the suffix be?"
        ),
        "gold": "GET /rest/tx/<TX-HASH>.<bin|hex|json>",
    },
    {
        "id": "AE-HITL-08",
        "app_id": "long-doc",
        "source_id": "bitcoin-json-rpc",
        "question": (
            "When no rpcpassword is set, where does Bitcoin Core put the "
            "preferred auto-login RPC credentials?"
        ),
        "gold": (
            "In a .cookie file in the Bitcoin Core configuration directory."
        ),
    },
    {
        "id": "AE-HITL-09",
        "app_id": "long-doc",
        "source_id": "rfc791",
        "question": (
            "Per RFC 791, what must every module that processes a datagram "
            "do to the TTL, and why conceptually?"
        ),
        "gold": (
            "Decrease the TTL by at least one; TTL is an upper bound so "
            "undeliverable datagrams are discarded."
        ),
    },
    {
        "id": "AE-HITL-10",
        "app_id": "long-doc",
        "source_id": "bip-0141",
        "question": (
            "In BIP-141, how is wtxid defined relative to the unchanged txid?"
        ),
        "gold": (
            "txid stays double-SHA256 of the traditional serialization "
            "without witness; wtxid is double-SHA256 of the serialization "
            "that includes marker, flag, and witness data."
        ),
    },
)


def missing_pack_source_ids(known: set[str]) -> list[str]:
    """
    GIVEN curated source_ids
    WHEN checking AE0 pack provenance
    THEN return pack source_ids absent from the registry.
    """
    return sorted(
        {
            str(p["source_id"])
            for p in AE0_PACK
            if str(p["source_id"]) not in known
        }
    )


def pack_app_counts(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> dict[str, int]:
    """
    GIVEN AE0 pack
    WHEN counting app_id
    THEN return {app_id: count}.
    """
    rows = pack if pack is not None else AE0_PACK
    out: dict[str, int] = {}
    for item in rows:
        key = str(item["app_id"])
        out[key] = out.get(key, 0) + 1
    return out


def mix_ok(pack: Sequence[Mapping[str, str]] | None = None) -> bool:
    """
    GIVEN AE0 pack
    WHEN checking app mix
    THEN True iff counts match AE0_MIX and every app_id is known.
    """
    counts = pack_app_counts(pack)
    if set(counts) != set(AE0_MIX):
        return False
    return all(counts.get(k) == v for k, v in AE0_MIX.items())


def unique_trial_ids(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    """
    GIVEN AE0 pack
    WHEN checking trial ids
    THEN True iff N distinct non-empty ids.
    """
    rows = pack if pack is not None else AE0_PACK
    ids = [str(p.get("id", "")).strip() for p in rows]
    return len(ids) == AE0_N and all(ids) and len(set(ids)) == AE0_N


def overlaps_prior_questions(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> list[str]:
    """
    GIVEN AE0 pack + AB0 + AC0 + AD0 packs
    WHEN checking held-out rule
    THEN return AE ids whose question text equals an AB/AC/AD question.
    """
    prior = (
        {str(p["question"]).strip() for p in AB0_PACK}
        | {str(p["question"]).strip() for p in AC0_PACK}
        | {str(p["question"]).strip() for p in AD0_PACK}
    )
    rows = pack if pack is not None else AE0_PACK
    return [
        str(p["id"])
        for p in rows
        if str(p.get("question", "")).strip() in prior
    ]


def decide_ae0_session(
    *,
    known_sources: set[str],
    trials_dir_ready: bool,
    pack: Sequence[Mapping[str, str]] | None = None,
) -> str:
    """
    GIVEN curated registry + trials dir flag + pack
    WHEN applying AE0 SESSION gate
    THEN PROMOTE iff N=10, unique ids, mix, sources, ≠AB/AC/AD Qs, trials ready.
    """
    rows = list(pack) if pack is not None else list(AE0_PACK)
    if len(rows) != AE0_N:
        return f"KILL (pack size {len(rows)} != {AE0_N})"
    if not unique_trial_ids(rows):
        return "KILL (trial ids missing or duplicated)"
    if not mix_ok(rows):
        return f"KILL (app mix {pack_app_counts(rows)} != {dict(AE0_MIX)})"
    clash = overlaps_prior_questions(rows)
    if clash:
        return f"KILL (verbatim AB/AC/AD questions: {','.join(clash)})"
    miss = missing_pack_source_ids(known_sources)
    if miss:
        return f"KILL (unknown source_id: {','.join(miss)})"
    for item in rows:
        if str(item.get("app_id", "")) not in AE0_APP_IDS:
            return f"KILL (bad app_id: {item.get('app_id')})"
        if not str(item.get("question", "")).strip():
            return f"KILL (empty question: {item.get('id')})"
        if not str(item.get("gold", "")).strip():
            return f"KILL (empty gold: {item.get('id')})"
        if not str(item.get("id", "")).startswith("AE-HITL-"):
            return f"KILL (bad trial id prefix: {item.get('id')})"
    if not trials_dir_ready:
        return "KILL (results/nano-lm/wave-ae/trials/ not ready)"
    return f"PROMOTE ({AE0_ID}: {AE0_THESIS})"
