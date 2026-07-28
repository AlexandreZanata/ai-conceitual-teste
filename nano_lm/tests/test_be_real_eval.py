"""Contract: Wave BE6 BE-REAL-EVAL — product+util+ctx+speed + live battery."""

from __future__ import annotations

from be_real_eval_ops import (
    ASK_BATTERY,
    BE_REAL_EVAL_CLAIM,
    BE_REAL_EVAL_ID,
    BE_REAL_EVAL_THESIS,
    PARENT_NANOGEN15,
    PROTOCOL,
    battery_pass,
    battery_row_ok,
    claim_is_honest,
    decide_be_real_eval,
    gen_claim_allowed,
    mode_matches_expect,
    nanogen15_outcome_ok,
    telemetry_ok,
)


def test_given_contract_when_constants_then_match_be6_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §9 BE6 — product pass · gen if BE5 PROMOTE
    assert BE_REAL_EVAL_ID == "BE-REAL-EVAL"
    assert len(ASK_BATTERY) >= 15
    assert PROTOCOL["live_ask_battery"] is True
    assert PROTOCOL["summary_only_forbidden"] is True
    assert PROTOCOL["eval_eq_prod_ask"] is True
    assert PROTOCOL["answer_usability_scored"] is True
    assert PROTOCOL["span_fallback_neq_gen"] is True
    assert PROTOCOL["intent_mismatch_is_false_hit"] is True
    assert PROTOCOL["utilization_scored"] is True
    claim_rule = str(PROTOCOL["gen_claim_rule"]).lower()
    assert "nanogen15" in claim_rule
    assert "true_continue" in claim_rule or "true-continue" in claim_rule
    assert "rename" in claim_rule
    assert "real eval" in BE_REAL_EVAL_THESIS.lower()
    assert "COMPINT" in BE_REAL_EVAL_THESIS
    assert PARENT_NANOGEN15 == "DEFER"
    assert claim_is_honest(BE_REAL_EVAL_CLAIM, nanogen15_decision="DEFER")
    assert not gen_claim_allowed(BE_REAL_EVAL_CLAIM)


def test_given_battery_pack_when_kinds_then_cover_modes() -> None:
    kinds = {p["kind"] for p in ASK_BATTERY}
    assert "known_lookup" in kinds
    assert "ood_abstain" in kinds
    assert "near_miss" in kinds
    assert "labeled_peak" in kinds
    assert "decode_content" in kinds
    assert "junk_trap" in kinds
    assert "be_forever_type_fp" in kinds
    assert "be_forever_neighbor_fp" in kinds
    assert "overrefuse_gold" in kinds
    assert "az_hold_div" in kinds
    assert "ba_forever_hold" in kinds
    assert "bb_forever_hold" in kinds
    assert "bc_forever_hold" in kinds
    assert "bd_forever_hold" in kinds
    assert "utilization_smoke" in kinds
    modes = {p["expect_mode"] for p in ASK_BATTERY}
    assert modes == {"LOOKUP", "PEAK", "DECODE", "ABSTAIN"}
    assert all(str(p["id"]).startswith("BE-ASK-") for p in ASK_BATTERY)


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
        "id": "BE-ASK-01",
        "kind": "known_lookup",
        "expect_mode": "LOOKUP",
        "product_mode": "LOOKUP",
        "completion": "def add(a, b): return a + b",
        "wall_ms": 1.0,
        "n_new": 0,
        "content_ok": True,
    }
    assert battery_row_ok(row)


def test_given_be_forever_fp_when_lookup_then_fail() -> None:
    row = {
        "id": "BE-ASK-07",
        "kind": "be_forever_type_fp",
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
    out = decide_be_real_eval(
        compint_decision="PROMOTE (x)",
        shipuse_decision="PROMOTE (x)",
        fastbe_decision="PROMOTE (x)",
        ctxbe_decision="PROMOTE (x)",
        nanogen15_decision="DEFER (x)",
        battery_ok=True,
        claim=BE_REAL_EVAL_CLAIM,
    )
    assert out.startswith("PROMOTE")
    assert nanogen15_outcome_ok("DEFER (x)")


def test_given_gen_claim_when_defer_then_kill() -> None:
    out = decide_be_real_eval(
        compint_decision="PROMOTE (x)",
        shipuse_decision="PROMOTE (x)",
        fastbe_decision="PROMOTE (x)",
        ctxbe_decision="PROMOTE (x)",
        nanogen15_decision="DEFER (x)",
        battery_ok=True,
        claim=BE_REAL_EVAL_CLAIM + " · mini-AGI unlocked",
    )
    assert out.startswith("KILL")


def test_given_battery_fail_when_decide_then_kill() -> None:
    out = decide_be_real_eval(
        compint_decision="PROMOTE (x)",
        shipuse_decision="PROMOTE (x)",
        fastbe_decision="PROMOTE (x)",
        ctxbe_decision="PROMOTE (x)",
        nanogen15_decision="DEFER (x)",
        battery_ok=False,
        claim=BE_REAL_EVAL_CLAIM,
    )
    assert out.startswith("KILL")
    assert "battery" in out.lower()


def test_given_shipuse_missing_when_decide_then_kill() -> None:
    out = decide_be_real_eval(
        compint_decision="PROMOTE (x)",
        shipuse_decision="MISSING",
        fastbe_decision="PROMOTE (x)",
        ctxbe_decision="PROMOTE (x)",
        nanogen15_decision="DEFER (x)",
        battery_ok=True,
        claim=BE_REAL_EVAL_CLAIM,
    )
    assert out.startswith("KILL")
    assert "shipuse" in out.lower()
