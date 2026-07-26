"""Wave AF0 SESSION: freeze 10 held-out HITL asks (≠ AB · ≠ AC · ≠ AD · ≠ AE)."""

from __future__ import annotations

from typing import Mapping, Sequence

from ab_session_ops import AB0_PACK
from ac_session_ops import AC0_PACK
from ad_session_ops import AD0_PACK
from ae_session_ops import AE0_PACK

__all__ = [
    "AF0_ID",
    "AF0_N",
    "AF0_PACK",
    "AF0_APP_IDS",
    "AF0_MIX",
    "AF0_THESIS",
    "missing_pack_source_ids",
    "pack_app_counts",
    "mix_ok",
    "unique_trial_ids",
    "overlaps_prior_questions",
    "decide_af0_session",
]

AF0_ID = "AF0-SESSION"
AF0_N = 10
AF0_THESIS = (
    "Wave AF OPEN: freeze 10 held-out HITL asks "
    "(≠ AB · ≠ AC · ≠ AD · ≠ AE); next AF1 H-CTXULTRA"
)

AF0_APP_IDS: frozenset[str] = frozenset(
    {"known-ask", "howto", "long-doc"}
)

# Mix from .local/wave-af/SESSION.md: 3 known · 5 howto · 2 long-doc.
AF0_MIX: Mapping[str, int] = {
    "known-ask": 3,
    "howto": 5,
    "long-doc": 2,
}

# Frozen held-out phrasing (.local/wave-af/SESSION.md). Same list AF1–AF5.
AF0_PACK: tuple[dict[str, str], ...] = (
    {
        "id": "AF-HITL-01",
        "app_id": "known-ask",
        "source_id": "bip-0001",
        "question": (
            "In one or two sentences: what is a BIP, and who should care?"
        ),
        "gold": (
            "A BIP is a Bitcoin Improvement Proposal — a design document for "
            "the Bitcoin community. Authors, implementers, and anyone "
            "tracking protocol changes should care."
        ),
    },
    {
        "id": "AF-HITL-02",
        "app_id": "known-ask",
        "source_id": "bitcoin-doc-bips",
        "question": (
            "Which BIP does Bitcoin Core document for parallel soft-fork "
            "deployments?"
        ),
        "gold": "BIP 9 (version-bits parallel soft-fork deployments).",
    },
    {
        "id": "AF-HITL-03",
        "app_id": "known-ask",
        "source_id": "rust-book-ch03-02",
        "question": (
            "Name the two main Rust data-type groups from the data-types "
            "chapter."
        ),
        "gold": "Scalar types and compound types.",
    },
    {
        "id": "AF-HITL-04",
        "app_id": "howto",
        "source_id": "python-tutorial-classes",
        "question": (
            "Minimal `Point` with `__init__(self, x, y)` — paste the class."
        ),
        "gold": (
            "class Point:\n"
            "    def __init__(self, x, y):\n"
            "        self.x = x\n"
            "        self.y = y"
        ),
    },
    {
        "id": "AF-HITL-05",
        "app_id": "howto",
        "source_id": "python-tutorial-control",
        "question": (
            "What values does `for i in range(3): print(i)` print, in order?"
        ),
        "gold": "0, then 1, then 2 (endpoint excluded).",
    },
    {
        "id": "AF-HITL-06",
        "app_id": "howto",
        "source_id": "python-tutorial-intro",
        "question": (
            "Write `add(a, b)` that returns the sum — one short function."
        ),
        "gold": "def add(a, b):\n    return a + b",
    },
    {
        "id": "AF-HITL-07",
        "app_id": "howto",
        "source_id": "rust-book-ch04-01",
        "question": (
            "Why does Rust ownership exist if there’s no garbage collector? "
            "Two sentences."
        ),
        "gold": (
            "Ownership is a compile-time memory-management system: rules "
            "checked by the compiler replace GC or manual free. Violations "
            "fail to compile, so runtime does not pay a garbage-collector cost."
        ),
    },
    {
        "id": "AF-HITL-08",
        "app_id": "howto",
        "source_id": "rust-book-ch05-01",
        "question": (
            "Define `struct User { name: String }` — show the definition."
        ),
        "gold": "struct User {\n    name: String,\n}",
    },
    {
        "id": "AF-HITL-09",
        "app_id": "long-doc",
        "source_id": "bitcoin-core-readme",
        "question": (
            "What does Bitcoin Core do on the P2P network with blocks and "
            "transactions?"
        ),
        "gold": (
            "It connects to the Bitcoin peer-to-peer network to download and "
            "fully validate blocks and transactions."
        ),
    },
    {
        "id": "AF-HITL-10",
        "app_id": "long-doc",
        "source_id": "rfc8446",
        "question": (
            "TLS 1.3 (RFC 8446 slice): what is the handshake trying to "
            "establish, plainly?"
        ),
        "gold": (
            "An authenticated negotiated channel: protocol parameters and "
            "shared secret keying material so later records stay confidential "
            "and integrity-protected."
        ),
    },
)


