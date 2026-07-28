"""Contract: Wave BD5 BD-REAL-EVAL — product+ctx+speed + live battery; gen if BD4 PROMOTE."""

from __future__ import annotations

from bd_real_eval_ops import (
    ASK_BATTERY,
    BD_REAL_EVAL_CLAIM,
    BD_REAL_EVAL_ID,
    BD_REAL_EVAL_THESIS,
    PARENT_NANOGEN14,
    PROTOCOL,
    battery_pass,
    battery_row_ok,
    claim_is_honest,
    decide_bd_real_eval,
    gen_claim_allowed,
    mode_matches_expect,
    nanogen14_outcome_ok,
    telemetry_ok,
)


def test_given_contract_when_constants_then_match_bd5_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §9 BD5 — product pass · gen if BD4 PROMOTE
    assert BD_REAL_EVAL_ID == "BD-REAL-EVAL"
    assert len(ASK_BATTERY) >= 12
    assert PROTOCOL["live_ask_battery"] is True
    assert PROTOCOL["summary_only_forbidden"] is True
    assert PROTOCOL["eval_eq_prod_ask"] is True
    assert PROTOCOL["answer_usability_scored"] is True
    assert PROTOCOL["span_fallback_neq_gen"] is True
    assert PROTOCOL["intent_mismatch_is_false_hit"] is True
    claim_rule = str(PROTOCOL["gen_claim_rule"]).lower()
    assert "nanogen14" in claim_rule
    assert "true_continue" in claim_rule or "true-continue" in claim_rule
    assert "rename" in claim_rule
    assert "real eval" in BD_REAL_EVAL_THESIS.lower()
    assert "SEMINT" in BD_REAL_EVAL_THESIS
    assert PARENT_NANOGEN14 == "DEFER"
    assert claim_is_honest(BD_REAL_EVAL_CLAIM, nanogen14_decision="DEFER")
    assert not gen_claim_allowed(BD_REAL_EVAL_CLAIM)


def test_given_battery_pack_when_kinds_then_cover_modes() -> None:
    kinds = {p["kind"] for p in ASK_BATTERY}
    assert "known_lookup" in kinds
    assert "ood_abstain" in kinds
    assert "near_miss" in kinds
    assert "labeled_peak" in kinds
    assert "decode_content" in kinds
    assert "junk_trap" in kinds
    assert "bd_forever_reverse_fp" in kinds
    assert "bd_forever_mul_fp" in kinds
    assert "overrefuse_gold" in kinds
    assert "az_hold_div" in kinds
    assert "ba_forever_hold" in kinds
    assert "bb_forever_hold" in kinds
    assert "bc_forever_hold" in kinds
    modes = {p["expect_mode"] for p in ASK_BATTERY}
    assert modes == {"LOOKUP", "PEAK", "DECODE", "ABSTAIN"}
    assert all(str(p["id"]).startswith("BD-ASK-") for p in ASK_BATTERY)


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
        "id": "BD-ASK-01",
        "kind": "known_lookup",
        "expect_mode": "LOOKUP",
        "product_mode": "LOOKUP",
        "completion": "def add(a, b): return a + b",
        "wall_ms": 1.0,
        "n_new": 0,
        "content_ok": True,
    }
    assert battery_row_ok(row)


def test_given_bd_forever_fp_when_lookup_then_fail() -> None:
    row = {
        "id": "BD-ASK-07",
        "kind": "bd_forever_reverse_fp",
        "expect_mode": "ABSTAIN",
        "product_mode": "LOOKUP",
        "completion": 'f"{s[::-1]}"',
        "wall_ms": 0.0,
        "n_new": 0,
        "content_ok": True,
    }
    assert not battery_row_ok(row)


def test_given_all_pillars_when_decide_then_promote() -> None:
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
    assert battery_pass(rows)
    out = decide_bd_real_eval(
        semint_decision="PROMOTE (x)",
        fastgain_decision="PROMOTE (x)",
        ctxgain_decision="PROMOTE (x)",
        nanogen14_decision="DEFER (x)",
        battery_ok=True,
        claim=BD_REAL_EVAL_CLAIM,
    )
    assert out.startswith("PROMOTE")
    assert nanogen14_outcome_ok("DEFER (x)")


def test_given_gen_claim_when_defer_then_kill() -> None:
    out = decide_bd_real_eval(
        semint_decision="PROMOTE (x)",
        fastgain_decision="PROMOTE (x)",
        ctxgain_decision="PROMOTE (x)",
        nanogen14_decision="DEFER (x)",
        battery_ok=True,
        claim=BD_REAL_EVAL_CLAIM + " · mini-AGI unlocked",
    )
    assert out.startswith("KILL")


def test_given_battery_fail_when_decide_then_kill() -> None:
    out = decide_bd_real_eval(
        semint_decision="PROMOTE (x)",
        fastgain_decision="PROMOTE (x)",
        ctxgain_decision="PROMOTE (x)",
        nanogen14_decision="DEFER (x)",
        battery_ok=False,
        claim=BD_REAL_EVAL_CLAIM,
    )
    assert out.startswith("KILL")
    assert "battery" in out.lower()
