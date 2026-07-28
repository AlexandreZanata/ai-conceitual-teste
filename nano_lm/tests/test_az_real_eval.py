"""Contract: Wave AZ4 AZ-REAL-EVAL — product pass + live battery; gen if AZ3 PROMOTE."""

from __future__ import annotations

from az_real_eval_ops import (
    ASK_BATTERY,
    AZ_REAL_EVAL_CLAIM,
    AZ_REAL_EVAL_ID,
    AZ_REAL_EVAL_THESIS,
    PARENT_NANOGEN10,
    PROTOCOL,
    battery_pass,
    battery_row_ok,
    claim_is_honest,
    decide_az_real_eval,
    gen_claim_allowed,
    mode_matches_expect,
    nanogen10_outcome_ok,
    telemetry_ok,
)


def test_given_contract_when_constants_then_match_az4_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AZ4 — product pass · gen if AZ3 PROMOTE
    assert AZ_REAL_EVAL_ID == "AZ-REAL-EVAL"
    assert len(ASK_BATTERY) >= 8
    assert PROTOCOL["live_ask_battery"] is True
    assert PROTOCOL["summary_only_forbidden"] is True
    assert PROTOCOL["eval_eq_prod_ask"] is True
    assert PROTOCOL["answer_usability_scored"] is True
    assert PROTOCOL["span_fallback_neq_gen"] is True
    assert PROTOCOL["gibberish_tail_fails"] is True
    assert PROTOCOL["intent_mismatch_is_false_hit"] is True
    assert PROTOCOL["exact_gold_abstain_is_miss"] is True
    claim_rule = str(PROTOCOL["gen_claim_rule"]).lower()
    assert "nanogen10" in claim_rule
    assert "true_continue" in claim_rule or "true-continue" in claim_rule
    assert "rename" in claim_rule
    assert "real eval" in AZ_REAL_EVAL_THESIS.lower()
    assert "PRODGEN" in AZ_REAL_EVAL_THESIS
    assert "SHIPAZ" in AZ_REAL_EVAL_THESIS
    assert PARENT_NANOGEN10 == "DEFER"
    assert claim_is_honest(AZ_REAL_EVAL_CLAIM, nanogen10_decision="DEFER")
    assert not gen_claim_allowed(AZ_REAL_EVAL_CLAIM)


def test_given_battery_pack_when_kinds_then_cover_modes() -> None:
    kinds = {p["kind"] for p in ASK_BATTERY}
    assert "known_lookup" in kinds
    assert "ood_abstain" in kinds
    assert "near_miss" in kinds
    assert "labeled_peak" in kinds
    assert "decode_content" in kinds
    assert "junk_trap" in kinds
    assert "heldout_intent_fp" in kinds
    assert "overrefuse_gold" in kinds
    assert "ay_named_hold" in kinds
    modes = {p["expect_mode"] for p in ASK_BATTERY}
    assert modes == {"LOOKUP", "PEAK", "DECODE", "ABSTAIN"}
    assert all(str(p["id"]).startswith("AZ-ASK-") for p in ASK_BATTERY)


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
    assert not mode_matches_expect(
        product_mode="LOOKUP",
        expect_mode="DECODE",
        kind="decode_content",
    )


def test_given_row_when_mode_and_content_then_ok() -> None:
    row = {
        "id": "AZ-ASK-01",
        "kind": "known_lookup",
        "expect_mode": "LOOKUP",
        "product_mode": "LOOKUP",
        "completion": "def add(a, b): return a + b",
        "wall_ms": 1.0,
        "n_new": 0,
        "content_ok": True,
    }
    assert battery_row_ok(row)
    row["content_ok"] = False
    assert not battery_row_ok(row)


def test_given_heldout_fp_when_lookup_then_fail() -> None:
    row = {
        "id": "AZ-ASK-07",
        "kind": "heldout_intent_fp",
        "expect_mode": "ABSTAIN",
        "product_mode": "LOOKUP",
        "completion": "def add(a, b): return a + b",
        "wall_ms": 1.0,
        "n_new": 0,
        "content_ok": True,
    }
    assert not battery_row_ok(row)


