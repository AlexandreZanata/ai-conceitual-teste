"""Contract: Wave AV4 AV-REAL-EVAL — product + live battery; gen if AV3 PROMOTE."""

from __future__ import annotations

from av_real_eval_ops import (
    ASK_BATTERY,
    AV_REAL_EVAL_CLAIM,
    AV_REAL_EVAL_ID,
    AV_REAL_EVAL_THESIS,
    PROTOCOL,
    battery_pass,
    battery_row_ok,
    claim_is_honest,
    decide_av_real_eval,
    gen_claim_allowed,
    mode_matches_expect,
    telemetry_ok,
)


def test_given_contract_when_constants_then_match_av4_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AV4 — product pass · gen if AV3 PROMOTE
    assert AV_REAL_EVAL_ID == "AV-REAL-EVAL"
    assert len(ASK_BATTERY) == 8
    assert PROTOCOL["live_ask_battery"] is True
    assert PROTOCOL["summary_only_forbidden"] is True
    assert PROTOCOL["eval_eq_prod_ask"] is True
    assert PROTOCOL["answer_usability_scored"] is True
    assert PROTOCOL["span_fallback_neq_gen"] is True
    assert PROTOCOL["gibberish_tail_fails"] is True
    claim_rule = str(PROTOCOL["gen_claim_rule"]).lower()
    assert "nanogen6" in claim_rule
    assert "span" in claim_rule or "fallback" in claim_rule
    assert "real eval" in AV_REAL_EVAL_THESIS.lower() or "battery" in (
        AV_REAL_EVAL_THESIS.lower()
    )
    # Default claim = AU STRICT archive — honest under HOLD (no true-continue unlock)
    assert claim_is_honest(AV_REAL_EVAL_CLAIM, nanogen6_decision="HOLD")
    assert not gen_claim_allowed(AV_REAL_EVAL_CLAIM)


def test_given_battery_pack_when_kinds_then_cover_modes() -> None:
    kinds = {p["kind"] for p in ASK_BATTERY}
    assert "known_lookup" in kinds
    assert "ood_abstain" in kinds
    assert "near_miss" in kinds
    assert "labeled_peak" in kinds
    assert "decode_content" in kinds
    assert "junk_trap" in kinds
    assert "human_para" in kinds
    assert "decode_gibberish_bar" in kinds
    modes = {p["expect_mode"] for p in ASK_BATTERY}
    assert modes == {"LOOKUP", "PEAK", "DECODE", "ABSTAIN"}


def test_given_telemetry_when_missing_then_fail() -> None:
    assert not telemetry_ok({"product_mode": "LOOKUP"})
    assert telemetry_ok(
        {"product_mode": "LOOKUP", "wall_ms": 1.0, "n_new": 0}
    )


def test_given_decode_path_when_abstain_junk_then_mode_ok() -> None:
    assert mode_matches_expect(
        product_mode="ABSTAIN",
        expect_mode="DECODE",
        kind="decode_gibberish_bar",
    )
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
        "id": "AV-ASK-01",
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


def test_given_decode_junk_abstain_when_row_then_ok() -> None:
    row = {
        "id": "AV-ASK-08",
        "kind": "decode_gibberish_bar",
        "expect_mode": "DECODE",
        "product_mode": "ABSTAIN",
        "completion": "NO_ANSWER",
        "wall_ms": 12.0,
        "n_new": 8,
        "content_ok": True,
    }
    assert battery_row_ok(row)


def test_given_full_battery_when_pass_then_true() -> None:
    rows = []
    for p in ASK_BATTERY:
        mode = p["expect_mode"]
        if p["kind"] in {"decode_content", "decode_gibberish_bar"}:
            mode = "ABSTAIN"  # honest DECODE-path junk refuse
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


def test_given_product_pass_hold_when_decide_then_promote() -> None:
    out = decide_av_real_eval(
        prodship_decision="PROMOTE",
        shipui2_decision="PROMOTE",
        nanogen6_decision="HOLD",
        battery_ok=True,
        claim=AV_REAL_EVAL_CLAIM,
    )
    assert out == "PROMOTE"


def test_given_true_continue_claim_while_hold_when_decide_then_kill() -> None:
    claim = (
        "AF packaged stack + AQ product layer + true-continue NANOGEN6 "
        "unlocked — not unlabeled open chat LM"
    )
    assert gen_claim_allowed(claim)
    out = decide_av_real_eval(
        prodship_decision="PROMOTE",
        shipui2_decision="PROMOTE",
        nanogen6_decision="HOLD",
        battery_ok=True,
        claim=claim,
    )
    assert out.startswith("KILL")


def test_given_nanogen6_promote_when_decide_then_promote() -> None:
    claim = (
        "AF packaged stack + AQ product layer + AS trust + "
        "true-continue NANOGEN6 — not unlabeled open chat LM"
    )
    out = decide_av_real_eval(
        prodship_decision="PROMOTE",
        shipui2_decision="PROMOTE",
        nanogen6_decision="PROMOTE",
        battery_ok=True,
        claim=claim,
    )
    assert out == "PROMOTE"


def test_given_battery_fail_when_decide_then_kill() -> None:
    out = decide_av_real_eval(
        prodship_decision="PROMOTE",
        shipui2_decision="PROMOTE",
        nanogen6_decision="HOLD",
        battery_ok=False,
        claim=AV_REAL_EVAL_CLAIM,
    )
    assert out.startswith("KILL")
    assert "battery" in out.lower()


def test_given_missing_prodship_when_decide_then_kill() -> None:
    out = decide_av_real_eval(
        prodship_decision="MISSING",
        shipui2_decision="PROMOTE",
        nanogen6_decision="HOLD",
        battery_ok=True,
        claim=AV_REAL_EVAL_CLAIM,
    )
    assert "MISSING" in out


def test_given_near_miss_lookup_when_segwit_bip39_then_refuse() -> None:
    from av_real_eval_ops import force_abstain_row, near_miss_should_abstain

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