def missing_pack_source_ids(known: set[str]) -> list[str]:
    """
    GIVEN curated source_ids
    WHEN checking AF0 pack provenance
    THEN return pack source_ids absent from the registry.
    """
    return sorted(
        {
            str(p["source_id"])
            for p in AF0_PACK
            if str(p["source_id"]) not in known
        }
    )


def pack_app_counts(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> dict[str, int]:
    """
    GIVEN AF0 pack
    WHEN counting app_id
    THEN return {app_id: count}.
    """
    rows = pack if pack is not None else AF0_PACK
    out: dict[str, int] = {}
    for item in rows:
        key = str(item["app_id"])
        out[key] = out.get(key, 0) + 1
    return out


def mix_ok(pack: Sequence[Mapping[str, str]] | None = None) -> bool:
    """
    GIVEN AF0 pack
    WHEN checking app mix
    THEN True iff counts match AF0_MIX and every app_id is known.
    """
    counts = pack_app_counts(pack)
    if set(counts) != set(AF0_MIX):
        return False
    return all(counts.get(k) == v for k, v in AF0_MIX.items())


def unique_trial_ids(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    """
    GIVEN AF0 pack
    WHEN checking trial ids
    THEN True iff N distinct non-empty ids.
    """
    rows = pack if pack is not None else AF0_PACK
    ids = [str(p.get("id", "")).strip() for p in rows]
    return len(ids) == AF0_N and all(ids) and len(set(ids)) == AF0_N


def overlaps_prior_questions(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> list[str]:
    """
    GIVEN AF0 pack + AB0 + AC0 + AD0 + AE0 packs
    WHEN checking held-out rule
    THEN return AF ids whose question text equals a prior-wave question.
    """
    prior = (
        {str(p["question"]).strip() for p in AB0_PACK}
        | {str(p["question"]).strip() for p in AC0_PACK}
        | {str(p["question"]).strip() for p in AD0_PACK}
        | {str(p["question"]).strip() for p in AE0_PACK}
    )
    rows = pack if pack is not None else AF0_PACK
    return [
        str(p["id"])
        for p in rows
        if str(p.get("question", "")).strip() in prior
    ]


def decide_af0_session(
    *,
    known_sources: set[str],
    trials_dir_ready: bool,
    pack: Sequence[Mapping[str, str]] | None = None,
) -> str:
    """
    GIVEN curated registry + trials dir flag + pack
    WHEN applying AF0 SESSION gate
    THEN PROMOTE iff N=10, unique ids, mix, sources, ≠AB/AC/AD/AE Qs, trials ready.
    """
    rows = list(pack) if pack is not None else list(AF0_PACK)
    if len(rows) != AF0_N:
        return f"KILL (pack size {len(rows)} != {AF0_N})"
    if not unique_trial_ids(rows):
        return "KILL (trial ids missing or duplicated)"
    if not mix_ok(rows):
        return f"KILL (app mix {pack_app_counts(rows)} != {dict(AF0_MIX)})"
    clash = overlaps_prior_questions(rows)
    if clash:
        return (
            "KILL (verbatim AB/AC/AD/AE questions: "
            f"{','.join(clash)})"
        )
    miss = missing_pack_source_ids(known_sources)
    if miss:
        return f"KILL (unknown source_id: {','.join(miss)})"
    for item in rows:
        if str(item.get("app_id", "")) not in AF0_APP_IDS:
            return f"KILL (bad app_id: {item.get('app_id')})"
        if not str(item.get("question", "")).strip():
            return f"KILL (empty question: {item.get('id')})"
        if not str(item.get("gold", "")).strip():
            return f"KILL (empty gold: {item.get('id')})"
        if not str(item.get("id", "")).startswith("AF-HITL-"):
            return f"KILL (bad trial id prefix: {item.get('id')})"
    if not trials_dir_ready:
        return "KILL (results/nano-lm/wave-af/trials/ not ready)"
    return f"PROMOTE ({AF0_ID}: {AF0_THESIS})"
