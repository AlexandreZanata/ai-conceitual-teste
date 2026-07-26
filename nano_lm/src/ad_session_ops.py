"""Wave AD0 SESSION: freeze 10 held-out HITL asks (≠ AB · ≠ AC)."""

from __future__ import annotations

from typing import Mapping, Sequence

from ab_session_ops import AB0_PACK
from ac_session_ops import AC0_PACK

__all__ = [
    "AD0_ID",
    "AD0_N",
    "AD0_PACK",
    "AD0_APP_IDS",
    "AD0_MIX",
    "AD0_THESIS",
    "missing_pack_source_ids",
    "pack_app_counts",
    "mix_ok",
    "unique_trial_ids",
    "overlaps_prior_questions",
    "decide_ad0_session",
]

AD0_ID = "AD0-SESSION"
AD0_N = 10
AD0_THESIS = (
    "Wave AD OPEN: freeze 10 held-out HITL asks (≠ AB · ≠ AC); "
    "next AD1 H-HARDPARA"
)

AD0_APP_IDS: frozenset[str] = frozenset(
    {"known-ask", "howto", "long-doc"}
)

# §13.5: ~3 paraphrase-hard · ~3 howto · ~4 long-doc
AD0_MIX: Mapping[str, int] = {
    "known-ask": 3,
    "howto": 3,
    "long-doc": 4,
}

# Frozen held-out phrasing (.local/wave-ad/SESSION.md). Same list AD1–AD5.
AD0_PACK: tuple[dict[str, str], ...] = (
    {
        "id": "AD-HITL-01",
        "app_id": "known-ask",
        "source_id": "bip-0340",
        "question": (
            "BIP-340 standardizes which signature scheme, and over which curve? "
            "One sentence."
        ),
        "gold": (
            "BIP-340 proposes a standard for 64-byte Schnorr signatures over "
            "secp256k1."
        ),
    },
    {
        "id": "AD-HITL-02",
        "app_id": "known-ask",
        "source_id": "bip-0141",
        "question": (
            "In BIP-141 SegWit, what kinds of data move into the segregated "
            "witness structure?"
        ),
        "gold": (
            "Scripts and signatures — data required to check transaction "
            "validity but not required to determine transaction effects."
        ),
    },
    {
        "id": "AD-HITL-03",
        "app_id": "known-ask",
        "source_id": "python-tutorial-datastructures",
        "question": (
            "In the Python tutorial data-structures chapter, how do you add one "
            "item to the end of a list?"
        ),
        "gold": "Call list.append(item) to push onto the end of the list.",
    },
    {
        "id": "AD-HITL-04",
        "app_id": "howto",
        "source_id": "python-tutorial-io",
        "question": (
            "Show the usual Python pattern to open a text file for reading "
            "using a context manager (one short snippet)."
        ),
        "gold": (
            "with open(filename, encoding=\"utf-8\") as f:\n"
            "    data = f.read()"
        ),
    },
    {
        "id": "AD-HITL-05",
        "app_id": "howto",
        "source_id": "rust-book-ch04-01",
        "question": (
            "In one sentence from the Rust book: what is ownership?"
        ),
        "gold": (
            "Ownership is a set of rules that govern how a Rust program "
            "manages memory, checked by the compiler."
        ),
    },
    {
        "id": "AD-HITL-06",
        "app_id": "howto",
        "source_id": "rust-book-ch05-01",
        "question": (
            "Sketch a Rust `User` struct with an `email: String` field "
            "(definition only)."
        ),
        "gold": "struct User {\n    email: String,\n}",
    },
    {
        "id": "AD-HITL-07",
        "app_id": "long-doc",
        "source_id": "bitcoin-developer-notes",
        "question": (
            "Per Bitcoin Core developer notes C++ style: how many spaces for "
            "block indentation (except namespaces)?"
        ),
        "gold": "4 space indentation (no tabs) for every block except namespaces.",
    },
    {
        "id": "AD-HITL-08",
        "app_id": "long-doc",
        "source_id": "rfc8949",
        "question": (
            "What data format does RFC 8949 specify, and which prior RFC does "
            "it obsolete?"
        ),
        "gold": (
            "CBOR (Concise Binary Object Representation); it obsoletes RFC 7049."
        ),
    },
    {
        "id": "AD-HITL-09",
        "app_id": "long-doc",
        "source_id": "rfc791",
        "question": (
            "What protocol does RFC 791 specify, and what blocks of data does "
            "it transmit between hosts?"
        ),
        "gold": (
            "Internet Protocol (IP); it transmits datagrams from sources to "
            "destinations."
        ),
    },
    {
        "id": "AD-HITL-10",
        "app_id": "long-doc",
        "source_id": "bitcoin-core-readme",
        "question": (
            "From the Bitcoin Core README: what network does it join, and what "
            "does it fully verify?"
        ),
        "gold": (
            "Bitcoin Core connects to the Bitcoin peer-to-peer network to "
            "download and fully verify the blockchain."
        ),
    },
)


