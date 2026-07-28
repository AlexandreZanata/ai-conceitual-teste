"""Contract: Wave BA2 H-FASTREAL — prod p50/p99 · anti-FP hold (≠ AG)."""

from __future__ import annotations

from ba_fastreal_ops import (
    BA_FASTREAL_ANTI_FP,
    BA_FASTREAL_BASELINE,
    BA_FASTREAL_CLAIM,
    BA_FASTREAL_ID,
    BA_FASTREAL_THESIS,
    P99_REGRESS_MAX_RATIO,
    decide_ba_fastreal,
    extract_ba_fastreal_board,
    p99_regressed,
)
from ba_session_ops import BA0_MODES


def _board(**overrides: object) -> dict:
    base = {
        "latency": {
            "LOOKUP": {"p50_wall_ms": 0.0, "p99_wall_ms": 0.0, "n": 64},
            "PEAK": {"p50_wall_ms": 0.02, "p99_wall_ms": 0.04, "n": 128},
            "DECODE": {"p50_wall_ms": 11.0, "p99_wall_ms": 12.0, "n": 12},
            "ABSTAIN": {"p50_wall_ms": 95.0, "p99_wall_ms": 110.0, "n": 32},
        },
        "forever_false_hit": 0,
        "forever_ok_n": 15,
        "forever_n": 15,
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
        "modes_visible": sorted(BA0_MODES),
        "modes_n": 4,
        "telemetry_ok": {m: True for m in BA0_MODES},
        "p99_regress_paths": [],
        "p99_regress": False,
        "p99_regress_max_ratio": P99_REGRESS_MAX_RATIO,
        "baseline_source": "H-PRODGEN",
        "lookup_wall_neq_speed_iq": True,
        "warm_cache_vanity_forbidden": True,
        "bank_stuff_forbidden": True,
        "ag_fastreal_archive_untouched": True,
    }
    base.update(overrides)
    return base


def test_given_id_when_read_then_h_fastreal_ba2_not_ag_clone() -> None:
    # GIVEN/WHEN/THEN: pesquisa §8 BA2 — hyp name H-FASTREAL; AG archive distinct
    assert BA_FASTREAL_ID == "H-FASTREAL"
    assert "anti-FP" in BA_FASTREAL_THESIS or "forever" in BA_FASTREAL_THESIS.lower()
    assert "AG" in BA_FASTREAL_THESIS or "≠" in BA_FASTREAL_THESIS
    assert "gibberish-tail" in BA_FASTREAL_CLAIM
    assert "LOOKUP" in BA_FASTREAL_ANTI_FP
    paths = BA_FASTREAL_BASELINE["paths"]
    assert set(paths) == BA0_MODES


def test_given_baseline_when_p99_ok_then_no_regress() -> None:
    latency = {
        "LOOKUP": {"p99_wall_ms": 0.0},
        "PEAK": {"p99_wall_ms": 0.04},
        "DECODE": {"p99_wall_ms": 13.0},
        "ABSTAIN": {"p99_wall_ms": 119.0},
    }
    assert p99_regressed(latency) == []


def test_given_blowup_when_p99_then_regress_listed() -> None:
    latency = {
        "LOOKUP": {"p99_wall_ms": 0.0},
        "PEAK": {"p99_wall_ms": 0.04},
        "DECODE": {"p99_wall_ms": 13.0},
        "ABSTAIN": {"p99_wall_ms": 500.0},
    }
    assert "ABSTAIN" in p99_regressed(latency)


def test_given_packs_when_extract_then_board() -> None:
    forever = [{"product_mode": "ABSTAIN"} for _ in range(15)]
    az = [{"product_mode": "ABSTAIN"} for _ in range(12)]
    orf = [
        {"product_mode": "LOOKUP", "completion": "a.clear()"} for _ in range(3)
    ]
    board = extract_ba_fastreal_board(
        latency=_board()["latency"],
        forever_rows=forever,
        az_rows=az,
        overrefuse_rows=orf,
        live_fp=0,
        near_miss_ok=True,
        known_lookup_ok=True,
        decode_content_ok=True,
        modes_visible=list(BA0_MODES),
        telemetry_ok={m: True for m in BA0_MODES},
    )
    assert board["forever_false_hit"] == 0
    assert board["az_hold_false_hit"] == 0
    assert board["overrefuse_miss"] == 0
    assert board["p99_regress"] is False
    assert board["ag_fastreal_archive_untouched"] is True


def test_given_all_ok_when_decide_then_promote() -> None:
    out = decide_ba_fastreal(board=_board(), anti_fp_signed=True)
    assert out.startswith("PROMOTE")
    assert BA_FASTREAL_ID in out


def test_given_forever_fp_when_decide_then_kill() -> None:
    out = decide_ba_fastreal(
        board=_board(forever_false_hit=1, forever_ok_n=14),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "forever" in out.lower()


def test_given_p99_regress_when_decide_then_kill() -> None:
    lat = _board()["latency"]
    lat = dict(lat)
    lat["ABSTAIN"] = {"p50_wall_ms": 200.0, "p99_wall_ms": 500.0, "n": 32}
    board = _board(
        latency=lat,
        p99_regress=True,
        p99_regress_paths=["ABSTAIN"],
    )
    out = decide_ba_fastreal(board=board, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "p99" in out.lower() or "regress" in out.lower()


def test_given_unsigned_when_decide_then_kill() -> None:
    out = decide_ba_fastreal(board=_board(), anti_fp_signed=False)
    assert out.startswith("KILL")
    assert "anti-FP" in out
