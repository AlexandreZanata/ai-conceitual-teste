"""Wave AH0 SESSION: freeze 10 held-out HITL asks (≠ AB…AG)."""

from __future__ import annotations

from typing import Mapping, Sequence

from ab_session_ops import AB0_PACK
from ac_session_ops import AC0_PACK
from ad_session_ops import AD0_PACK
from ae_session_ops import AE0_PACK
from af_session_ops import AF0_PACK
from ag_session_ops import AG0_PACK

__all__ = [
    "AH0_ID",
    "AH0_N",
    "AH0_PACK",
    "AH0_APP_IDS",
    "AH0_MIX",
    "AH0_THESIS",
    "missing_pack_source_ids",
    "pack_app_counts",
    "mix_ok",
    "unique_trial_ids",
    "overlaps_prior_questions",
    "decide_ah0_session",
]

AH0_ID = "AH0-SESSION"
AH0_N = 10
AH0_THESIS = (
    "Wave AH OPEN: freeze 10 held-out HITL asks "
    "(≠ AB · ≠ AC · ≠ AD · ≠ AE · ≠ AF · ≠ AG); next AH1 H-GENLIFT"
)

AH0_APP_IDS: frozenset[str] = frozenset(
    {"known-ask", "howto", "long-doc"}
)

# Mix from .local/wave-ah/SESSION.md: 3 known · 5 howto · 2 long-doc.
AH0_MIX: Mapping[str, int] = {
    "known-ask": 3,
    "howto": 5,
    "long-doc": 2,
}

# Frozen held-out phrasing (.local/wave-ah/SESSION.md). Same list AH1–AH5.
AH0_PACK: tuple[dict[str, str], ...] = (
    {
        "id": "AH-HITL-01",
        "app_id": "known-ask",
        "source_id": "bip-0039",
        "question": (
            "BIP-39 mnemonic→seed with an empty passphrase: what UTF-8 "
            "salt string is used?"
        ),
        "gold": (
            'The salt is the literal string "mnemonic" '
            "(plus the empty passphrase)."
        ),
    },
    {
        "id": "AH-HITL-02",
        "app_id": "known-ask",
        "source_id": "bip-0340",
        "question": (
            "BIP-340 key prefixing protects against which attack class "
            "on additive key tweaks? One short phrase."
        ),
        "gold": (
            "Related-key attacks (additive tweaks / unhardened BIP32 "
            "derivation)."
        ),
    },
    {
        "id": "AH-HITL-03",
        "app_id": "known-ask",
        "source_id": "rust-book-ch03-02",
        "question": (
            "List Rust's four primary scalar types from the data-types "
            "chapter."
        ),
        "gold": (
            "integers, floating-point numbers, Booleans, and characters"
        ),
    },
    {
        "id": "AH-HITL-04",
        "app_id": "howto",
        "source_id": "python-tutorial-datastructures",
        "question": (
            "Remove and return the last item of list `a` — one method call."
        ),
        "gold": "a.pop()",
    },
    {
        "id": "AH-HITL-05",
        "app_id": "howto",
        "source_id": "python-tutorial-control",
        "question": (
            "Inside a Python function that is not ready yet, what single "
            "statement is a valid empty body?"
        ),
        "gold": "pass",
    },
    {
        "id": "AH-HITL-06",
        "app_id": "howto",
        "source_id": "python-tutorial-classes",
        "question": (
            "Inside an instance method, what does the first parameter "
            "conventionally named `self` refer to?"
        ),
        "gold": "The instance on which the method was invoked.",
    },
    {
        "id": "AH-HITL-07",
        "app_id": "howto",
        "source_id": "rust-book-ch04-01",
        "question": (
            "From the Rust ownership chapter: where must data of unknown "
            "size at compile time be stored?"
        ),
        "gold": "On the heap.",
    },
    {
        "id": "AH-HITL-08",
        "app_id": "howto",
        "source_id": "rust-book-ch05-01",
        "question": (
            "Name the Rust syntax that fills remaining struct fields from "
            "another instance (`..other`)."
        ),
        "gold": "struct update syntax",
    },
    {
        "id": "AH-HITL-09",
        "app_id": "long-doc",
        "source_id": "bitcoin-rest",
        "question": (
            "What default mainnet TCP port does Bitcoin Core's REST "
            "interface share with JSON-RPC?"
        ),
        "gold": "8332",
    },
    {
        "id": "AH-HITL-10",
        "app_id": "long-doc",
        "source_id": "rfc8949",
        "question": (
            "RFC 8949 expands CBOR — which prior RFC number does it "
            "obsolete?"
        ),
        "gold": "7049",
    },
)


