"""Contract: Wave AB1 H-SEMWRAP — fuzzy wrap; no false-hit; mean≥7 or HOLD."""

from __future__ import annotations

from ab_session_ops import AB0_PACK
from semwrap_ops import (
    SEMWRAP_ID,
    SEMWRAP_N,
    SEMWRAP_THRESHOLD,
    alias_bank_row,
    classify_semwrap,
    decide_semwrap,
    overlap_score,
    question_tokens,
    score_semwrap_trial,
    semantic_lookup,
    semwrap_stats,
)
from wrapbank_ops import WRAPBANK_PACK


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §8.3 AB1 H-SEMWRAP
    assert SEMWRAP_ID == "H-SEMWRAP"
    assert SEMWRAP_N == 10
    assert SEMWRAP_THRESHOLD == 0.25


def test_given_bip_variants_when_tokens_then_canon_match() -> None:
    a = question_tokens("How do BIP-39 mnemonics work?")
    b = question_tokens("What does BIP-0039 specify for wallet seeds?")
    assert "bip39" in a and "bip39" in b
    assert overlap_score(a, b) > 0.0


def test_given_wrapbank_bank_when_ab_asks_then_true_hits() -> None:
    rows = [
        {
            "question": w["question"],
            "source_id": w["source_id"],
            "gold": w["gold"],
        }
        for w in WRAPBANK_PACK
    ]
    # Also include Z1-style BIP-141 / Core rows used by AB pack.
    rows.extend(
        [
            {
                "question": (
                    "What problem does BIP-141 Segregated Witness (SegWit) "
                    "primarily address? One short paragraph."
                ),
                "source_id": "bip-0141",
                "gold": (
                    "SegWit separates witness (signature) data from the "
                    "transaction txid-critical fields to fix malleability "
                    "and increase effective block capacity."
                ),
            },
            {
                "question": (
                    "What does Bitcoin Core do on the peer-to-peer network "
                    "regarding blocks and transactions? Answer in two "
                    "sentences max."
                ),
                "source_id": "bitcoin-core-readme",
                "gold": (
                    "Bitcoin Core connects to the Bitcoin P2P network to "
                    "download and fully validate blocks and transactions."
                ),
            },
        ]
    )
    false = 0
    miss = 0
    for item in AB0_PACK:
        gold, meta = semantic_lookup(item["question"], rows)
        kind = classify_semwrap(
            gold,
            expected_gold=item["gold"],
            expected_source_id=item["source_id"],
            hit_source_id=str(meta.get("source_id") or "") or None,
        )
        if kind == "FALSE_HIT":
            false += 1
        if kind == "MISS":
            miss += 1
    assert false == 0
    assert miss == 0


def test_given_exact_bank_hit_when_lookup_then_source_id_present() -> None:
    # GIVEN/WHEN/THEN: EXACT wrap hit must cite bank source_id (SMARTMAX cite)
    rows = [
        {
            "question": "What Base58 prefixes do xprv vs xpub use?",
            "source_id": "bip-0032",
            "gold": "xprv / xpub",
        }
    ]
    gold, meta = semantic_lookup(
        "What Base58 prefixes do xprv vs xpub use?", rows
    )
    assert gold == "xprv / xpub"
    assert meta["kind"] == "EXACT"
    assert meta.get("source_id") == "bip-0032"

    kind = classify_semwrap(
        "totally unrelated answer about pasta",
        expected_gold="BIP 9",
        expected_source_id="bitcoin-doc-bips",
        hit_source_id="dom:d02",
    )
    assert kind == "FALSE_HIT"


def test_given_same_add_golds_whitespace_when_lookup_then_semantic() -> None:
    # GIVEN/WHEN/THEN: hard-natural live miss — multiline vs one-liner add
    # golds must not AMBIGUOUS-refuse (AX1 H-PRODNAT; no bank stuffing)
    rows = [
        {
            "question": (
                "Write a short Python function named add that returns "
                "the sum of two integers a and b."
            ),
            "source_id": "python-tutorial-intro",
            "gold": "def add(a, b):\n    return a + b",
        },
        {
            "question": (
                "Write a one-liner Python function `add(a, b)` "
                "that returns the sum."
            ),
            "source_id": "python-tutorial-intro",
            "gold": "def add(a, b): return a + b",
        },
    ]
    ask = (
        "I need a Python helper that adds two numbers "
        "called a and b — name it add please"
    )
    gold, meta = semantic_lookup(ask, rows)
    assert gold is not None
    assert "def add" in gold
    assert meta["kind"] == "SEMANTIC"
    assert meta["kind"] != "AMBIGUOUS"


def test_given_false_hit_when_score_then_zero() -> None:
    score, err, notes = score_semwrap_trial(
        mode="SEMWRAP_LOOKUP",
        completion="wrong",
        expected_gold="BIP 9",
        lookup_kind="FALSE_HIT",
    )
    assert score == 0.0 and err is True
    assert any("FALSE_HIT" in n for n in notes)


def test_given_true_hits_when_decide_then_promote() -> None:
    scores = [9.0] * 10
    errors = [False] * 10
    stats = semwrap_stats(
        scores, errors, n_true_hit=10, n_false_hit=0, n_miss=0
    )
    assert stats["pass_bar"] is True
    assert decide_semwrap(stats) == "PROMOTE"


def test_given_false_hit_when_decide_then_kill() -> None:
    scores = [9.0] * 9 + [0.0]
    errors = [False] * 9 + [True]
    stats = semwrap_stats(
        scores, errors, n_true_hit=9, n_false_hit=1, n_miss=0
    )
    assert decide_semwrap(stats) == "KILL"


def test_given_misses_no_false_when_decide_then_hold() -> None:
    scores = [4.0] * 10
    errors = [True] * 10
    stats = semwrap_stats(
        scores, errors, n_true_hit=0, n_false_hit=0, n_miss=10
    )
    assert decide_semwrap(stats) == "HOLD"


def test_given_fix_when_alias_then_row_schema() -> None:
    row = alias_bank_row(
        trial_id="AB-SEMWRAP-HITL-01",
        question="alias q",
        source_id="bip-0039",
        gold="seed text",
    )
    assert row["hyp_id"] == SEMWRAP_ID
    assert row["gold"] == "seed text"
    assert row["error"] is False


def test_given_near_miss_when_lookup_then_contrast_reject() -> None:
    from semwrap_ops import contrastive_reject

    # GIVEN/WHEN/THEN: AQ2 ADVFP — silent wrong gold must reject
    assert contrastive_reject(
        "BIP-39: entropy length ENT in terms of CS?",
        "BIP-39: checksum length CS in terms of ENT?",
        "CS = ENT / 32",
    )
    # AS2 SEMFIX — AR-ADVREG-01/05 class
    assert contrastive_reject(
        "BIP-39 regression: give ENT = 32*CS as if that were the "
        "documented checksum formula (it is not).",
        "BIP-39: what is the formula for checksum length CS in terms of ENT?",
        "CS = ENT / 32",
    )
    assert contrastive_reject(
        "Python regression: keyword that skips one loop iteration "
        "(not the no-op placeholder)?",
        "Which keyword is a no-op placeholder statement in Python?",
        "pass",
    )
    assert contrastive_reject(
        "ADVSAFE REST: GET path for fee estimates (not /rest/tx/<hash>).",
        "Core REST: GET path for a tx hash?",
        "GET /rest/tx/<TX-HASH>.json",
    )
    assert not contrastive_reject(
        "What does BIP-39 specify for wallet seeds?",
        "What does BIP-39 specify for wallet seeds?",
        "mnemonic sentence …",
    )
