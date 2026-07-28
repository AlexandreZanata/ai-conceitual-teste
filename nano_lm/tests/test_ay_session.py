"""Contract: Wave AY0 SESSION — freeze intent-FP/PRODINT/gen-defer/eval."""

from __future__ import annotations

from ax_session_ops import AX0_HARD_NATURAL_ROWS
from ay_session_ops import (
    AY0_ANTI_FP,
    AY0_ASK_BATTERY,
    AY0_CITED_AX_LOCKS,
    AY0_GEN_STANCE,
    AY0_ID,
    AY0_INTENT_FP_PROTOCOL,
    AY0_INTENT_FP_ROWS,
    AY0_LATENCY_PATHS,
    AY0_MODES,
    AY0_NORTH_STAR,
    AY0_PRODUCT_INT_CHARTER,
    AY0_REAL_EVAL_PROTOCOL,
    AY0_SAFE_NOTE,
    AY0_SHIP_LOCK,
    AY0_THESIS,
    AY0_TRUE_GEN_JUDGE,
    decide_ay0_session,
    map_ay_product_mode,
)


def test_given_modes_when_map_then_lookup_peak_decode_abstain() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AY0 — four product modes
    assert map_ay_product_mode("WRAP_LOOKUP") == "LOOKUP"
    assert map_ay_product_mode("SEMWRAP_LOOKUP") == "LOOKUP"
    assert map_ay_product_mode("WRAP_DECODE") == "DECODE"
    assert map_ay_product_mode("NO_ANSWER") == "ABSTAIN"
    assert map_ay_product_mode("ABSTAIN") == "ABSTAIN"
    assert set(AY0_LATENCY_PATHS) == AY0_MODES
    assert "ABSTAIN" in AY0_MODES


def test_given_product_int_when_read_then_cites_ax_and_debts() -> None:
    # GIVEN AX locks · WHEN freeze product-int · THEN cite + 8 debts + bars
    cited = set(AY0_PRODUCT_INT_CHARTER["cite_ax_locks"])
    assert cited == AY0_CITED_AX_LOCKS
    assert "H-PRODNAT" in cited
    assert "H-NANOGEN8" in cited
    assert "AX-FREEZE" in cited
    debts = AY0_PRODUCT_INT_CHARTER["debts"]
    ids = {d["id"] for d in debts}
    assert {
        "intent_false_hit_zero",
        "hard_natural_hold",
        "false_hit_zero",
        "latency_publish",
        "kb_holes_publish",
        "mode_ui_always",
        "decode_content_law",
        "gen_defer_stance",
    } <= ids
    bars = AY0_PRODUCT_INT_CHARTER["bars"]
    assert int(bars["intent_false_hit_max"]) == 0
    assert float(bars["hard_natural_para_hit_min"]) >= 0.70
    assert int(bars["false_hit_max"]) == 0
    assert int(bars["intent_fp_min_n"]) >= 12
    assert int(bars["intent_fp_classes_min"]) >= 4
    assert bars["decode_gibberish_neq_content_ok"] is True
    assert bars["default_ask_intent_mismatch"] == "ABSTAIN"
    assert bars["default_ask_near_miss"] == "ABSTAIN"
    assert bars["eval_eq_prod_ask"] is True
    assert bars["pack_fh_neq_live_intent"] is True
    assert bars["bank_stuff_forbidden"] is True
    assert bars["regression_hold"] is True
    assert set(bars["modes_required"]) == AY0_MODES
    metrics = set(AY0_PRODUCT_INT_CHARTER["metrics"])
    assert {
        "intent_false_hit",
        "hard_natural_para_hit",
        "false_hit",
        "decode_content_ok",
        "true_continue_ablated",
    } <= metrics


def test_given_intent_fp_when_read_then_held_out_four_classes() -> None:
    assert AY0_INTENT_FP_PROTOCOL["held_out"] is True
    assert AY0_INTENT_FP_PROTOCOL["bank_stuff_forbidden"] is True
    assert AY0_INTENT_FP_PROTOCOL["neq_ax_hard_natural"] is True
    assert AY0_INTENT_FP_PROTOCOL["intent_mismatch_is_false_hit"] is True
    assert AY0_INTENT_FP_PROTOCOL["pack_fh_neq_live_intent"] is True
    assert AY0_INTENT_FP_PROTOCOL["live_fp_id"] == "AY-IFP-01"
    assert int(AY0_INTENT_FP_PROTOCOL["min_n"]) >= 12
    assert len(AY0_INTENT_FP_ROWS) >= 12
    ids = [p["id"] for p in AY0_INTENT_FP_ROWS]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("AY-IFP-") for i in ids)
    assert all(str(p["question"]).strip() for p in AY0_INTENT_FP_ROWS)
    assert all(p["expect_mode"] == "ABSTAIN" for p in AY0_INTENT_FP_ROWS)
    classes = {p["class"] for p in AY0_INTENT_FP_ROWS}
    assert {
        "predicate_swap",
        "antonym",
        "false_friend",
        "half_known",
    } <= classes
    ax_q = {str(p["question"]).strip() for p in AX0_HARD_NATURAL_ROWS}
    ay_q = {str(p["question"]).strip() for p in AY0_INTENT_FP_ROWS}
    assert ax_q.isdisjoint(ay_q)
    live = AY0_INTENT_FP_ROWS[0]["question"]
    assert "mul" in live.lower()
    assert "product" in live.lower() or "a*b" in live.lower() or "multiply" in live.lower()


