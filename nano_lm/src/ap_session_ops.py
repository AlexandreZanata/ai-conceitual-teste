"""Wave AP0 SESSION: freeze 10 held-out HITL asks (≠ AB…AO)."""

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
from am_session_ops import AM0_PACK
from an_session_ops import AN0_PACK
from ao_session_ops import AO0_PACK

__all__ = [
    "AP0_ID",
    "AP0_N",
    "AP0_PACK",
    "AP0_APP_IDS",
    "AP0_MIX",
    "AP0_THESIS",
    "missing_pack_source_ids",
    "pack_app_counts",
    "mix_ok",
    "unique_trial_ids",
    "overlaps_prior_questions",
    "decide_ap0_session",
]

AP0_ID = "AP0-SESSION"
AP0_N = 10
AP0_THESIS = (
    "Wave AP OPEN: freeze 10 held-out HITL asks "
    "(≠ AB · ≠ AC · ≠ AD · ≠ AE · ≠ AF · ≠ AG · ≠ AH · ≠ AI · ≠ AJ · "
    "≠ AK · ≠ AL · ≠ AM · ≠ AN · ≠ AO); next AP1 H-GENBASE"
)

AP0_APP_IDS: frozenset[str] = frozenset(
    {"known-ask", "howto", "long-doc"}
)

# Mix: 3 known · 5 howto · 2 long-doc (same app mix as AO0).
AP0_MIX: Mapping[str, int] = {
    "known-ask": 3,
    "howto": 5,
    "long-doc": 2,
}

# Frozen held-out phrasing (.local/wave-ap/SESSION.md). Same list AP1–AP5.
AP0_PACK: tuple[dict[str, str], ...] = (
    {
        "id": "AP-HITL-01",
        "app_id": "known-ask",
        "source_id": "bip-0039",
        "question": (
            "BIP-39: what is the formula for checksum length CS in terms "
            "of ENT? (write CS = …)"
        ),
        "gold": "CS = ENT / 32",
    },
    {
        "id": "AP-HITL-02",
        "app_id": "known-ask",
        "source_id": "bip-0032",
        "question": (
            "BIP-32 extended-key serialization: what parent fingerprint "
            "value is used for a master key (hex)?"
        ),
        "gold": "0x00000000",
    },
    {
        "id": "AP-HITL-03",
        "app_id": "known-ask",
        "source_id": "bip-0141",
        "question": (
            "BIP-141: a version-0 witness program of length L=20 is "
            "interpreted as which program type (acronym)?"
        ),
        "gold": "P2WPKH",
    },
    {
        "id": "AP-HITL-04",
        "app_id": "howto",
        "source_id": "python-tutorial-datastructures",
        "question": (
            "Add item `x` to the end of list `a` — one method call."
        ),
        "gold": "a.append(x)",
    },
    {
        "id": "AP-HITL-05",
        "app_id": "howto",
        "source_id": "python-tutorial-control",
        "question": (
            "Which keyword is a no-op placeholder statement in Python "
            "(Pass Statements)?"
        ),
        "gold": "pass",
    },
    {
        "id": "AP-HITL-06",
        "app_id": "howto",
        "source_id": "python-tutorial-classes",
        "question": (
            "Name the built-in that checks class inheritance "
            "(listed with isinstance tip)."
        ),
        "gold": "issubclass",
    },
    {
        "id": "AP-HITL-07",
        "app_id": "howto",
        "source_id": "rust-book-ch03-02",
        "question": (
            "From Rust's data-types chapter: which integer type pair is "
            "used primarily when indexing a collection? (write both names)"
        ),
        "gold": "isize or usize",
    },
    {
        "id": "AP-HITL-08",
        "app_id": "howto",
        "source_id": "rust-book-ch05-01",
        "question": (
            "Rust structs chapter: which two-character token starts the "
            "trailing field-copy from another instance (e.g. `..user1`)?"
        ),
        "gold": "..",
    },
    {
        "id": "AP-HITL-09",
        "app_id": "long-doc",
        "source_id": "bitcoin-rest",
        "question": (
            "Bitcoin Core REST: which GET path pattern returns a "
            "transaction by hash (include encoding suffixes)?"
        ),
        "gold": "GET /rest/tx/<TX-HASH>.<bin|hex|json>",
    },
    {
        "id": "AP-HITL-10",
        "app_id": "long-doc",
        "source_id": "rfc791",
        "question": (
            "RFC 791: how many bits is the Protocol field of the "
            "Internet header?"
        ),
        "gold": "8",
    },
)


