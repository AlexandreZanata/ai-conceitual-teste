"""Contract: Wave AT4 AT-REAL-EVAL — product + gen + live battery."""

from __future__ import annotations

from real_eval_ops import (
    ASK_BATTERY,
    PARENT_NANOGEN4_ABLATED,
    PROTOCOL,
    REAL_EVAL_CLAIM,
    REAL_EVAL_ID,
    REAL_EVAL_THESIS,
    battery_pass,
    battery_row_ok,
    claim_is_honest,
    decide_at_real_eval,
    gen_claim_allowed,
    telemetry_ok,
)


def test_given_contract_when_constants_then_match_at4_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AT4 — product pass · gen if AT3 PROMOTE
    assert REAL_EVAL_ID == "AT-REAL-EVAL"
    assert len(ASK_BATTERY) == 6
    assert PARENT_NANOGEN4_ABLATED == 5.5
    assert PROTOCOL["live_ask_battery"] is True
    assert PROTOCOL["summary_only_forbidden"] is True
    assert "real eval" in REAL_EVAL_THESIS.lower() or "battery" in (
        REAL_EVAL_THESIS.lower()
    )
    assert claim_is_honest(
        REAL_EVAL_CLAIM, nanogen4_decision="PROMOTE"
    )
    assert gen_claim_allowed(REAL_EVAL_CLAIM)


def test_given_battery_pack_when_kinds_then_cover_modes() -> None:
    kinds = {p["kind"] for p in ASK_BATTERY}
    assert "known_lookup" in kinds
    assert "ood_abstain" in kinds
    assert "labeled_peak" in kinds
    assert "decode_smoke" in kinds
    assert "junk_trap" in kinds
    modes = {p["expect_mode"] for p in ASK_BATTERY}
    assert modes == {"LOOKUP", "PEAK", "DECODE", "ABSTAIN"}


def test_given_telemetry_when_missing_then_fail() -> None:
    assert not telemetry_ok({"product_mode": "LOOKUP"})
    assert telemetry_ok(
        {"product_mode": "LOOKUP", "wall_ms": 1.0, "n_new": 0}
    )


def test_given_row_when_mode_match_then_ok() -> None:
    row = {
        "id": "AT-ASK-01",
        "expect_mode": "LOOKUP",
        "product_mode": "LOOKUP",
        "wall_ms": 1.0,
        "n_new": 0,
    }
    assert battery_row_ok(row)
    row["product_mode"] = "DECODE"
    assert not battery_row_ok(row)


def test_given_full_battery_when_pass_then_true() -> None:
    rows = []
    for p in ASK_BATTERY:
        rows.append(
            {
                "id": p["id"],
                "expect_mode": p["expect_mode"],
                "product_mode": p["expect_mode"],
                "wall_ms": 1.0,
                "n_new": 0,
            }
        )
    assert battery_pass(rows)


def test_given_all_promote_when_decide_then_promote() -> None:
    out = decide_at_real_eval(
        prodreg_decision="PROMOTE",
        shipapp_decision="PROMOTE",
        nanogen4_decision="PROMOTE",
        battery_ok=True,
        claim=REAL_EVAL_CLAIM,
    )
    assert out == "PROMOTE"


def test_given_battery_fail_when_decide_then_kill() -> None:
    out = decide_at_real_eval(
        prodreg_decision="PROMOTE",
        shipapp_decision="PROMOTE",
        nanogen4_decision="PROMOTE",
        battery_ok=False,
        claim=REAL_EVAL_CLAIM,
    )
    assert out.startswith("KILL")
    assert "battery" in out.lower()


def test_given_gen_claim_while_hold_when_decide_then_kill() -> None:
    out = decide_at_real_eval(
        prodreg_decision="PROMOTE",
        shipapp_decision="PROMOTE",
        nanogen4_decision="HOLD",
        battery_ok=True,
        claim=REAL_EVAL_CLAIM,
    )
    assert out.startswith("KILL")


def test_given_hold_product_claim_when_decide_then_promote() -> None:
    claim = (
        "AF packaged stack + AQ product layer + AS trust path — "
        "not open chat LM"
    )
    assert claim_is_honest(claim, nanogen4_decision="HOLD")
    out = decide_at_real_eval(
        prodreg_decision="PROMOTE",
        shipapp_decision="PROMOTE",
        nanogen4_decision="HOLD",
        battery_ok=True,
        claim=claim,
    )
    assert out == "PROMOTE"


def test_given_near_miss_lookup_when_segwit_bip39_then_refuse() -> None:
    from real_eval_ops import force_abstain_row, near_miss_should_abstain

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

    out = decide_at_real_eval(
        prodreg_decision="MISSING",
        shipapp_decision="PROMOTE",
        nanogen4_decision="PROMOTE",
        battery_ok=True,
        claim=REAL_EVAL_CLAIM,
    )
    assert "MISSING" in out