def test_given_gen_stance_when_read_then_defer_not_nanogen9_rename() -> None:
    assert AY0_GEN_STANCE["stance"] == "defer"
    assert "defer" in AY0_GEN_STANCE["allowed_stances"]
    assert AY0_GEN_STANCE["capcheck"] == "closed"
    assert AY0_GEN_STANCE["named_hyp"] == "H-NANOGEN9"
    assert AY0_GEN_STANCE["nanogen9_rename_forbidden"] is True
    assert AY0_GEN_STANCE["nanogen6_hold_cited"] is True
    assert AY0_GEN_STANCE["nanogen7_hold_cited"] is True
    assert AY0_GEN_STANCE["nanogen8_defer_cited"] is True
    rat = str(AY0_GEN_STANCE["rationale"]).lower()
    assert "defer" in rat
    assert "nanogen" in rat
    judge = AY0_TRUE_GEN_JUDGE
    assert judge["span_fallback_neq_gen"] is True
    assert judge["nanogen9_rename_forbidden"] is True
    assert judge["nanogen8_defer_archived"] is True
    assert "true_continue" in str(judge["scoring"])


def test_given_real_eval_when_read_then_live_and_nanogen9_gated() -> None:
    assert AY0_REAL_EVAL_PROTOCOL["live_ask_battery"] is True
    assert AY0_REAL_EVAL_PROTOCOL["summary_only_forbidden"] is True
    assert AY0_REAL_EVAL_PROTOCOL["wall_ms_n_new_mandatory"] is True
    assert AY0_REAL_EVAL_PROTOCOL["eval_eq_prod_ask"] is True
    assert AY0_REAL_EVAL_PROTOCOL["intent_mismatch_is_false_hit"] is True
    assert AY0_REAL_EVAL_PROTOCOL["gold_substring_neq_gen"] is True
    assert AY0_REAL_EVAL_PROTOCOL["gibberish_tail_fails"] is True
    assert AY0_REAL_EVAL_PROTOCOL["span_fallback_neq_gen"] is True
    assert AY0_REAL_EVAL_PROTOCOL["pack_fh_neq_live_intent"] is True
    assert AY0_REAL_EVAL_PROTOCOL[
        "wall_ms_n_new_insufficient_for_decode_quality"
    ] is True
    claim = str(AY0_REAL_EVAL_PROTOCOL["gen_claim_rule"]).lower()
    assert "nanogen9" in claim
    assert "rename" in claim
    assert "span" in claim or "fallback" in claim


def test_given_battery_when_scan_then_covers_modes_and_debts() -> None:
    assert len(AY0_ASK_BATTERY) >= 4
    modes = {p["expect_mode"] for p in AY0_ASK_BATTERY}
    assert modes == AY0_MODES
    kinds = {p["kind"] for p in AY0_ASK_BATTERY}
    assert {
        "near_miss",
        "intent_fp",
        "hard_natural_hold",
        "labeled_peak",
        "junk_trap",
        "decode_content",
    } <= kinds
    ids = [p["id"] for p in AY0_ASK_BATTERY]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("AY-ASK-") for i in ids)


def test_given_notes_when_read_then_anti_fp_and_north_star() -> None:
    assert "≠" in AY0_SAFE_NOTE
    assert "intent" in AY0_SAFE_NOTE.lower()
    assert "LOOKUP" in AY0_ANTI_FP
    assert "eval path = prod" in AY0_ANTI_FP.lower()
    assert "intent" in AY0_ANTI_FP.lower()
    assert "NANOGEN9" in AY0_ANTI_FP or "nanogen9" in AY0_ANTI_FP.lower()
    assert "≤5M" in AY0_NORTH_STAR
    assert "defer" in AY0_NORTH_STAR.lower()
    assert "gibberish-tail" in AY0_SHIP_LOCK
    assert "TAC" in AY0_SHIP_LOCK
    assert "PRODINT" in AY0_THESIS or "AY1" in AY0_THESIS
    assert "defer" in AY0_THESIS.lower()
    assert "intent" in AY0_THESIS.lower()


def test_given_ready_when_decide_then_promote() -> None:
    out = decide_ay0_session(trials_dir_ready=True, anti_fp_signed=True)
    assert out.startswith("PROMOTE")
    assert AY0_ID in out


def test_given_no_trials_when_decide_then_kill() -> None:
    out = decide_ay0_session(trials_dir_ready=False, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "trials" in out


def test_given_unsigned_anti_fp_when_decide_then_kill() -> None:
    out = decide_ay0_session(trials_dir_ready=True, anti_fp_signed=False)
    assert out.startswith("KILL")
    assert "anti-FP" in out


def test_given_incomplete_battery_when_decide_then_kill() -> None:
    bad = [dict(p) for p in AY0_ASK_BATTERY if p["expect_mode"] != "PEAK"]
    out = decide_ay0_session(
        trials_dir_ready=True, anti_fp_signed=True, battery=bad
    )
    assert out.startswith("KILL")
    assert "battery" in out.lower() or "modes" in out.lower()