def test_given_overrefuse_when_abstain_then_fail() -> None:
    row = {
        "id": "AZ-ASK-08",
        "kind": "overrefuse_gold",
        "expect_mode": "LOOKUP",
        "product_mode": "ABSTAIN",
        "completion": "NO_ANSWER",
        "wall_ms": 1.0,
        "n_new": 0,
        "content_ok": True,
    }
    assert not battery_row_ok(row)


def test_given_full_battery_when_pass_then_true() -> None:
    rows = []
    for p in ASK_BATTERY:
        mode = p["expect_mode"]
        if p["kind"] in {"decode_content", "decode_gibberish_bar"}:
            mode = "ABSTAIN"
        rows.append(
            {
                "id": p["id"],
                "kind": p["kind"],
                "expect_mode": p["expect_mode"],
                "product_mode": mode,
                "completion": (
                    "NO_ANSWER"
                    if mode == "ABSTAIN"
                    else "usable span answer here"
                ),
                "wall_ms": 1.0,
                "n_new": 0,
                "content_ok": True,
            }
        )
    assert battery_pass(rows)


def test_given_product_pass_defer_when_decide_then_promote() -> None:
    out = decide_az_real_eval(
        prodgen_decision="PROMOTE",
        shipaz_decision="PROMOTE",
        nanogen10_decision="DEFER",
        battery_ok=True,
        claim=AZ_REAL_EVAL_CLAIM,
    )
    assert out == "PROMOTE"


def test_given_true_continue_claim_while_defer_when_decide_then_kill() -> None:
    claim = (
        "AF packaged stack + AQ product layer + true-continue NANOGEN10 "
        "unlocked — not unlabeled open chat LM"
    )
    assert gen_claim_allowed(claim)
    out = decide_az_real_eval(
        prodgen_decision="PROMOTE",
        shipaz_decision="PROMOTE",
        nanogen10_decision="DEFER",
        battery_ok=True,
        claim=claim,
    )
    assert out.startswith("KILL")


def test_given_nanogen10_promote_when_decide_then_promote() -> None:
    claim = (
        "AF packaged stack + AQ product layer + AS trust + "
        "true-continue NANOGEN10 — not unlabeled open chat LM"
    )
    out = decide_az_real_eval(
        prodgen_decision="PROMOTE",
        shipaz_decision="PROMOTE",
        nanogen10_decision="PROMOTE",
        battery_ok=True,
        claim=claim,
    )
    assert out == "PROMOTE"


def test_given_battery_fail_when_decide_then_kill() -> None:
    out = decide_az_real_eval(
        prodgen_decision="PROMOTE",
        shipaz_decision="PROMOTE",
        nanogen10_decision="DEFER",
        battery_ok=False,
        claim=AZ_REAL_EVAL_CLAIM,
    )
    assert out.startswith("KILL")
    assert "battery" in out.lower()


def test_given_missing_prodgen_when_decide_then_kill() -> None:
    out = decide_az_real_eval(
        prodgen_decision="MISSING",
        shipaz_decision="PROMOTE",
        nanogen10_decision="DEFER",
        battery_ok=True,
        claim=AZ_REAL_EVAL_CLAIM,
    )
    assert "MISSING" in out


def test_given_nanogen10_outcomes_when_check_then_ok() -> None:
    assert nanogen10_outcome_ok("DEFER")
    assert nanogen10_outcome_ok("HOLD")
    assert nanogen10_outcome_ok("PROMOTE")
    assert not nanogen10_outcome_ok("MISSING")
    assert not nanogen10_outcome_ok("KILL (x)")


def test_given_near_miss_lookup_when_segwit_bip39_then_refuse() -> None:
    from az_real_eval_ops import force_abstain_row, near_miss_should_abstain

    q = (
        "BIP-39 entropy formula is CS = ENT / 32 — confirm for "
        "SegWit witness discount?"
    )
    assert near_miss_should_abstain(
        question=q,
        completion="CS = ENT / 32",
        product_mode="LOOKUP",
    )
    forced = force_abstain_row(
        {
            "product_mode": "LOOKUP",
            "completion": "CS = ENT / 32",
            "mode": "SEMWRAP_LOOKUP",
            "wall_ms": 1.0,
            "n_new": 0,
        }
    )
    assert forced["product_mode"] == "ABSTAIN"
    assert forced["completion"] == "NO_ANSWER"