def missing_pack_source_ids(known: set[str]) -> list[str]:
    """
    GIVEN curated source_ids
    WHEN checking AH0 pack provenance
    THEN return pack source_ids absent from the registry.
    """
    return sorted(
        {
            str(p["source_id"])
            for p in AH0_PACK
            if str(p["source_id"]) not in known
        }
    )


def pack_app_counts(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> dict[str, int]:
    """
    GIVEN AH0 pack
    WHEN counting app_id
    THEN return {app_id: count}.
    """
    rows = pack if pack is not None else AH0_PACK
    out: dict[str, int] = {}
    for item in rows:
        key = str(item["app_id"])
        out[key] = out.get(key, 0) + 1
    return out


def mix_ok(pack: Sequence[Mapping[str, str]] | None = None) -> bool:
    """
    GIVEN AH0 pack
    WHEN checking app mix
    THEN True iff counts match AH0_MIX and every app_id is known.
    """
    counts = pack_app_counts(pack)
    if set(counts) != set(AH0_MIX):
        return False
    return all(counts.get(k) == v for k, v in AH0_MIX.items())


def unique_trial_ids(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    """
    GIVEN AH0 pack
    WHEN checking trial ids
    THEN True iff N distinct non-empty ids.
    """
    rows = pack if pack is not None else AH0_PACK
    ids = [str(p.get("id", "")).strip() for p in rows]
    return len(ids) == AH0_N and all(ids) and len(set(ids)) == AH0_N


def overlaps_prior_questions(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> list[str]:
    """
    GIVEN AH0 pack + AB0…AG0 packs
    WHEN checking held-out rule
    THEN return AH ids whose question text equals a prior-wave question.
    """
    prior = (
        {str(p["question"]).strip() for p in AB0_PACK}
        | {str(p["question"]).strip() for p in AC0_PACK}
        | {str(p["question"]).strip() for p in AD0_PACK}
        | {str(p["question"]).strip() for p in AE0_PACK}
        | {str(p["question"]).strip() for p in AF0_PACK}
        | {str(p["question"]).strip() for p in AG0_PACK}
    )
    rows = pack if pack is not None else AH0_PACK
    return [
        str(p["id"])
        for p in rows
        if str(p.get("question", "")).strip() in prior
    ]


def decide_ah0_session(
    *,
    known_sources: set[str],
    trials_dir_ready: bool,
    pack: Sequence[Mapping[str, str]] | None = None,
) -> str:
    """
    GIVEN curated registry + trials dir flag + pack
    WHEN applying AH0 SESSION gate
    THEN PROMOTE iff N=10, unique ids, mix, sources, ≠AB…AG Qs, trials ready.
    """
    rows = list(pack) if pack is not None else list(AH0_PACK)
    if len(rows) != AH0_N:
        return f"KILL (pack size {len(rows)} != {AH0_N})"
    if not unique_trial_ids(rows):
        return "KILL (trial ids missing or duplicated)"
    if not mix_ok(rows):
        return f"KILL (app mix {pack_app_counts(rows)} != {dict(AH0_MIX)})"
    clash = overlaps_prior_questions(rows)
    if clash:
        return (
            "KILL (verbatim AB/AC/AD/AE/AF/AG questions: "
            f"{','.join(clash)})"
        )
    miss = missing_pack_source_ids(known_sources)
    if miss:
        return f"KILL (unknown source_id: {','.join(miss)})"
    for item in rows:
        if str(item.get("app_id", "")) not in AH0_APP_IDS:
            return f"KILL (bad app_id: {item.get('app_id')})"
        if not str(item.get("question", "")).strip():
            return f"KILL (empty question: {item.get('id')})"
        if not str(item.get("gold", "")).strip():
            return f"KILL (empty gold: {item.get('id')})"
        if not str(item.get("id", "")).startswith("AH-HITL-"):
            return f"KILL (bad trial id prefix: {item.get('id')})"
    if not trials_dir_ready:
        return "KILL (results/nano-lm/wave-ah/trials/ not ready)"
    return f"PROMOTE ({AH0_ID}: {AH0_THESIS})"
