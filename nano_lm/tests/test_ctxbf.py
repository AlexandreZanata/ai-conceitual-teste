"""Contract: Wave BF4 H-CTXBF — content bars · anti-FP (≠ BE CTXBE)."""

from __future__ import annotations

from bd_session_ops import BD0_MODES
from ctxbf_ops import (
    CTXBF_ANTI_FP,
    CTXBF_CLAIM,
    CTXBF_CTX_BASELINE,
    CTXBF_ID,
    CTXBF_THESIS,
    CTX_CONTENT_ROWS,
    decide_ctxbf,
    extract_ctxbf_board,
)


def _latency() -> dict:
    return {
        "LOOKUP": {"p50_wall_ms": 0.0, "p99_wall_ms": 0.0, "n": 64},
        "PEAK": {"p50_wall_ms": 0.01, "p99_wall_ms": 0.02, "n": 128},
        "DECODE": {"p50_wall_ms": 11.0, "p99_wall_ms": 12.0, "n": 12},
        "ABSTAIN": {"p50_wall_ms": 95.0, "p99_wall_ms": 110.0, "n": 32},
    }


def _ctx_ok_rows() -> list[dict]:
    rows = []
    for item in CTX_CONTENT_ROWS:
        kind = item["kind"]
        if kind == "long":
            rows.append(
                {
                    **item,
                    "product_mode": "PEAK",
                    "completion": "Ownership is a set of rules that govern memory.",
                }
            )
        else:
            rows.append(
                {
                    **item,
                    "product_mode": "LOOKUP",
                    "completion": item["gold"],
                    "mode": "WRAP_LOOKUP",
                }
            )
    return rows


def _apps_ok() -> list[dict]:
    return [
        {
            "app_id": "known-ask",
            "product_mode": "LOOKUP",
            "mode": "WRAP_LOOKUP",
            "completion": "CS = ENT / 32",
            "gold": "CS = ENT / 32",
            "modeui_line": "mode=LOOKUP",
        },
        {
            "app_id": "howto",
            "product_mode": "LOOKUP",
            "mode": "WRAP_LOOKUP",
            "completion": "a.append(x)",
            "gold": "a.append(x)",
            "modeui_line": "mode=LOOKUP",
        },
        {
            "app_id": "long-doc",
            "product_mode": "LOOKUP",
            "mode": "WRAP_LOOKUP",
            "completion": "GET /rest/tx/<TX-HASH>.<bin|hex|json>",
            "gold": "GET /rest/tx/<TX-HASH>.<bin|hex|json>",
            "modeui_line": "mode=LOOKUP",
        },
    ]


def _board(**overrides: object) -> dict:
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
    base = extract_ctxbf_board(
        ctx_rows=_ctx_ok_rows(),
        apps_rows=_apps_ok(),
        bf_rows=bf,
        be_rows=be,
        bd_rows=bd,
        bc_rows=bc,
        bb_rows=bb,
        ba_rows=ba,
        az_rows=az,
        overrefuse_rows=orf,
        live_fp=0,
        near_miss_ok=True,
        known_lookup_ok=True,
        decode_content_ok=True,
        peak_ok=True,
        latency=_latency(),
        modes_visible=list(BD0_MODES),
        telemetry_ok={m: True for m in BD0_MODES},
    )
    base.update(overrides)
    return base


def test_given_id_when_read_then_h_ctxbf_not_be_clone() -> None:
    # GIVEN/WHEN/THEN: pesquisa §9 BF4 — hyp H-CTXBF; not BE CTXBE clone
    assert CTXBF_ID == "H-CTXBF"
    assert "howto" in CTXBF_THESIS.lower() or "content" in CTXBF_THESIS.lower()
    assert "CTXBE" in CTXBF_THESIS or "BF-FOREVER" in CTXBF_THESIS
    assert "gibberish-tail" in CTXBF_CLAIM
    assert "LOOKUP" in CTXBF_ANTI_FP or "BF-FOREVER" in CTXBF_ANTI_FP
    assert bool(CTXBF_CTX_BASELINE.get("l_eff_alone_insufficient"))
    assert "CTXBF" in str(CTXBF_CTX_BASELINE.get("bf4_gate", ""))


def test_given_all_ok_when_decide_then_promote() -> None:
    out = decide_ctxbf(board=_board(), anti_fp_signed=True)
    assert out.startswith("PROMOTE")
    assert CTXBF_ID in out


def test_given_bf_fh_when_decide_then_kill() -> None:
    out = decide_ctxbf(
        board=_board(bf_forever_false_hit=1, bf_forever_ok_n=11),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "bf_forever" in out


def test_given_be_fh_when_decide_then_kill() -> None:
    out = decide_ctxbf(
        board=_board(be_forever_false_hit=1, be_forever_ok_n=11),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "be_forever" in out


def test_given_ctx_fail_when_decide_then_kill() -> None:
    out = decide_ctxbf(
        board=_board(ctx_content_ok=False, ctx_content_ok_n=3, howto_ok=False),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "ctx" in out.lower() or "howto" in out.lower()


def test_given_leff_alone_when_decide_then_kill() -> None:
    out = decide_ctxbf(
        board=_board(l_eff_alone_insufficient=False),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "L_eff" in out


def test_given_unsigned_when_decide_then_kill() -> None:
    out = decide_ctxbf(board=_board(), anti_fp_signed=False)
    assert out.startswith("KILL")
    assert "anti-FP" in out
