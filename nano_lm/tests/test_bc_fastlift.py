"""Contract: Wave BC2 H-FASTLIFT — prod p50/p99 hold · anti-FP (≠ AH FASTLIFT)."""

from __future__ import annotations

from bc_fastlift_ops import (
    FASTLIFT_ANTI_FP,
    FASTLIFT_BASELINE,
    FASTLIFT_CLAIM,
    FASTLIFT_ID,
    FASTLIFT_THESIS,
    P99_REGRESS_MAX_RATIO,
    P99_REGRESS_MIN_BASE_MS,
    decide_fastlift,
    extract_fastlift_board,
    p99_regressed,
)
from bc_session_ops import BC0_MODES


def _board(**overrides: object) -> dict:
    base = {
        "latency": {
            "LOOKUP": {"p50_wall_ms": 0.0, "p99_wall_ms": 0.0, "n": 64},
            "PEAK": {"p50_wall_ms": 0.01, "p99_wall_ms": 0.02, "n": 128},
            "DECODE": {"p50_wall_ms": 11.0, "p99_wall_ms": 12.0, "n": 12},
            "ABSTAIN": {"p50_wall_ms": 95.0, "p99_wall_ms": 110.0, "n": 32},
        },
        "bc_forever_false_hit": 0,
        "bc_forever_ok_n": 18,
        "bc_forever_n": 18,
        "bb_forever_false_hit": 0,
        "bb_forever_ok_n": 15,
        "bb_forever_n": 15,
        "ba_forever_false_hit": 0,
        "ba_forever_ok_n": 15,
        "ba_forever_n": 15,
        "az_hold_false_hit": 0,
        "az_hold_ok_n": 12,
        "az_hold_n": 12,
        "overrefuse_miss": 0,
        "overrefuse_ok_n": 3,
        "overrefuse_n": 3,
        "live_fp": 0,
        "near_miss_ok": True,
        "known_lookup_ok": True,
        "decode_content_ok": True,
        "modes_visible": sorted(BC0_MODES),
        "modes_n": 4,
        "telemetry_ok": {m: True for m in BC0_MODES},
        "p99_regress_paths": [],
        "p99_regress": False,
        "p99_regress_max_ratio": P99_REGRESS_MAX_RATIO,
        "baseline_source": "H-FASTHOLD",
        "lookup_wall_neq_speed_iq": True,
        "warm_cache_vanity_forbidden": True,
        "bank_stuff_forbidden": True,
        "ba_bb_pass_neq_bc_forever": True,
        "bb_fasthold_archive_untouched": True,
        "ba_fastreal_archive_untouched": True,
        "ah_fastlift_archive_untouched": True,
        "fp_for_ms_forbidden": True,
    }
    base.update(overrides)
    return base


def test_given_id_when_read_then_h_fastlift_not_ah_archive_clone() -> None:
    # GIVEN/WHEN/THEN: pesquisa §9 BC2 — hyp H-FASTLIFT; not AH/BB/BA FAST clone
    assert FASTLIFT_ID == "H-FASTLIFT"
    assert "anti-FP" in FASTLIFT_THESIS or "BC-FOREVER" in FASTLIFT_THESIS
    assert "AH" in FASTLIFT_THESIS or "≠" in FASTLIFT_THESIS
    assert "gibberish-tail" in FASTLIFT_CLAIM
    assert "LOOKUP" in FASTLIFT_ANTI_FP
    paths = FASTLIFT_BASELINE["paths"]
    assert set(paths) == BC0_MODES
    assert "FASTHOLD" in str(FASTLIFT_BASELINE.get("source", ""))


def test_given_baseline_when_p99_ok_then_no_regress() -> None:
    # Within ≤1.5× BC0/BB-FASTHOLD product walls (DECODE·ABSTAIN)
    latency = {
        "LOOKUP": {"p99_wall_ms": 0.0},
        "PEAK": {"p99_wall_ms": 0.5},
        "DECODE": {"p99_wall_ms": 17.0},
        "ABSTAIN": {"p99_wall_ms": 125.0},
    }
    assert p99_regressed(latency) == []


def test_given_subms_peak_when_noisy_then_not_regress() -> None:
    # GIVEN PEAK baseline < 1ms (microbench) WHEN noise THEN not speed IQ kill
    assert P99_REGRESS_MIN_BASE_MS == 1.0
    latency = {
        "LOOKUP": {"p99_wall_ms": 0.0},
        "PEAK": {"p99_wall_ms": 5.0},
        "DECODE": {"p99_wall_ms": 17.0},
        "ABSTAIN": {"p99_wall_ms": 125.0},
    }
    assert "PEAK" not in p99_regressed(latency)


def test_given_blowup_when_p99_then_regress_listed() -> None:
    latency = {
        "LOOKUP": {"p99_wall_ms": 0.0},
        "PEAK": {"p99_wall_ms": 0.5},
        "DECODE": {"p99_wall_ms": 17.0},
        "ABSTAIN": {"p99_wall_ms": 500.0},
    }
    assert "ABSTAIN" in p99_regressed(latency)


def test_given_packs_when_extract_then_board() -> None:
    bc = [{"product_mode": "ABSTAIN"} for _ in range(18)]
    bb = [{"product_mode": "ABSTAIN"} for _ in range(15)]
    ba = [{"product_mode": "ABSTAIN"} for _ in range(15)]
    az = [{"product_mode": "ABSTAIN"} for _ in range(12)]
    orf = [
        {"product_mode": "LOOKUP", "completion": "a.clear()"} for _ in range(3)
    ]
    board = extract_fastlift_board(
        latency=_board()["latency"],
        bc_rows=bc,
        ba_rows=ba,
        bb_rows=bb,
        az_rows=az,
        overrefuse_rows=orf,
        live_fp=0,
        near_miss_ok=True,
        known_lookup_ok=True,
        decode_content_ok=True,
        modes_visible=list(BC0_MODES),
        telemetry_ok={m: True for m in BC0_MODES},
    )
    assert board["bc_forever_false_hit"] == 0
    assert board["bb_forever_false_hit"] == 0
    assert board["ba_forever_false_hit"] == 0
    assert board["az_hold_false_hit"] == 0
    assert board["overrefuse_miss"] == 0
    assert board["p99_regress"] is False
    assert board["ah_fastlift_archive_untouched"] is True
    assert board["bb_fasthold_archive_untouched"] is True


def test_given_all_ok_when_decide_then_promote() -> None:
    out = decide_fastlift(board=_board(), anti_fp_signed=True)
    assert out.startswith("PROMOTE")
    assert FASTLIFT_ID in out


def test_given_bc_fh_when_decide_then_kill() -> None:
    out = decide_fastlift(
        board=_board(bc_forever_false_hit=1, bc_forever_ok_n=17),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "bc_forever" in out


def test_given_bb_fh_when_decide_then_kill() -> None:
    out = decide_fastlift(
        board=_board(bb_forever_false_hit=1, bb_forever_ok_n=14),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "bb_forever" in out


def test_given_p99_regress_when_decide_then_kill() -> None:
    lat = dict(_board()["latency"])
    lat["ABSTAIN"] = {"p50_wall_ms": 200.0, "p99_wall_ms": 500.0, "n": 32}
    board = _board(
        latency=lat,
        p99_regress=True,
        p99_regress_paths=["ABSTAIN"],
    )
    out = decide_fastlift(board=board, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "p99" in out.lower() or "regress" in out.lower()


def test_given_unsigned_when_decide_then_kill() -> None:
    out = decide_fastlift(board=_board(), anti_fp_signed=False)
    assert out.startswith("KILL")
    assert "anti-FP" in out
