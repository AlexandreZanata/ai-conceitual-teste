"""Contract: Wave BG4 H-CTXBG — content bars · anti-FP (≠ BF CTXBF)."""

from __future__ import annotations

from bd_session_ops import BD0_MODES
from ctxbg_ops import (
    CTXBG_ANTI_FP,
    CTXBG_CLAIM,
    CTXBG_CTX_BASELINE,
    CTXBG_ID,
    CTXBG_THESIS,
    CTX_CONTENT_ROWS,
    decide_ctxbg,
    extract_ctxbg_board,
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


def _abstain_rows(n: int) -> list[dict]:
    return [{"product_mode": "ABSTAIN"} for _ in range(n)]


def _board(**overrides: object) -> dict:
    orf = [
        {"product_mode": "LOOKUP", "completion": "a.clear()"} for _ in range(3)
    ]
    base = extract_ctxbg_board(
        ctx_rows=_ctx_ok_rows(),
        apps_rows=_apps_ok(),
        bg_rows=_abstain_rows(12),
        bf_rows=_abstain_rows(12),
        be_rows=_abstain_rows(12),
        bd_rows=_abstain_rows(12),
        bc_rows=_abstain_rows(18),
        bb_rows=_abstain_rows(15),
        ba_rows=_abstain_rows(15),
        az_rows=_abstain_rows(12),
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


def test_given_id_when_read_then_h_ctxbg_not_bf_clone() -> None:
    # GIVEN/WHEN/THEN: pesquisa §9 BG4 — hyp H-CTXBG; not BF CTXBF clone
    assert CTXBG_ID == "H-CTXBG"
    assert "howto" in CTXBG_THESIS.lower() or "content" in CTXBG_THESIS.lower()
    assert "CTXBF" in CTXBG_THESIS or "BG-FOREVER" in CTXBG_THESIS
    assert "gibberish-tail" in CTXBG_CLAIM
    assert "LOOKUP" in CTXBG_ANTI_FP or "BG-FOREVER" in CTXBG_ANTI_FP
    assert bool(CTXBG_CTX_BASELINE.get("l_eff_alone_insufficient"))
    assert "CTXBG" in str(CTXBG_CTX_BASELINE.get("bg4_gate", ""))


def test_given_all_ok_when_decide_then_promote() -> None:
    out = decide_ctxbg(board=_board(), anti_fp_signed=True)
    assert out.startswith("PROMOTE")
    assert CTXBG_ID in out


def test_given_bg_fh_when_decide_then_kill() -> None:
    out = decide_ctxbg(
        board=_board(bg_forever_false_hit=1, bg_forever_ok_n=11),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "bg_forever" in out


def test_given_bf_fh_when_decide_then_kill() -> None:
    out = decide_ctxbg(
        board=_board(bf_forever_false_hit=1, bf_forever_ok_n=11),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "bf_forever" in out


def test_given_ctx_fail_when_decide_then_kill() -> None:
    out = decide_ctxbg(
        board=_board(ctx_content_ok=False, ctx_content_ok_n=3, howto_ok=False),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "ctx" in out.lower() or "howto" in out.lower()


def test_given_leff_alone_when_decide_then_kill() -> None:
    out = decide_ctxbg(
        board=_board(l_eff_alone_insufficient=False),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "L_eff" in out


def test_given_unsigned_when_decide_then_kill() -> None:
    out = decide_ctxbg(board=_board(), anti_fp_signed=False)
    assert out.startswith("KILL")
    assert "anti-FP" in out
