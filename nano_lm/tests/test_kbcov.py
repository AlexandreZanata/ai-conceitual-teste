"""Contract: Wave AQ4 H-KBCOV — coverage % + holes (pesquisa §5)."""

from __future__ import annotations

from kbcov_ops import (
    KBCOV_ID,
    KBCOV_THESIS,
    PRODUCT_HOLES,
    build_kbcov_snapshot,
    curated_blob_stats,
    decide_kbcov,
    parent_gold_hits,
)


def _snap_ok() -> dict:
    return build_kbcov_snapshot(
        curated_ids={"bip-0039", "rfc791"},
        bank_source_ids={"bip-0039", "extra-bank"},
    )


def _blobs_ok() -> dict:
    return curated_blob_stats(
        [
            {"source_id": "bip-0039", "exists": True},
            {"source_id": "rfc791", "exists": True},
        ]
    )


def _parents_ok() -> dict:
    return {
        "n": 2,
        "hit_n": 2,
        "miss_n": 0,
        "hit_pct": 100.0,
        "hit_ids": ["AQ-PARA-01", "AQ-PARA-02"],
        "miss_ids": [],
    }


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AQ4 — coverage % + holes · no fake 100%
    assert KBCOV_ID == "H-KBCOV"
    assert len(PRODUCT_HOLES) >= 1
    assert "fake" in KBCOV_THESIS or "complete" in KBCOV_THESIS


def test_given_partial_when_snap_then_pct_and_holes() -> None:
    snap = _snap_ok()
    assert snap["coverage_pct"] == 50.0
    assert "rfc791" in snap["missing_curated_in_bank"]
    assert snap["complete_claim_forbidden"] is True
    for hole in PRODUCT_HOLES:
        assert hole in snap["holes"]


def test_given_parents_when_gold_then_hit_miss() -> None:
    bank = [
        {
            "question": "Write a short Python function named add that returns "
            "the sum of two integers a and b.",
            "gold": "def add(a, b):\n    return a + b",
            "source_id": "python-tutorial-intro",
        }
    ]
    parents = [
        {
            "id": "AQ-PARA-01",
            "parent_question": bank[0]["question"],
        },
        {
            "id": "AQ-PARA-MISS",
            "parent_question": "totally unknown parent ask",
        },
    ]
    out = parent_gold_hits(parents, bank)
    assert out["hit_n"] == 1
    assert out["miss_ids"] == ["AQ-PARA-MISS"]
    assert out["hit_pct"] == 50.0


def test_given_blobs_when_missing_then_listed() -> None:
    st = curated_blob_stats(
        [
            {"source_id": "a", "exists": True},
            {"source_id": "b", "exists": False},
        ]
    )
    assert st["present_n"] == 1
    assert st["missing_ids"] == ["b"]


def test_given_honest_when_decide_then_promote() -> None:
    assert (
        decide_kbcov(snap=_snap_ok(), blobs=_blobs_ok(), parents=_parents_ok())
        == "PROMOTE"
    )


def test_given_empty_holes_when_decide_then_kill() -> None:
    snap = dict(_snap_ok())
    snap["holes"] = []
    out = decide_kbcov(snap=snap, blobs=_blobs_ok(), parents=_parents_ok())
    assert out.startswith("KILL")


def test_given_fake_complete_flag_when_decide_then_kill() -> None:
    snap = dict(_snap_ok())
    snap["complete_claim_forbidden"] = False
    out = decide_kbcov(snap=snap, blobs=_blobs_ok(), parents=_parents_ok())
    assert out.startswith("KILL")


def test_given_missing_blob_when_decide_then_kill() -> None:
    blobs = curated_blob_stats(
        [
            {"source_id": "bip-0039", "exists": True},
            {"source_id": "rfc791", "exists": False},
        ]
    )
    out = decide_kbcov(snap=_snap_ok(), blobs=blobs, parents=_parents_ok())
    assert out.startswith("KILL")
    assert "rfc791" in out


def test_given_registry_100_with_holes_when_decide_then_promote() -> None:
    snap = build_kbcov_snapshot(
        curated_ids={"a", "b"},
        bank_source_ids={"a", "b", "c"},
    )
    assert snap["coverage_pct"] == 100.0
    assert snap["complete_claim_forbidden"] is True
    assert decide_kbcov(snap=snap, blobs=_blobs_ok(), parents=_parents_ok()) == (
        "PROMOTE"
    )
