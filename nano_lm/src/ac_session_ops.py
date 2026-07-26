"""Wave AC0 SESSION: freeze 10 held-out HITL asks (≠ AB pack)."""

from __future__ import annotations

from typing import Mapping, Sequence

from ab_session_ops import AB0_PACK

__all__ = [
    "AC0_ID",
    "AC0_N",
    "AC0_PACK",
    "AC0_APP_IDS",
    "AC0_MIX",
    "AC0_THESIS",
    "missing_pack_source_ids",
    "pack_app_counts",
    "mix_ok",
    "unique_trial_ids",
    "overlaps_ab_questions",
    "decide_ac0_session",
]

AC0_ID = "AC0-SESSION"
AC0_N = 10
AC0_THESIS = (
    "Wave AC OPEN: freeze 10 held-out HITL asks (≠ AB); "
    "next AC1 H-CTXPLUS"
)

AC0_APP_IDS: frozenset[str] = frozenset(
    {"known-ask", "howto", "long-doc"}
)

# §12.5: ~3 paraphrase-hard · ~3 howto · ~4 long-doc
AC0_MIX: Mapping[str, int] = {
    "known-ask": 3,
    "howto": 3,
    "long-doc": 4,
}

# Frozen held-out phrasing (.local/wave-ac/SESSION.md). Same list AC1–AC5.
AC0_PACK: tuple[dict[str, str], ...] = (
    {
        "id": "AC-HITL-01",
        "app_id": "known-ask",
        "source_id": "bip-0032",
        "question": (
            "In BIP-32 HD wallets, what index range marks hardened child keys? "
            "One short answer."
        ),
        "gold": (
            "Hardened child keys use indices 2^31 through 2^32-1 "
            "(i ≥ 2^31 / 0x80000000)."
        ),
    },
    {
        "id": "AC-HITL-02",
        "app_id": "known-ask",
        "source_id": "bip-0001",
        "question": (
            "What is a BIP, and who is it meant to inform? Two sentences max."
        ),
        "gold": (
            "A BIP is a design document providing information to the Bitcoin "
            "community, or describing a new feature for Bitcoin or its "
            "processes or environment."
        ),
    },
    {
        "id": "AC-HITL-03",
        "app_id": "known-ask",
        "source_id": "python-tutorial-control",
        "question": (
            "Walk me through `for i in range(3): print(i)` — what values print, "
            "in order?"
        ),
        "gold": (
            "It prints 0, then 1, then 2 — range(3) excludes the endpoint 3."
        ),
    },
    {
        "id": "AC-HITL-04",
        "app_id": "howto",
        "source_id": "python-tutorial-classes",
        "question": (
            "Show a tiny Python `Point` class with `__init__(self, x, y)` "
            "storing both fields."
        ),
        "gold": (
            "class Point:\n"
            "    def __init__(self, x, y):\n"
            "        self.x = x\n"
            "        self.y = y"
        ),
    },
    {
        "id": "AC-HITL-05",
        "app_id": "howto",
        "source_id": "python-tutorial-intro",
        "question": (
            "Write a one-liner Python function `add(a, b)` that returns the sum."
        ),
        "gold": "def add(a, b): return a + b",
    },
    {
        "id": "AC-HITL-06",
        "app_id": "howto",
        "source_id": "rust-book-ch03",
        "question": (
            "How do I declare a mutable Rust integer `x` starting at 5? One line."
        ),
        "gold": "let mut x = 5;",
    },
    {
        "id": "AC-HITL-07",
        "app_id": "long-doc",
        "source_id": "rust-book-ch03-02",
        "question": (
            "Name the two main Rust data-type groups from the book’s "
            "data-types chapter."
        ),
        "gold": "Scalar types and compound types.",
    },
    {
        "id": "AC-HITL-08",
        "app_id": "long-doc",
        "source_id": "bip-0039",
        "question": (
            "Someone said “seed words” — what does BIP-39 actually specify for "
            "wallet entropy? Keep it practical."
        ),
        "gold": (
            "BIP-39 specifies a mnemonic sentence that encodes entropy "
            "(128–256 bits) and converts via PBKDF2 into a binary seed for "
            "HD wallets."
        ),
    },
    {
        "id": "AC-HITL-09",
        "app_id": "long-doc",
        "source_id": "bitcoin-rest",
        "question": (
            "How do I turn on Bitcoin Core’s unauthenticated REST interface?"
        ),
        "gold": (
            "Enable it with the `-rest` option; the REST API shares the "
            "JSON-RPC port (e.g. 8332 mainnet)."
        ),
    },
    {
        "id": "AC-HITL-10",
        "app_id": "long-doc",
        "source_id": "rfc8446",
        "question": (
            "From TLS 1.3 (RFC 8446 curated slice): what is the handshake "
            "trying to establish, in plain language?"
        ),
        "gold": (
            "The handshake authenticates the parties, negotiates cryptographic "
            "parameters, and establishes shared keying material."
        ),
    },
)


