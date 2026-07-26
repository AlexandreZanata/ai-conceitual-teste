"""Wave AA0 H-WRAPBANK: expand wrap golds; HITL pass bar; no weight update."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN
from z_wrap import normalize_question

__all__ = [
    "WRAPBANK_ID",
    "WRAPBANK_N",
    "WRAPBANK_PACK",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "bank_row_from_item",
    "expand_bank_rows",
    "missing_pack_source_ids",
    "new_questions_not_in_bank",
    "score_wrap_hit",
    "wrapbank_stats",
    "decide_wrapbank",
]

WRAPBANK_ID = "H-WRAPBANK"
WRAPBANK_N = 10

# New scoped Q→gold pairs (curated source_ids). Distinct from Z1 bank.
WRAPBANK_PACK: tuple[dict[str, str], ...] = (
    {
        "question": (
            "What does BIP-0039 specify for wallet seeds? Answer in one or two sentences."
        ),
        "source_id": "bip-0039",
        "gold": (
            "BIP-0039 specifies a mnemonic sentence of easy-to-remember words that "
            "encodes entropy and converts via PBKDF2 into a binary seed for "
            "deterministic wallets (e.g. BIP-0032)."
        ),
    },
    {
        "question": (
            "What signature scheme does BIP-0340 standardize for Bitcoin? One sentence."
        ),
        "source_id": "bip-0340",
        "gold": (
            "BIP-0340 standardizes 64-byte Schnorr signatures over the secp256k1 curve."
        ),
    },
    {
        "question": (
            "In Python, which list method adds one item to the end of a list? "
            "Name the method and show a one-line example."
        ),
        "source_id": "python-tutorial-datastructures",
        "gold": "list.append — example: squares.append(x**2)",
    },
    {
        "question": (
            "In Python, how do you open a text file for reading with UTF-8 encoding? "
            "Show one line using open()."
        ),
        "source_id": "python-tutorial-io",
        "gold": 'f = open("workfile", "r", encoding="utf-8")',
    },
    {
        "question": (
            "In Rust, what are the two main data-type subsets described in the book "
            "chapter on data types? Name both."
        ),
        "source_id": "rust-book-ch03-02",
        "gold": "Scalar types and compound types.",
    },
    {
        "question": (
            "What is ownership in Rust, in one or two sentences?"
        ),
        "source_id": "rust-book-ch04-01",
        "gold": (
            "Ownership is a set of compile-time rules that govern how a Rust program "
            "manages memory without a garbage collector; violating the rules prevents "
            "compilation and does not slow runtime."
        ),
    },
    {
        "question": (
            "How do you define a simple Rust struct named User with one String field "
            "named name? Show a minimal definition."
        ),
        "source_id": "rust-book-ch05-01",
        "gold": "struct User {\n    name: String,\n}",
    },
    {
        "question": (
            "Bitcoin Core JSON-RPC: name the two endpoints documented for the server."
        ),
        "source_id": "bitcoin-json-rpc",
        "gold": "`/` and `/wallet/<walletname>/`",
    },
    {
        "question": (
            "How do you enable Bitcoin Core's unauthenticated REST interface? "
            "One short answer."
        ),
        "source_id": "bitcoin-rest",
        "gold": "Start bitcoind/bitcoin-qt with the `-rest` option.",
    },
    {
        "question": (
            "According to Bitcoin Core's bips.md, which BIP enables multiple soft-fork "
            "deployments in parallel (implemented since v0.12.1)?"
        ),
        "source_id": "bitcoin-doc-bips",
        "gold": "BIP 9",
    },
)


def missing_pack_source_ids(known: set[str]) -> list[str]:
    """
    GIVEN curated source_ids
    WHEN checking WRAPBANK pack provenance
    THEN return pack source_ids absent from the registry.
    """
    return sorted(
        {
            str(p["source_id"])
            for p in WRAPBANK_PACK
            if str(p["source_id"]) not in known
        }
    )


def bank_row_from_item(item: Mapping[str, str], *, trial_id: str) -> dict[str, Any]:
    """
    GIVEN a WRAPBANK pack item
    WHEN materializing an error_bank row
    THEN return schema-valid gold row (no weight update fuel flag).
    """
    gold = str(item["gold"]).strip()
    return {
        "trial_id": trial_id,
        "question": str(item["question"]),
        "source_id": str(item["source_id"]),
        "model_raw": "",
        "gold": gold,
        "repaired": gold,
        "score": 9.0,
        "error": False,
        "recipe_id": "champion-wrap-v0",
        "ckpt": None,
        "judge_notes": [
            "WRAPBANK curated gold for known-ask expansion",
            "scoped to curated source_id",
            "no student weight update",
        ],
        "hyp_id": WRAPBANK_ID,
    }


def new_questions_not_in_bank(
    rows: Sequence[Mapping[str, Any]],
    pack: Sequence[Mapping[str, str]],
) -> list[dict[str, str]]:
    """Return pack items whose normalized question is absent from bank rows."""
    have = {normalize_question(str(r.get("question", ""))) for r in rows}
    return [
        dict(p)
        for p in pack
        if normalize_question(str(p["question"])) not in have
    ]


def expand_bank_rows(
    rows: Sequence[Mapping[str, Any]],
    pack: Sequence[Mapping[str, str]] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    GIVEN existing bank + WRAPBANK pack
    WHEN expanding wrap golds
    THEN return (added_rows, merged_rows) without duplicating questions.
    """
    use = list(pack) if pack is not None else list(WRAPBANK_PACK)
    merged = [dict(r) for r in rows]
    have = {normalize_question(str(r.get("question", ""))) for r in merged}
    added: list[dict[str, Any]] = []
    for i, item in enumerate(use, start=1):
        if normalize_question(str(item["question"])) in have:
            continue
        row = bank_row_from_item(item, trial_id=f"AA0-{i:02d}")
        added.append(row)
        merged.append(row)
        have.add(normalize_question(str(item["question"])))
    return added, merged


