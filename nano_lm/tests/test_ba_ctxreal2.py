"""Contract: Wave BA3 H-CTXREAL2 — content bars · anti-FP hold (≠ AG)."""

from __future__ import annotations

from ba_ctxreal2_ops import (
    BA_CTXREAL2_ANTI_FP,
    BA_CTXREAL2_CLAIM,
    BA_CTXREAL2_CTX_BASELINE,
    BA_CTXREAL2_ID,
    BA_CTXREAL2_THESIS,
    CTX_CONTENT_ROWS,
    apps_ctx_content_ok,
    ctx_row_content_ok,
    decide_ba_ctxreal2,
    extract_ba_ctxreal2_board,
)
from ba_session_ops import BA0_MODES


def _latency() -> dict:
    return {
        "LOOKUP": {"p50_wall_ms": 0.0, "p99_wall_ms": 0.0, "n": 64},
        "PEAK": {"p50_wall_ms": 0.02, "p99_wall_ms": 0.04, "n": 128},
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
        elif kind == "howto":
            rows.append(
                {
                    **item,
                    "product_mode": "LOOKUP",
                    "completion": item["gold"],
                    "mode": "WRAP_LOOKUP",
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
    forever = [{"product_mode": "ABSTAIN"} for _ in range(15)]
    az = [{"product_mode": "ABSTAIN"} for _ in range(12)]
    orf = [
        {"product_mode": "LOOKUP", "completion": "a.clear()"} for _ in range(3)
    ]
    base = extract_ba_ctxreal2_board(
        ctx_rows=_ctx_ok_rows(),
        apps_rows=_apps_ok(),
        forever_rows=forever,
        az_rows=az,
        overrefuse_rows=orf,
        live_fp=0,
        near_miss_ok=True,
        known_lookup_ok=True,
        decode_content_ok=True,
        peak_ok=True,
        latency=_latency(),
        modes_visible=list(BA0_MODES),
        telemetry_ok={m: True for m in BA0_MODES},
    )
    base.update(overrides)
    return base


def test_given_id_when_read_then_h_ctxreal2_not_ag_clone() -> None:
    assert BA_CTXREAL2_ID == "H-CTXREAL2"
    assert "content" in BA_CTXREAL2_THESIS.lower()
    assert "L_eff" in BA_CTXREAL2_THESIS or "l_eff" in BA_CTXREAL2_THESIS
    assert "AG" in BA_CTXREAL2_THESIS or "≠" in BA_CTXREAL2_THESIS
    assert "gibberish-tail" in BA_CTXREAL2_CLAIM
    assert "LOOKUP" in BA_CTXREAL2_ANTI_FP
    assert BA_CTXREAL2_CTX_BASELINE.get("l_eff_alone_insufficient") is True
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
    out = decide_ba_ctxreal2(board=_board(), anti_fp_signed=True)
    assert out.startswith("PROMOTE")
    assert BA_CTXREAL2_ID in out


def test_given_forever_fp_when_decide_then_kill() -> None:
    out = decide_ba_ctxreal2(
        board=_board(forever_false_hit=1, forever_ok_n=14),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "forever" in out.lower()


def test_given_ctx_fail_when_decide_then_kill() -> None:
    out = decide_ba_ctxreal2(
        board=_board(ctx_content_ok=False, ctx_content_ok_n=2),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "content" in out.lower()


def test_given_unsigned_when_decide_then_kill() -> None:
    out = decide_ba_ctxreal2(board=_board(), anti_fp_signed=False)
    assert out.startswith("KILL")
    assert "anti-FP" in out
