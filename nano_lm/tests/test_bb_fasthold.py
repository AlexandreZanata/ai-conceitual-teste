"""Contract: Wave BB2 H-FASTHOLD — prod p50/p99 hold · anti-FP (≠ BA/AG FAST)."""

from __future__ import annotations

from bb_fasthold_ops import (
    FASTHOLD_ANTI_FP,
    FASTHOLD_BASELINE,
    FASTHOLD_CLAIM,
    FASTHOLD_ID,
    FASTHOLD_THESIS,
    P99_REGRESS_MAX_RATIO,
    P99_REGRESS_MIN_BASE_MS,
    decide_fasthold,
    extract_fasthold_board,
    p99_regressed,
)
from bb_session_ops import BB0_MODES


def _board(**overrides: object) -> dict:
    base = {
        "latency": {
            "LOOKUP": {"p50_wall_ms": 0.0, "p99_wall_ms": 0.0, "n": 64},
            "PEAK": {"p50_wall_ms": 0.01, "p99_wall_ms": 0.02, "n": 128},
            "DECODE": {"p50_wall_ms": 11.0, "p99_wall_ms": 12.0, "n": 12},
            "ABSTAIN": {"p50_wall_ms": 95.0, "p99_wall_ms": 110.0, "n": 32},
        },
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
        "modes_visible": sorted(BB0_MODES),
        "modes_n": 4,
        "telemetry_ok": {m: True for m in BB0_MODES},
        "p99_regress_paths": [],
        "p99_regress": False,
        "p99_regress_max_ratio": P99_REGRESS_MAX_RATIO,
        "baseline_source": "H-FASTREAL",
        "lookup_wall_neq_speed_iq": True,
        "warm_cache_vanity_forbidden": True,
        "bank_stuff_forbidden": True,
        "ba_pass_neq_bb_forever": True,
        "ba_fastreal_archive_untouched": True,
        "ag_fastreal_archive_untouched": True,
    }
    base.update(overrides)
    return base


def test_given_id_when_read_then_h_fasthold_not_fastreal_rename() -> None:
    # GIVEN/WHEN/THEN: pesquisa §8 BB2 — hyp H-FASTHOLD; not BA/AG FASTREAL clone
    assert FASTHOLD_ID == "H-FASTHOLD"
    assert "anti-FP" in FASTHOLD_THESIS or "BB-FOREVER" in FASTHOLD_THESIS
    assert "FASTREAL" in FASTHOLD_THESIS or "≠" in FASTHOLD_THESIS
    assert "gibberish-tail" in FASTHOLD_CLAIM
    assert "LOOKUP" in FASTHOLD_ANTI_FP
    paths = FASTHOLD_BASELINE["paths"]
    assert set(paths) == BB0_MODES
    assert "FASTREAL" in str(FASTHOLD_BASELINE.get("source", ""))


def test_given_baseline_when_p99_ok_then_no_regress() -> None:
    # Within ≤1.5× BB0_SPEED_BASELINE product walls (DECODE·ABSTAIN)
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
    bb = [{"product_mode": "ABSTAIN"} for _ in range(15)]
    ba = [{"product_mode": "ABSTAIN"} for _ in range(15)]
    az = [{"product_mode": "ABSTAIN"} for _ in range(12)]
    orf = [
        {"product_mode": "LOOKUP", "completion": "a.clear()"} for _ in range(3)
    ]
    board = extract_fasthold_board(
        latency=_board()["latency"],
        bb_rows=bb,
        ba_rows=ba,
        az_rows=az,
        overrefuse_rows=orf,
        live_fp=0,
        near_miss_ok=True,
        known_lookup_ok=True,
        decode_content_ok=True,
        modes_visible=list(BB0_MODES),
        telemetry_ok={m: True for m in BB0_MODES},
    )
    assert board["bb_forever_false_hit"] == 0
    assert board["ba_forever_false_hit"] == 0
    assert board["az_hold_false_hit"] == 0
    assert board["overrefuse_miss"] == 0
    assert board["p99_regress"] is False
    assert board["ba_fastreal_archive_untouched"] is True
    assert board["ag_fastreal_archive_untouched"] is True


def test_given_all_ok_when_decide_then_promote() -> None:
    out = decide_fasthold(board=_board(), anti_fp_signed=True)
    assert out.startswith("PROMOTE")
    assert FASTHOLD_ID in out


def test_given_bb_fh_when_decide_then_kill() -> None:
    out = decide_fasthold(
        board=_board(bb_forever_false_hit=1, bb_forever_ok_n=14),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "bb_forever" in out


def test_given_ba_fh_when_decide_then_kill() -> None:
    out = decide_fasthold(
        board=_board(ba_forever_false_hit=1, ba_forever_ok_n=14),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "ba_forever" in out


def test_given_p99_regress_when_decide_then_kill() -> None:
    lat = dict(_board()["latency"])
    lat["ABSTAIN"] = {"p50_wall_ms": 200.0, "p99_wall_ms": 500.0, "n": 32}
    board = _board(
        latency=lat,
        p99_regress=True,
        p99_regress_paths=["ABSTAIN"],
    )
    out = decide_fasthold(board=board, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "p99" in out.lower() or "regress" in out.lower()


def test_given_unsigned_when_decide_then_kill() -> None:
    out = decide_fasthold(board=_board(), anti_fp_signed=False)
    assert out.startswith("KILL")
    assert "anti-FP" in out
