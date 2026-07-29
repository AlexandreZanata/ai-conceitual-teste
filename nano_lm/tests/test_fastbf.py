"""Contract: Wave BF3 H-FASTBF — prod p50/p99 hold · anti-FP (≠ BE FASTBE)."""

from __future__ import annotations

from bd_session_ops import BD0_MODES
from fastbf_ops import (
    FASTBF_ANTI_FP,
    FASTBF_BASELINE,
    FASTBF_CLAIM,
    FASTBF_ID,
    FASTBF_THESIS,
    P99_REGRESS_MAX_RATIO,
    P99_REGRESS_MIN_BASE_MS,
    decide_fastbf,
    extract_fastbf_board,
    p99_regressed,
)


def _board(**overrides: object) -> dict:
    base = {
        "latency": {
            "LOOKUP": {"p50_wall_ms": 0.0, "p99_wall_ms": 0.0, "n": 64},
            "PEAK": {"p50_wall_ms": 0.01, "p99_wall_ms": 0.02, "n": 128},
            "DECODE": {"p50_wall_ms": 11.0, "p99_wall_ms": 12.0, "n": 12},
            "ABSTAIN": {"p50_wall_ms": 95.0, "p99_wall_ms": 110.0, "n": 32},
        },
        "bf_forever_false_hit": 0,
        "bf_forever_ok_n": 12,
        "bf_forever_n": 12,
        "be_forever_false_hit": 0,
        "be_forever_ok_n": 12,
        "be_forever_n": 12,
        "bd_forever_false_hit": 0,
        "bd_forever_ok_n": 12,
        "bd_forever_n": 12,
        "ba_forever_false_hit": 0,
        "ba_forever_ok_n": 15,
        "ba_forever_n": 15,
        "bb_forever_false_hit": 0,
        "bb_forever_ok_n": 15,
        "bb_forever_n": 15,
        "bc_forever_false_hit": 0,
        "bc_forever_ok_n": 18,
        "bc_forever_n": 18,
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
        "modes_visible": sorted(BD0_MODES),
        "modes_n": 4,
        "telemetry_ok": {m: True for m in BD0_MODES},
        "p99_regress_paths": [],
        "p99_regress": False,
        "p99_regress_max_ratio": P99_REGRESS_MAX_RATIO,
        "baseline_source": "H-FASTBE",
        "lookup_wall_neq_speed_iq": True,
        "warm_cache_vanity_forbidden": True,
        "bank_stuff_forbidden": True,
        "ba_bb_bc_bd_be_pass_neq_bf_forever": True,
        "be_fastbe_archive_untouched": True,
        "bd_fastgain_archive_untouched": True,
        "bc_fastlift_archive_untouched": True,
        "bb_fasthold_archive_untouched": True,
        "ba_fastreal_archive_untouched": True,
        "ah_fastlift_archive_untouched": True,
        "fp_for_ms_forbidden": True,
    }
    base.update(overrides)
    return base


def test_given_id_when_read_then_h_fastbf_not_be_clone() -> None:
    # GIVEN/WHEN/THEN: pesquisa §9 BF3 — hyp H-FASTBF; not BE FASTBE clone
    assert FASTBF_ID == "H-FASTBF"
    assert "BF-FOREVER" in FASTBF_THESIS or "anti-FP" in FASTBF_THESIS
    assert "FASTBE" in FASTBF_THESIS
    assert "gibberish-tail" in FASTBF_CLAIM
    assert "LOOKUP" in FASTBF_ANTI_FP or "BF-FOREVER" in FASTBF_ANTI_FP
    paths = FASTBF_BASELINE["paths"]
    assert set(paths) == BD0_MODES
    assert "FASTBE" in str(FASTBF_BASELINE.get("source", ""))


def test_given_baseline_when_p99_ok_then_no_regress() -> None:
    latency = {
        "LOOKUP": {"p99_wall_ms": 0.0},
        "PEAK": {"p99_wall_ms": 0.5},
        "DECODE": {"p99_wall_ms": 16.0},
        "ABSTAIN": {"p99_wall_ms": 180.0},
    }
    assert p99_regressed(latency) == []


def test_given_subms_peak_when_noisy_then_not_regress() -> None:
    assert P99_REGRESS_MIN_BASE_MS == 1.0
    latency = {
        "LOOKUP": {"p99_wall_ms": 0.0},
        "PEAK": {"p99_wall_ms": 5.0},
        "DECODE": {"p99_wall_ms": 16.0},
        "ABSTAIN": {"p99_wall_ms": 180.0},
    }
    assert "PEAK" not in p99_regressed(latency)


def test_given_blowup_when_p99_then_regress_listed() -> None:
    latency = {
        "LOOKUP": {"p99_wall_ms": 0.0},
        "PEAK": {"p99_wall_ms": 0.5},
        "DECODE": {"p99_wall_ms": 16.0},
        "ABSTAIN": {"p99_wall_ms": 500.0},
    }
    assert "ABSTAIN" in p99_regressed(latency)


def test_given_packs_when_extract_then_board() -> None:
    bf = [{"product_mode": "ABSTAIN"} for _ in range(12)]
    be = [{"product_mode": "ABSTAIN"} for _ in range(12)]
    bd = [{"product_mode": "ABSTAIN"} for _ in range(12)]
    bc = [{"product_mode": "ABSTAIN"} for _ in range(18)]
    bb = [{"product_mode": "ABSTAIN"} for _ in range(15)]
    ba = [{"product_mode": "ABSTAIN"} for _ in range(15)]
    az = [{"product_mode": "ABSTAIN"} for _ in range(12)]
    orf = [
        {"product_mode": "LOOKUP", "completion": "a.clear()"} for _ in range(3)
    ]
    board = extract_fastbf_board(
        latency=_board()["latency"],
        bf_rows=bf,
        be_rows=be,
        bd_rows=bd,
        ba_rows=ba,
        bb_rows=bb,
        bc_rows=bc,
        az_rows=az,
        overrefuse_rows=orf,
        live_fp=0,
        near_miss_ok=True,
        known_lookup_ok=True,
        decode_content_ok=True,
        modes_visible=list(BD0_MODES),
        telemetry_ok={m: True for m in BD0_MODES},
    )
    assert board["bf_forever_false_hit"] == 0
    assert board["be_forever_false_hit"] == 0
    assert board["p99_regress"] is False
    assert board["be_fastbe_archive_untouched"] is True


def test_given_all_ok_when_decide_then_promote() -> None:
    out = decide_fastbf(board=_board(), anti_fp_signed=True)
    assert out.startswith("PROMOTE")
    assert FASTBF_ID in out


def test_given_bf_fh_when_decide_then_kill() -> None:
    out = decide_fastbf(
        board=_board(bf_forever_false_hit=1, bf_forever_ok_n=11),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "bf_forever" in out


def test_given_be_fh_when_decide_then_kill() -> None:
    out = decide_fastbf(
        board=_board(be_forever_false_hit=1, be_forever_ok_n=11),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "be_forever" in out


def test_given_p99_regress_when_decide_then_kill() -> None:
    lat = dict(_board()["latency"])
    lat["ABSTAIN"] = {"p50_wall_ms": 200.0, "p99_wall_ms": 500.0, "n": 32}
    board = _board(
        latency=lat,
        p99_regress=True,
        p99_regress_paths=["ABSTAIN"],
    )
    out = decide_fastbf(board=board, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "p99" in out.lower() or "regress" in out.lower()


def test_given_unsigned_when_decide_then_kill() -> None:
    out = decide_fastbf(board=_board(), anti_fp_signed=False)
    assert out.startswith("KILL")
    assert "anti-FP" in out
