"""Wave AB0 SESSION: freeze 10 real HITL asks (source_id + app_id)."""

from __future__ import annotations

from typing import Mapping, Sequence

__all__ = [
    "AB0_ID",
    "AB0_N",
    "AB0_PACK",
    "AB0_APP_IDS",
    "AB0_MIX",
    "AB0_THESIS",
    "missing_pack_source_ids",
    "pack_app_counts",
    "mix_ok",
    "unique_trial_ids",
    "decide_ab0_session",
]

AB0_ID = "AB0-SESSION"
AB0_N = 10
AB0_THESIS = (
    "Wave AB OPEN: freeze 10 real HITL asks with source_id + app_id; "
    "next AB1 H-SEMWRAP"
)

AB0_APP_IDS: frozenset[str] = frozenset(
    {"known-ask", "howto", "long-doc"}
)

# Expected mix (§11.5): ~4 known-ask · ~3 howto · ~3 long-doc
AB0_MIX: Mapping[str, int] = {
    "known-ask": 4,
    "howto": 3,
    "long-doc": 3,
}

# Frozen real-user phrasing (SESSION.md). Same list for AB1–AB6.
AB0_PACK: tuple[dict[str, str], ...] = (
    {
        "id": "AB-HITL-01",
        "app_id": "known-ask",
        "source_id": "bip-0039",
        "question": (
            "How do BIP-39 mnemonic phrases turn into a wallet seed? Keep it short."
        ),
        "gold": (
            "BIP-39 encodes entropy as a mnemonic sentence; PBKDF2 turns that "
            "mnemonic (plus optional passphrase) into a binary seed for HD wallets."
        ),
    },
    {
        "id": "AB-HITL-02",
        "app_id": "known-ask",
        "source_id": "bip-0340",
        "question": (
            "Which Bitcoin signature scheme does BIP-340 lock in, and over which curve?"
        ),
        "gold": (
            "BIP-340 standardizes 64-byte Schnorr signatures over secp256k1."
        ),
    },
    {
        "id": "AB-HITL-03",
        "app_id": "known-ask",
        "source_id": "python-tutorial-datastructures",
        "question": (
            "What’s the Python list method that appends a single element? "
            "Give a one-liner."
        ),
        "gold": "list.append — example: xs.append(item)",
    },
    {
        "id": "AB-HITL-04",
        "app_id": "known-ask",
        "source_id": "rust-book-ch04-01",
        "question": (
            "Explain Rust ownership like I’m shipping production code — "
            "two sentences max."
        ),
        "gold": (
            "Ownership is compile-time rules for memory without a GC; "
            "breaking them fails compilation rather than slowing runtime."
        ),
    },
    {
        "id": "AB-HITL-05",
        "app_id": "howto",
        "source_id": "python-tutorial-io",
        "question": (
            "I need to read a UTF-8 text file in Python — show the idiomatic "
            "`open(...)` line."
        ),
        "gold": 'f = open("workfile", "r", encoding="utf-8")',
    },
    {
        "id": "AB-HITL-06",
        "app_id": "howto",
        "source_id": "rust-book-ch05-01",
        "question": (
            "Define a minimal Rust `User` struct with a `name: String` field."
        ),
        "gold": "struct User {\n    name: String,\n}",
    },
    {
        "id": "AB-HITL-07",
        "app_id": "howto",
        "source_id": "bitcoin-json-rpc",
        "question": (
            "Which JSON-RPC URL paths does Bitcoin Core document for the RPC server?"
        ),
        "gold": "`/` and `/wallet/<walletname>/`",
    },
    {
        "id": "AB-HITL-08",
        "app_id": "long-doc",
        "source_id": "bip-0141",
        "question": (
            "From SegWit (BIP-141): what problem does separating witness data "
            "mainly solve?"
        ),
        "gold": (
            "Separating witness data from txid-critical fields fixes malleability "
            "and raises effective block capacity."
        ),
    },
    {
        "id": "AB-HITL-09",
        "app_id": "long-doc",
        "source_id": "bitcoin-core-readme",
        "question": (
            "In plain language, what does Bitcoin Core do on the P2P network "
            "with blocks and txs?"
        ),
        "gold": (
            "Bitcoin Core downloads and fully validates blocks and transactions "
            "on the P2P network, relays them to peers, and can serve wallet/RPC."
        ),
    },
    {
        "id": "AB-HITL-10",
        "app_id": "long-doc",
        "source_id": "bitcoin-doc-bips",
        "question": (
            "Which BIP lets multiple soft forks deploy in parallel "
            "(Core docs / bips.md)?"
        ),
        "gold": "BIP 9",
    },
)


def missing_pack_source_ids(known: set[str]) -> list[str]:
    """
    GIVEN curated source_ids
    WHEN checking AB0 pack provenance
    THEN return pack source_ids absent from the registry.
    """
    return sorted(
        {
            str(p["source_id"])
            for p in AB0_PACK
            if str(p["source_id"]) not in known
        }
    )


def pack_app_counts(pack: Sequence[Mapping[str, str]] | None = None) -> dict[str, int]:
    """
    GIVEN AB0 pack
    WHEN counting app_id
    THEN return {app_id: count}.
    """
    rows = pack if pack is not None else AB0_PACK
    out: dict[str, int] = {}
    for item in rows:
        key = str(item["app_id"])
        out[key] = out.get(key, 0) + 1
    return out


def mix_ok(pack: Sequence[Mapping[str, str]] | None = None) -> bool:
    """
    GIVEN AB0 pack
    WHEN checking §11.5 mix
    THEN True iff counts match AB0_MIX and every app_id is known.
    """
    counts = pack_app_counts(pack)
    if set(counts) != set(AB0_MIX):
        return False
    return all(counts.get(k) == v for k, v in AB0_MIX.items())


def unique_trial_ids(pack: Sequence[Mapping[str, str]] | None = None) -> bool:
    """
    GIVEN AB0 pack
    WHEN checking trial ids
    THEN True iff N distinct non-empty ids.
    """
    rows = pack if pack is not None else AB0_PACK
    ids = [str(p.get("id", "")).strip() for p in rows]
    return len(ids) == AB0_N and all(ids) and len(set(ids)) == AB0_N


def decide_ab0_session(
    *,
    known_sources: set[str],
    trials_dir_ready: bool,
    pack: Sequence[Mapping[str, str]] | None = None,
) -> str:
    """
    GIVEN curated registry + trials dir flag + pack
    WHEN applying AB0 SESSION gate
    THEN PROMOTE iff N=10, unique ids, mix, sources, trials ready.
    """
    rows = list(pack) if pack is not None else list(AB0_PACK)
    if len(rows) != AB0_N:
        return f"KILL (pack size {len(rows)} != {AB0_N})"
    if not unique_trial_ids(rows):
        return "KILL (trial ids missing or duplicated)"
    if not mix_ok(rows):
        return f"KILL (app mix {pack_app_counts(rows)} != {dict(AB0_MIX)})"
    miss = missing_pack_source_ids(known_sources)
    if miss:
        return f"KILL (unknown source_id: {','.join(miss)})"
    for item in rows:
        if str(item.get("app_id", "")) not in AB0_APP_IDS:
            return f"KILL (bad app_id: {item.get('app_id')})"
        if not str(item.get("question", "")).strip():
            return f"KILL (empty question: {item.get('id')})"
        if not str(item.get("gold", "")).strip():
            return f"KILL (empty gold: {item.get('id')})"
    if not trials_dir_ready:
        return "KILL (results/nano-lm/wave-ab/trials/ not ready)"
    return f"PROMOTE ({AB0_ID}: {AB0_THESIS})"
