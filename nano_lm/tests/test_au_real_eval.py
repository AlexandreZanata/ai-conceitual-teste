"""Contract: Wave AU4 AU-REAL-EVAL — product + STRICT gen + live battery."""

from __future__ import annotations

from au_real_eval_ops import (
    ASK_BATTERY,
    AU_REAL_EVAL_CLAIM,
    AU_REAL_EVAL_ID,
    AU_REAL_EVAL_THESIS,
    PARENT_NANOGEN5_STRICT,
    PROTOCOL,
    battery_pass,
    battery_row_ok,
    claim_is_honest,
    decide_au_real_eval,
    gen_claim_allowed,
    telemetry_ok,
)


def test_given_contract_when_constants_then_match_au4_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AU4 — product pass · gen if AU3 PROMOTE
    assert AU_REAL_EVAL_ID == "AU-REAL-EVAL"
    assert len(ASK_BATTERY) == 7
    assert PARENT_NANOGEN5_STRICT == 5.5
    assert PROTOCOL["live_ask_battery"] is True
    assert PROTOCOL["summary_only_forbidden"] is True
    assert PROTOCOL["eval_eq_prod_ask"] is True
    assert PROTOCOL["answer_usability_scored"] is True
    assert PROTOCOL["gibberish_tail_fails"] is True
    assert "nanogen5" in str(PROTOCOL["gen_claim_rule"]).lower()
    assert "real eval" in AU_REAL_EVAL_THESIS.lower() or "battery" in (
        AU_REAL_EVAL_THESIS.lower()
    )
    assert claim_is_honest(
        AU_REAL_EVAL_CLAIM, nanogen5_decision="PROMOTE"
    )
    assert gen_claim_allowed(AU_REAL_EVAL_CLAIM)


def test_given_battery_pack_when_kinds_then_cover_modes() -> None:
    kinds = {p["kind"] for p in ASK_BATTERY}
    assert "known_lookup" in kinds
    assert "ood_abstain" in kinds
    assert "near_miss" in kinds
    assert "labeled_peak" in kinds
    assert "decode_smoke" in kinds
    assert "junk_trap" in kinds
    assert "human_para" in kinds
    modes = {p["expect_mode"] for p in ASK_BATTERY}
    assert modes == {"LOOKUP", "PEAK", "DECODE", "ABSTAIN"}


def test_given_telemetry_when_missing_then_fail() -> None:
    assert not telemetry_ok({"product_mode": "LOOKUP"})
    assert telemetry_ok(
        {"product_mode": "LOOKUP", "wall_ms": 1.0, "n_new": 0}
    )


def test_given_row_when_mode_and_content_then_ok() -> None:
    row = {
        "id": "AU-ASK-01",
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


def test_given_full_battery_when_pass_then_true() -> None:
    rows = []
    for p in ASK_BATTERY:
        rows.append(
            {
                "id": p["id"],
                "expect_mode": p["expect_mode"],
                "product_mode": p["expect_mode"],
                "completion": (
                    "NO_ANSWER"
                    if p["expect_mode"] == "ABSTAIN"
                    else "usable span answer here"
                ),
                "wall_ms": 1.0,
                "n_new": 0,
                "content_ok": True,
            }
        )
    assert battery_pass(rows)


def test_given_all_promote_when_decide_then_promote() -> None:
    out = decide_au_real_eval(
        prodhard_decision="PROMOTE",
        shipreal_decision="PROMOTE",
        nanogen5_decision="PROMOTE",
        battery_ok=True,
        claim=AU_REAL_EVAL_CLAIM,
    )
    assert out == "PROMOTE"


def test_given_battery_fail_when_decide_then_kill() -> None:
    out = decide_au_real_eval(
        prodhard_decision="PROMOTE",
        shipreal_decision="PROMOTE",
        nanogen5_decision="PROMOTE",
        battery_ok=False,
        claim=AU_REAL_EVAL_CLAIM,
    )
    assert out.startswith("KILL")
    assert "battery" in out.lower()


def test_given_gen_claim_while_hold_when_decide_then_kill() -> None:
    out = decide_au_real_eval(
        prodhard_decision="PROMOTE",
        shipreal_decision="PROMOTE",
        nanogen5_decision="HOLD",
        battery_ok=True,
        claim=AU_REAL_EVAL_CLAIM,
    )
    assert out.startswith("KILL")


def test_given_hold_product_claim_when_decide_then_promote() -> None:
    claim = (
        "AF packaged stack + AQ product layer + AS trust path — "
        "not open chat LM"
    )
    assert claim_is_honest(claim, nanogen5_decision="HOLD")
    out = decide_au_real_eval(
        prodhard_decision="PROMOTE",
        shipreal_decision="PROMOTE",
        nanogen5_decision="HOLD",
        battery_ok=True,
        claim=claim,
    )
    assert out == "PROMOTE"


def test_given_near_miss_lookup_when_segwit_bip39_then_refuse() -> None:
    from au_real_eval_ops import force_abstain_row, near_miss_should_abstain

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

    out = decide_au_real_eval(
        prodhard_decision="MISSING",
        shipreal_decision="PROMOTE",
        nanogen5_decision="PROMOTE",
        battery_ok=True,
        claim=AU_REAL_EVAL_CLAIM,
    )
    assert "MISSING" in out