def missing_pack_source_ids(known: set[str]) -> list[str]:
    """
    GIVEN curated source_ids
    WHEN checking AC0 pack provenance
    THEN return pack source_ids absent from the registry.
    """
    return sorted(
        {
            str(p["source_id"])
            for p in AC0_PACK
            if str(p["source_id"]) not in known
        }
    )


def pack_app_counts(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> dict[str, int]:
    """
    GIVEN AC0 pack
    WHEN counting app_id
    THEN return {app_id: count}.
    """
    rows = pack if pack is not None else AC0_PACK
    out: dict[str, int] = {}
    for item in rows:
        key = str(item["app_id"])
        out[key] = out.get(key, 0) + 1
    return out


def mix_ok(pack: Sequence[Mapping[str, str]] | None = None) -> bool:
    """
    GIVEN AC0 pack
    WHEN checking §12.5 mix
    THEN True iff counts match AC0_MIX and every app_id is known.
    """
    counts = pack_app_counts(pack)
    if set(counts) != set(AC0_MIX):
        return False
    return all(counts.get(k) == v for k, v in AC0_MIX.items())


def unique_trial_ids(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    """
    GIVEN AC0 pack
    WHEN checking trial ids
    THEN True iff N distinct non-empty ids.
    """
    rows = pack if pack is not None else AC0_PACK
    ids = [str(p.get("id", "")).strip() for p in rows]
    return len(ids) == AC0_N and all(ids) and len(set(ids)) == AC0_N


def overlaps_ab_questions(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> list[str]:
    """
    GIVEN AC0 pack + AB0 pack
    WHEN checking held-out rule
    THEN return AC ids whose question text equals an AB question.
    """
    ab_q = {str(p["question"]).strip() for p in AB0_PACK}
    rows = pack if pack is not None else AC0_PACK
    return [
        str(p["id"])
        for p in rows
        if str(p.get("question", "")).strip() in ab_q
    ]


def decide_ac0_session(
    *,
    known_sources: set[str],
    trials_dir_ready: bool,
    pack: Sequence[Mapping[str, str]] | None = None,
) -> str:
    """
    GIVEN curated registry + trials dir flag + pack
    WHEN applying AC0 SESSION gate
    THEN PROMOTE iff N=10, unique ids, mix, sources, ≠AB Qs, trials ready.
    """
    rows = list(pack) if pack is not None else list(AC0_PACK)
    if len(rows) != AC0_N:
        return f"KILL (pack size {len(rows)} != {AC0_N})"
    if not unique_trial_ids(rows):
        return "KILL (trial ids missing or duplicated)"
    if not mix_ok(rows):
        return f"KILL (app mix {pack_app_counts(rows)} != {dict(AC0_MIX)})"
    clash = overlaps_ab_questions(rows)
    if clash:
        return f"KILL (verbatim AB questions: {','.join(clash)})"
    miss = missing_pack_source_ids(known_sources)
    if miss:
        return f"KILL (unknown source_id: {','.join(miss)})"
    for item in rows:
        if str(item.get("app_id", "")) not in AC0_APP_IDS:
            return f"KILL (bad app_id: {item.get('app_id')})"
        if not str(item.get("question", "")).strip():
            return f"KILL (empty question: {item.get('id')})"
        if not str(item.get("gold", "")).strip():
            return f"KILL (empty gold: {item.get('id')})"
        if not str(item.get("id", "")).startswith("AC-HITL-"):
            return f"KILL (bad trial id prefix: {item.get('id')})"
    if not trials_dir_ready:
        return "KILL (results/nano-lm/wave-ac/trials/ not ready)"
    return f"PROMOTE ({AC0_ID}: {AC0_THESIS})"
