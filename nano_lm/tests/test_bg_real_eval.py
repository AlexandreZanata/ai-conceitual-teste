"""Contract: Wave BG6 BG-REAL-EVAL — product+util+ctx+speed + live battery."""

from __future__ import annotations

from bg_real_eval_ops import (
    ASK_BATTERY,
    BG_REAL_EVAL_CLAIM,
    BG_REAL_EVAL_ID,
    BG_REAL_EVAL_THESIS,
    PARENT_NANOGEN17,
    PROTOCOL,
    battery_pass,
    battery_row_ok,
    claim_is_honest,
    decide_bg_real_eval,
    gen_claim_allowed,
    mode_matches_expect,
    nanogen17_outcome_ok,
    telemetry_ok,
)


def test_given_contract_when_constants_then_match_bg6_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §9 BG6 — product pass · gen if BG5 PROMOTE
    assert BG_REAL_EVAL_ID == "BG-REAL-EVAL"
    assert len(ASK_BATTERY) >= 17
    assert PROTOCOL["live_ask_battery"] is True
    assert PROTOCOL["summary_only_forbidden"] is True
    assert PROTOCOL["eval_eq_prod_ask"] is True
    assert PROTOCOL["answer_usability_scored"] is True
    assert PROTOCOL["span_fallback_neq_gen"] is True
    assert PROTOCOL["intent_mismatch_is_false_hit"] is True
    assert PROTOCOL["unary_mismatch_is_false_hit"] is True
    assert PROTOCOL["transform_mismatch_is_false_hit"] is True
    assert PROTOCOL["utilization_scored"] is True
    claim_rule = str(PROTOCOL["gen_claim_rule"]).lower()
    assert "nanogen17" in claim_rule
    assert "true_continue" in claim_rule or "true-continue" in claim_rule
    assert "rename" in claim_rule or "skip" in claim_rule
    assert "real eval" in BG_REAL_EVAL_THESIS.lower()
    assert "UNARYINT" in BG_REAL_EVAL_THESIS
    assert PARENT_NANOGEN17 == "SKIP"
    assert claim_is_honest(BG_REAL_EVAL_CLAIM, nanogen17_decision="SKIP")
    assert not gen_claim_allowed(BG_REAL_EVAL_CLAIM)


def test_given_battery_pack_when_kinds_then_cover_modes() -> None:
    kinds = {p["kind"] for p in ASK_BATTERY}
    assert "known_lookup" in kinds
    assert "ood_abstain" in kinds
    assert "near_miss" in kinds
    assert "labeled_peak" in kinds
    assert "decode_content" in kinds
    assert "junk_trap" in kinds
    assert "bg_forever_unary_fp" in kinds
    assert "bg_forever_transform_fp" in kinds
    assert "overrefuse_gold" in kinds
    assert "az_hold_div" in kinds
    assert "ba_forever_hold" in kinds
    assert "bb_forever_hold" in kinds
    assert "bc_forever_hold" in kinds
    assert "bd_forever_hold" in kinds
    assert "be_forever_hold" in kinds
    assert "bf_forever_hold" in kinds
    assert "utilization_smoke" in kinds
    modes = {p["expect_mode"] for p in ASK_BATTERY}
    assert modes == {"LOOKUP", "PEAK", "DECODE", "ABSTAIN"}
    assert all(str(p["id"]).startswith("BG-ASK-") for p in ASK_BATTERY)


def test_given_telemetry_when_missing_then_fail() -> None:
    assert not telemetry_ok({"product_mode": "LOOKUP"})
    assert telemetry_ok(
        {"product_mode": "LOOKUP", "wall_ms": 1.0, "n_new": 0}
    )


def test_given_decode_path_when_abstain_junk_then_mode_ok() -> None:
    assert mode_matches_expect(
        product_mode="ABSTAIN",
        expect_mode="DECODE",
        kind="decode_content",
    )


def test_given_row_when_mode_and_content_then_ok() -> None:
    row = {
        "id": "BG-ASK-01",
        "kind": "known_lookup",
        "expect_mode": "LOOKUP",
        "product_mode": "LOOKUP",
        "completion": "def add(a, b): return a + b",
        "wall_ms": 1.0,
        "n_new": 0,
        "content_ok": True,
    }
    assert battery_row_ok(row)


def test_given_bg_forever_fp_when_lookup_then_fail() -> None:
    row = {
        "id": "BG-ASK-07",
        "kind": "bg_forever_unary_fp",
        "expect_mode": "ABSTAIN",
        "product_mode": "LOOKUP",
        "completion": "def add(a, b): return a + b",
        "wall_ms": 0.0,
        "n_new": 0,
        "content_ok": True,
    }
    assert not battery_row_ok(row)


def _ok_battery() -> list[dict]:
    rows = []
    for p in ASK_BATTERY:
        mode = p["expect_mode"]
        if p["kind"] == "decode_content":
            mode = "ABSTAIN"
            comp = "NO_ANSWER"
        elif mode == "LOOKUP":
            comp = "def add(a, b): return a + b"
        elif mode == "PEAK":
            comp = "Ownership is a set of rules that govern memory."
        else:
            comp = "NO_ANSWER"
        rows.append(
            {
                **p,
                "product_mode": mode,
                "completion": comp,
                "wall_ms": 1.0,
                "n_new": 0 if mode != "DECODE" else 8,
                "content_ok": True,
            }
        )
    return rows


def test_given_all_pillars_when_decide_then_promote() -> None:
    rows = _ok_battery()
    assert battery_pass(rows)
    out = decide_bg_real_eval(
        unaryint_decision="PROMOTE (x)",
        shippub_decision="PROMOTE (x)",
        fastbg_decision="PROMOTE (x)",
        ctxbg_decision="PROMOTE (x)",
        nanogen17_decision="SKIP (x)",
        battery_ok=True,
        claim=BG_REAL_EVAL_CLAIM,
    )
    assert out.startswith("PROMOTE")
    assert nanogen17_outcome_ok("SKIP (x)")
    assert "gen locked" in out.lower()


def test_given_gen_claim_when_skip_then_kill() -> None:
    out = decide_bg_real_eval(
        unaryint_decision="PROMOTE (x)",
        shippub_decision="PROMOTE (x)",
        fastbg_decision="PROMOTE (x)",
        ctxbg_decision="PROMOTE (x)",
        nanogen17_decision="SKIP (x)",
        battery_ok=True,
        claim=BG_REAL_EVAL_CLAIM + " · mini-AGI unlocked",
    )
    assert out.startswith("KILL")


def test_given_battery_fail_when_decide_then_kill() -> None:
    out = decide_bg_real_eval(
        unaryint_decision="PROMOTE (x)",
        shippub_decision="PROMOTE (x)",
        fastbg_decision="PROMOTE (x)",
        ctxbg_decision="PROMOTE (x)",
        nanogen17_decision="SKIP (x)",
        battery_ok=False,
        claim=BG_REAL_EVAL_CLAIM,
    )
    assert out.startswith("KILL")
    assert "battery" in out.lower()


def test_given_shippub_missing_when_decide_then_kill() -> None:
    out = decide_bg_real_eval(
        unaryint_decision="PROMOTE (x)",
        shippub_decision="MISSING",
        fastbg_decision="PROMOTE (x)",
        ctxbg_decision="PROMOTE (x)",
        nanogen17_decision="SKIP (x)",
        battery_ok=True,
        claim=BG_REAL_EVAL_CLAIM,
    )
    assert out.startswith("KILL")
    assert "shippub" in out.lower()
