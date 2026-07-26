"""Wave AA1 H-PARA: paraphrase Z1 asks; wrap must not false-hit."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN
from z_wrap import normalize_question

__all__ = [
    "PARA_ID",
    "PARA_N",
    "PARA_PACK",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "paraphrase_collides_bank",
    "classify_lookup",
    "score_para_trial",
    "para_stats",
    "decide_para",
]

PARA_ID = "H-PARA"
PARA_N = 10

# Paraphrases of Z1-01..Z1-10 (normalize key ≠ parent; same gold target).
PARA_PACK: tuple[dict[str, str], ...] = (
    {
        "parent_question": (
            "Write a short Python function named add that returns the sum of two integers a and b."
        ),
        "paraphrase": (
            "Please write a tiny Python helper called add which adds integers a and b and returns the result."
        ),
        "source_id": "python-tutorial-intro",
        "parent_gold": "def add(a, b):\n    return a + b",
    },
    {
        "parent_question": (
            "In Python, to create a list of squares you can write squares = [x**2 for x in"
        ),
        "paraphrase": (
            "Complete this Python list comprehension that builds squares: squares = [x**2 for x in"
        ),
        "source_id": "prog:g01",
        "parent_gold": "range(10)]",
    },
    {
        "parent_question": (
            "Explain briefly how a Python for-loop over range(3) works, and show a one-line example that prints each value."
        ),
        "paraphrase": (
            "In a few words, what does for i in range(3) iterate, and give one print example?"
        ),
        "source_id": "python-tutorial-control",
        "parent_gold": (
            "range(3) yields 0,1,2. Example: for i in range(3): print(i)"
        ),
    },
    {
        "parent_question": (
            "In Rust, variables are immutable by default; how do you declare a mutable integer x starting at 5? Show one line."
        ),
        "paraphrase": (
            "Rust: show the one-liner that makes integer x mutable and equal to 5."
        ),
        "source_id": "rust-book-ch03",
        "parent_gold": "let mut x = 5;",
    },
    {
        "parent_question": "What is a BIP in Bitcoin? Answer in one or two sentences.",
        "paraphrase": (
            "Define BIP as used in Bitcoin Core docs, briefly (1–2 sentences)."
        ),
        "source_id": "bip-0001",
        "parent_gold": (
            "A BIP (Bitcoin Improvement Proposal) is a design document that informs "
            "the Bitcoin community or describes a new feature for Bitcoin."
        ),
    },
    {
        "parent_question": (
            "In BIP-0032 hierarchical deterministic wallets, hardened child keys use which index range? Answer briefly."
        ),
        "paraphrase": (
            "BIP-32 HD wallets: which child-key index range is reserved for hardened keys?"
        ),
        "source_id": "bip-0032",
        "parent_gold": "Hardened keys use indices >= 2^31 (0x80000000).",
    },
    {
        "parent_question": (
            "What problem does BIP-141 Segregated Witness (SegWit) primarily address? One short paragraph."
        ),
        "paraphrase": (
            "Why was BIP-141 SegWit introduced — what core problem does it mainly fix?"
        ),
        "source_id": "bip-0141",
        "parent_gold": (
            "SegWit separates witness (signature) data from the transaction "
            "txid-critical fields to fix malleability and increase effective block capacity."
        ),
    },
    {
        "parent_question": (
            "Write a minimal Python class Point with __init__(self, x, y) storing x and y on the instance."
        ),
        "paraphrase": (
            "Give a minimal Python Point class whose constructor stores coordinates x and y."
        ),
        "source_id": "python-tutorial-classes",
        "parent_gold": (
            "class Point:\n    def __init__(self, x, y):\n        self.x = x\n        self.y = y"
        ),
    },
    {
        "parent_question": "Before boiling pasta, fill a pot with water and bring it to a",
        "paraphrase": "To cook pasta, first fill a pot and heat the water until it reaches a",
        "source_id": "dom:d02",
        "parent_gold": "boil (rolling boil), then add salt and pasta.",
    },
    {
        "parent_question": (
            "What does Bitcoin Core do on the peer-to-peer network regarding blocks and transactions? Answer in two sentences max."
        ),
        "paraphrase": (
            "Summarize Bitcoin Core's P2P role for blocks/txs in at most two sentences."
        ),
        "source_id": "bitcoin-core-readme",
        "parent_gold": (
            "Bitcoin Core connects to the Bitcoin P2P network to download and fully "
            "validate blocks and transactions. It also relays them to peers and can "
            "serve a wallet and RPC interface."
        ),
    },
)


def paraphrase_collides_bank(
    pack: Sequence[Mapping[str, str]],
    rows: Sequence[Mapping[str, Any]],
) -> list[str]:
    """
    GIVEN PARA pack + bank rows
    WHEN checking normalize keys
    THEN return paraphrases that collide with any bank question key.
    """
    keys = {normalize_question(str(r.get("question", ""))) for r in rows}
    bad: list[str] = []
    for item in pack:
        if normalize_question(str(item["paraphrase"])) in keys:
            bad.append(str(item["paraphrase"]))
    return bad


def classify_lookup(looked_up: str | None, parent_gold: str) -> str:
    """
    GIVEN wrap lookup result + parent gold
    WHEN classifying paraphrase stress
    THEN TRUE_HIT | FALSE_HIT | MISS.
    """
    if looked_up is None:
        return "MISS"
    if str(looked_up).strip() == str(parent_gold).strip():
        return "TRUE_HIT"
    return "FALSE_HIT"


def score_para_trial(
    *,
    mode: str,
    completion: str,
    parent_gold: str,
    lookup_kind: str,
) -> tuple[float, bool, list[str]]:
    """
    GIVEN wrap ask on a paraphrase
    WHEN scoring HITL
    THEN FALSE_HIT→0; TRUE_HIT→9; MISS uses decode quality vs parent gold.
    """
    if lookup_kind == "FALSE_HIT":
        return (
            0.0,
            True,
            [
                "FALSE_HIT: wrap returned a bank gold that is not the parent gold",
                "lookup brittleness / collision — product bug for known-ask claims",
                "in-scope; mark error",
            ],
        )
    text = str(completion).strip()
    g = str(parent_gold).strip()
    if lookup_kind == "TRUE_HIT" and text == g:
        return (
            9.0,
            False,
            [
                "TRUE_HIT: paraphrase matched parent bank gold via WRAP_LOOKUP",
                "correct vs parent gold",
                "harm/scope ok",
            ],
        )
    if set(text) <= {".", " "} or text in {"", "........"}:
        return (
            1.0,
            True,
            [
                "MISS: no WRAP_LOOKUP; decode collapsed to periods",
                "documents exact-match wrap brittleness under paraphrase",
                "in-scope; not a false-hit",
            ],
        )
    if text == g:
        return (
            9.0,
            False,
            [
                f"MISS path but completion matched parent gold (mode={mode})",
                "correct enough vs parent",
                "harm/scope ok",
            ],
        )
    return (
        4.0,
        True,
        [
            f"MISS: mode={mode}; completion ≠ parent gold",
            "partial/wrong open decode under paraphrase stress",
            "documents wrap lookup brittleness (no false-hit)",
        ],
    )


def para_stats(
    scores: Sequence[float],
    errors: Sequence[bool],
    *,
    n_true_hit: int,
    n_false_hit: int,
    n_miss: int,
) -> dict[str, Any]:
    """
    GIVEN 10 PARA scores + hit breakdown
    WHEN summarizing H-PARA
    THEN return mean, pass_bar, and false-hit counts.
    """
    if len(scores) != PARA_N or len(errors) != PARA_N:
        raise ValueError(f"PARA requires exactly {PARA_N} scores/errors")
    mean = float(sum(scores) / float(PARA_N))
    n_err = int(sum(1 for e in errors if e))
    return {
        "n_trials": PARA_N,
        "mean": mean,
        "n_errors": n_err,
        "n_true_hit": int(n_true_hit),
        "n_false_hit": int(n_false_hit),
        "n_miss": int(n_miss),
        "pass_bar": mean >= PASS_MEAN and n_err <= PASS_MAX_ERRORS,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
    }


def decide_para(stats: Mapping[str, Any]) -> str:
    """
    GIVEN PARA stats
    WHEN applying §8.1 gate
    THEN PROMOTE if pass_bar & no false-hit;
         HOLD if no false-hit (document brittleness);
         KILL if any false-hit.
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    if bool(stats.get("pass_bar")):
        return "PROMOTE"
    return "HOLD"