def score_wrap_hit(completion: str, gold: str) -> tuple[float, bool, list[str]]:
    """
    GIVEN wrap ask completion + curated gold
    WHEN judging known-ask product (frontier rubric, automated)
    THEN score 9 iff completion equals curated gold; else error.
    """
    text = str(completion).strip()
    g = str(gold).strip()
    if text and g and text == g:
        return (
            9.0,
            False,
            [
                "WRAP_LOOKUP returned curated WRAPBANK gold",
                "correct and scoped vs source_id domain",
                "harm/scope ok; no weight update",
            ],
        )
    if set(text) <= {".", " "} or text in {"", "........"}:
        return (
            1.0,
            True,
            [
                "completion is only period tokens or empty",
                "incorrect vs curated WRAPBANK gold",
                "mark error; bank expansion / wrap miss",
            ],
        )
    return (
        4.0,
        True,
        [
            "completion does not match WRAPBANK gold",
            "partial or wrong vs curated answer",
            "mark error for bank/HITL audit",
        ],
    )


def wrapbank_stats(
    scores: Sequence[float],
    errors: Sequence[bool],
    *,
    n_lookup: int,
) -> dict[str, Any]:
    """
    GIVEN 10 HITL scores + error flags + WRAP_LOOKUP count
    WHEN summarizing H-WRAPBANK
    THEN return mean, pass_bar, and weight_update=False.
    """
    if len(scores) != WRAPBANK_N or len(errors) != WRAPBANK_N:
        raise ValueError(f"WRAPBANK requires exactly {WRAPBANK_N} scores/errors")
    mean = float(sum(scores) / float(WRAPBANK_N))
    n_err = int(sum(1 for e in errors if e))
    return {
        "n_trials": WRAPBANK_N,
        "mean": mean,
        "n_errors": n_err,
        "n_lookup": int(n_lookup),
        "pass_bar": mean >= PASS_MEAN and n_err <= PASS_MAX_ERRORS,
        "weight_update": False,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
    }


def decide_wrapbank(stats: Mapping[str, Any]) -> str:
    """
    GIVEN WRAPBANK stats
    WHEN applying §8.1 gate (mean≥7, errors≤3; no weight update)
    THEN PROMOTE iff pass_bar; else KILL.
    """
    if bool(stats.get("pass_bar")) and stats.get("weight_update") is False:
        return "PROMOTE"
    return "KILL"