def missing_pack_source_ids(known: set[str]) -> list[str]:
    """
    GIVEN curated source_ids
    WHEN checking AP0 pack provenance
    THEN return pack source_ids absent from the registry.
    """
    return sorted(
        {
            str(p["source_id"])
            for p in AP0_PACK
            if str(p["source_id"]) not in known
        }
    )


def pack_app_counts(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> dict[str, int]:
    """
    GIVEN AP0 pack
    WHEN counting app_id
    THEN return {app_id: count}.
    """
    rows = pack if pack is not None else AP0_PACK
    out: dict[str, int] = {}
    for item in rows:
        key = str(item["app_id"])
        out[key] = out.get(key, 0) + 1
    return out


def mix_ok(pack: Sequence[Mapping[str, str]] | None = None) -> bool:
    """
    GIVEN AP0 pack
    WHEN checking app mix
    THEN True iff counts match AP0_MIX and every app_id is known.
    """
    counts = pack_app_counts(pack)
    if set(counts) != set(AP0_MIX):
        return False
    return all(counts.get(k) == v for k, v in AP0_MIX.items())


def unique_trial_ids(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    """
    GIVEN AP0 pack
    WHEN checking trial ids
    THEN True iff N distinct non-empty ids.
    """
    rows = pack if pack is not None else AP0_PACK
    ids = [str(p.get("id", "")).strip() for p in rows]
    return len(ids) == AP0_N and all(ids) and len(set(ids)) == AP0_N


def overlaps_prior_questions(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> list[str]:
    """
    GIVEN AP0 pack + AB0…AO0 packs
    WHEN checking held-out rule
    THEN return AP ids whose question text equals a prior-wave question.
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
        | {str(p["question"]).strip() for p in AM0_PACK}
        | {str(p["question"]).strip() for p in AN0_PACK}
        | {str(p["question"]).strip() for p in AO0_PACK}
    )
    rows = pack if pack is not None else AP0_PACK
    return [
        str(p["id"])
        for p in rows
        if str(p.get("question", "")).strip() in prior
    ]


def decide_ap0_session(
    *,
    known_sources: set[str],
    trials_dir_ready: bool,
    pack: Sequence[Mapping[str, str]] | None = None,
) -> str:
    """
    GIVEN curated registry + trials dir flag + pack
    WHEN applying AP0 SESSION gate
    THEN PROMOTE iff N=10, unique ids, mix, sources, ≠AB…AO Qs, trials ready.
    """
    rows = list(pack) if pack is not None else list(AP0_PACK)
    if len(rows) != AP0_N:
        return f"KILL (pack size {len(rows)} != {AP0_N})"
    if not unique_trial_ids(rows):
        return "KILL (trial ids missing or duplicated)"
    if not mix_ok(rows):
        return f"KILL (app mix {pack_app_counts(rows)} != {dict(AP0_MIX)})"
    clash = overlaps_prior_questions(rows)
    if clash:
        return (
            "KILL (verbatim AB…AO questions: "
            f"{','.join(clash)})"
        )
    miss = missing_pack_source_ids(known_sources)
    if miss:
        return f"KILL (unknown source_id: {','.join(miss)})"
    for item in rows:
        if str(item.get("app_id", "")) not in AP0_APP_IDS:
            return f"KILL (bad app_id: {item.get('app_id')})"
        if not str(item.get("question", "")).strip():
            return f"KILL (empty question: {item.get('id')})"
        if not str(item.get("gold", "")).strip():
            return f"KILL (empty gold: {item.get('id')})"
        if not str(item.get("id", "")).startswith("AP-HITL-"):
            return f"KILL (bad trial id prefix: {item.get('id')})"
    if not trials_dir_ready:
        return "KILL (results/nano-lm/wave-ap/trials/ not ready)"
    return f"PROMOTE ({AP0_ID}: {AP0_THESIS})"
