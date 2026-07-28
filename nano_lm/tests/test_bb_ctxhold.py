"""Contract: Wave BB3 H-CTXHOLD — content bars · anti-FP (≠ BA/AG CTX)."""

from __future__ import annotations

from bb_ctxhold_ops import (
    CTXHOLD_ANTI_FP,
    CTXHOLD_CLAIM,
    CTXHOLD_CTX_BASELINE,
    CTXHOLD_ID,
    CTXHOLD_THESIS,
    CTX_CONTENT_ROWS,
    apps_ctx_content_ok,
    ctx_row_content_ok,
    decide_ctxhold,
    extract_ctxhold_board,
)
from bb_session_ops import BB0_MODES


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
    bb = [{"product_mode": "ABSTAIN"} for _ in range(15)]
    ba = [{"product_mode": "ABSTAIN"} for _ in range(15)]
    az = [{"product_mode": "ABSTAIN"} for _ in range(12)]
    orf = [
        {"product_mode": "LOOKUP", "completion": "a.clear()"} for _ in range(3)
    ]
    base = extract_ctxhold_board(
        ctx_rows=_ctx_ok_rows(),
        apps_rows=_apps_ok(),
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
        modes_visible=list(BB0_MODES),
        telemetry_ok={m: True for m in BB0_MODES},
    )
    base.update(overrides)
    return base


def test_given_id_when_read_then_h_ctxhold_not_ctxreal_rename() -> None:
    # GIVEN/WHEN/THEN: pesquisa §8 BB3 — hyp H-CTXHOLD; not BA/AG CTX clone
    assert CTXHOLD_ID == "H-CTXHOLD"
    assert "content" in CTXHOLD_THESIS.lower()
    assert "L_eff" in CTXHOLD_THESIS or "l_eff" in CTXHOLD_THESIS
    assert "CTXREAL" in CTXHOLD_THESIS or "≠" in CTXHOLD_THESIS
    assert "gibberish-tail" in CTXHOLD_CLAIM
    assert "LOOKUP" in CTXHOLD_ANTI_FP
    assert CTXHOLD_CTX_BASELINE.get("l_eff_alone_insufficient") is True
    assert "CTXHOLD" in str(CTXHOLD_CTX_BASELINE.get("bb3_gate", ""))
    assert len(CTX_CONTENT_ROWS) >= 5
    kinds = {r["kind"] for r in CTX_CONTENT_ROWS}
    assert kinds == {"howto", "cite", "long"}


def test_given_howto_when_content_then_ok() -> None:
    row = {
        "kind": "howto",
        "product_mode": "LOOKUP",
        "mode": "WRAP_LOOKUP",
        "completion": "a.append(x)",
        "gold": "a.append(x)",
    }
    assert ctx_row_content_ok(row) is True


def test_given_peak_junk_when_long_then_fail() -> None:
    row = {
        "kind": "long",
        "product_mode": "PEAK",
        "completion": "....",
        "gold": "Ownership",
    }
    assert ctx_row_content_ok(row) is False


def test_given_apps_when_content_then_ok() -> None:
    assert apps_ctx_content_ok(_apps_ok()) is True


def test_given_all_ok_when_decide_then_promote() -> None:
    out = decide_ctxhold(board=_board(), anti_fp_signed=True)
    assert out.startswith("PROMOTE")
    assert CTXHOLD_ID in out


def test_given_bb_fh_when_decide_then_kill() -> None:
    out = decide_ctxhold(
        board=_board(bb_forever_false_hit=1, bb_forever_ok_n=14),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "bb_forever" in out


def test_given_ba_fh_when_decide_then_kill() -> None:
    out = decide_ctxhold(
        board=_board(ba_forever_false_hit=1, ba_forever_ok_n=14),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "ba_forever" in out


def test_given_ctx_fail_when_decide_then_kill() -> None:
    out = decide_ctxhold(
        board=_board(ctx_content_ok=False, ctx_content_ok_n=2),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "content" in out.lower()


def test_given_unsigned_when_decide_then_kill() -> None:
    out = decide_ctxhold(board=_board(), anti_fp_signed=False)
    assert out.startswith("KILL")
    assert "anti-FP" in out