def missing_pack_source_ids(known: set[str]) -> list[str]:
    """
    GIVEN curated source_ids
    WHEN checking AD0 pack provenance
    THEN return pack source_ids absent from the registry.
    """
    return sorted(
        {
            str(p["source_id"])
            for p in AD0_PACK
            if str(p["source_id"]) not in known
        }
    )


def pack_app_counts(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> dict[str, int]:
    """
    GIVEN AD0 pack
    WHEN counting app_id
    THEN return {app_id: count}.
    """
    rows = pack if pack is not None else AD0_PACK
    out: dict[str, int] = {}
    for item in rows:
        key = str(item["app_id"])
        out[key] = out.get(key, 0) + 1
    return out


def mix_ok(pack: Sequence[Mapping[str, str]] | None = None) -> bool:
    """
    GIVEN AD0 pack
    WHEN checking §13.5 mix
    THEN True iff counts match AD0_MIX and every app_id is known.
    """
    counts = pack_app_counts(pack)
    if set(counts) != set(AD0_MIX):
        return False
    return all(counts.get(k) == v for k, v in AD0_MIX.items())


def unique_trial_ids(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    """
    GIVEN AD0 pack
    WHEN checking trial ids
    THEN True iff N distinct non-empty ids.
    """
    rows = pack if pack is not None else AD0_PACK
    ids = [str(p.get("id", "")).strip() for p in rows]
    return len(ids) == AD0_N and all(ids) and len(set(ids)) == AD0_N


def overlaps_prior_questions(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> list[str]:
    """
    GIVEN AD0 pack + AB0 + AC0 packs
    WHEN checking held-out rule
    THEN return AD ids whose question text equals an AB or AC question.
    """
    prior = {str(p["question"]).strip() for p in AB0_PACK} | {
        str(p["question"]).strip() for p in AC0_PACK
    }
    rows = pack if pack is not None else AD0_PACK
    return [
        str(p["id"])
        for p in rows
        if str(p.get("question", "")).strip() in prior
    ]


def decide_ad0_session(
    *,
    known_sources: set[str],
    trials_dir_ready: bool,
    pack: Sequence[Mapping[str, str]] | None = None,
) -> str:
    """
    GIVEN curated registry + trials dir flag + pack
    WHEN applying AD0 SESSION gate
    THEN PROMOTE iff N=10, unique ids, mix, sources, ≠AB/AC Qs, trials ready.
    """
    rows = list(pack) if pack is not None else list(AD0_PACK)
    if len(rows) != AD0_N:
        return f"KILL (pack size {len(rows)} != {AD0_N})"
    if not unique_trial_ids(rows):
        return "KILL (trial ids missing or duplicated)"
    if not mix_ok(rows):
        return f"KILL (app mix {pack_app_counts(rows)} != {dict(AD0_MIX)})"
    clash = overlaps_prior_questions(rows)
    if clash:
        return f"KILL (verbatim AB/AC questions: {','.join(clash)})"
    miss = missing_pack_source_ids(known_sources)
    if miss:
        return f"KILL (unknown source_id: {','.join(miss)})"
    for item in rows:
        if str(item.get("app_id", "")) not in AD0_APP_IDS:
            return f"KILL (bad app_id: {item.get('app_id')})"
        if not str(item.get("question", "")).strip():
            return f"KILL (empty question: {item.get('id')})"
        if not str(item.get("gold", "")).strip():
            return f"KILL (empty gold: {item.get('id')})"
        if not str(item.get("id", "")).startswith("AD-HITL-"):
            return f"KILL (bad trial id prefix: {item.get('id')})"
    if not trials_dir_ready:
        return "KILL (results/nano-lm/wave-ad/trials/ not ready)"
    return f"PROMOTE ({AD0_ID}: {AD0_THESIS})"
