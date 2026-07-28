"""Contract: Wave BC3 H-CTXLIFT2 — content bars · anti-FP (≠ AH/BB/BA CTX)."""

from __future__ import annotations

from bc_ctxlift2_ops import (
    CTXLIFT2_ANTI_FP,
    CTXLIFT2_CLAIM,
    CTXLIFT2_CTX_BASELINE,
    CTXLIFT2_ID,
    CTXLIFT2_THESIS,
    CTX_CONTENT_ROWS,
    apps_ctx_content_ok,
    ctx_row_content_ok,
    decide_ctxlift2,
    extract_ctxlift2_board,
)
from bc_session_ops import BC0_MODES


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
    bc = [{"product_mode": "ABSTAIN"} for _ in range(18)]
    bb = [{"product_mode": "ABSTAIN"} for _ in range(15)]
    ba = [{"product_mode": "ABSTAIN"} for _ in range(15)]
    az = [{"product_mode": "ABSTAIN"} for _ in range(12)]
    orf = [
        {"product_mode": "LOOKUP", "completion": "a.clear()"} for _ in range(3)
    ]
    base = extract_ctxlift2_board(
        ctx_rows=_ctx_ok_rows(),
        apps_rows=_apps_ok(),
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
        modes_visible=list(BC0_MODES),
        telemetry_ok={m: True for m in BC0_MODES},
    )
    base.update(overrides)
    return base


def test_given_id_when_read_then_h_ctxlift2_not_ah_archive_clone() -> None:
    # GIVEN/WHEN/THEN: pesquisa §9 BC3 — hyp H-CTXLIFT2; not AH/BB/BA CTX clone
    assert CTXLIFT2_ID == "H-CTXLIFT2"
    assert "content" in CTXLIFT2_THESIS.lower()
    assert "L_eff" in CTXLIFT2_THESIS or "l_eff" in CTXLIFT2_THESIS
    assert "AH" in CTXLIFT2_THESIS or "≠" in CTXLIFT2_THESIS
    assert "gibberish-tail" in CTXLIFT2_CLAIM
    assert "LOOKUP" in CTXLIFT2_ANTI_FP
    assert CTXLIFT2_CTX_BASELINE.get("l_eff_alone_insufficient") is True
    assert "CTXLIFT2" in str(CTXLIFT2_CTX_BASELINE.get("bc3_gate", ""))
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
    out = decide_ctxlift2(board=_board(), anti_fp_signed=True)
    assert out.startswith("PROMOTE")
    assert CTXLIFT2_ID in out


def test_given_bc_fh_when_decide_then_kill() -> None:
    out = decide_ctxlift2(
        board=_board(bc_forever_false_hit=1, bc_forever_ok_n=17),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "bc_forever" in out


def test_given_bb_fh_when_decide_then_kill() -> None:
    out = decide_ctxlift2(
        board=_board(bb_forever_false_hit=1, bb_forever_ok_n=14),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "bb_forever" in out


def test_given_ctx_fail_when_decide_then_kill() -> None:
    out = decide_ctxlift2(
        board=_board(ctx_content_ok=False, ctx_content_ok_n=2),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "content" in out.lower()


def test_given_unsigned_when_decide_then_kill() -> None:
    out = decide_ctxlift2(board=_board(), anti_fp_signed=False)
    assert out.startswith("KILL")
    assert "anti-FP" in out
