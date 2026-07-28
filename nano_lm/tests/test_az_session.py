"""Contract: Wave AZ0 SESSION — freeze held-out/over-refuse/PRODGEN/gen-defer."""

from __future__ import annotations

from ay_session_ops import AY0_INTENT_FP_ROWS
from az_session_ops import (
    AZ0_ANTI_FP,
    AZ0_ASK_BATTERY,
    AZ0_CITED_AY_LOCKS,
    AZ0_GEN_STANCE,
    AZ0_HELDOUT_FP_PROTOCOL,
    AZ0_HELDOUT_FP_ROWS,
    AZ0_ID,
    AZ0_LATENCY_PATHS,
    AZ0_MODES,
    AZ0_NORTH_STAR,
    AZ0_OVERREFUSE_PROTOCOL,
    AZ0_OVERREFUSE_ROWS,
    AZ0_PRODUCT_GEN_CHARTER,
    AZ0_REAL_EVAL_PROTOCOL,
    AZ0_SAFE_NOTE,
    AZ0_SHIP_LOCK,
    AZ0_THESIS,
    AZ0_TRUE_GEN_JUDGE,
    decide_az0_session,
    map_az_product_mode,
)


def test_given_modes_when_map_then_lookup_peak_decode_abstain() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AZ0 — four product modes
    assert map_az_product_mode("WRAP_LOOKUP") == "LOOKUP"
    assert map_az_product_mode("SEMWRAP_LOOKUP") == "LOOKUP"
    assert map_az_product_mode("WRAP_DECODE") == "DECODE"
    assert map_az_product_mode("NO_ANSWER") == "ABSTAIN"
    assert map_az_product_mode("ABSTAIN") == "ABSTAIN"
    assert set(AZ0_LATENCY_PATHS) == AZ0_MODES
    assert "ABSTAIN" in AZ0_MODES


def test_given_product_gen_when_read_then_cites_ay_and_debts() -> None:
    # GIVEN AY locks · WHEN freeze product-gen · THEN cite + 10 debts + bars
    cited = set(AZ0_PRODUCT_GEN_CHARTER["cite_ay_locks"])
    assert cited == AZ0_CITED_AY_LOCKS
    assert "H-PRODINT" in cited
    assert "H-NANOGEN9" in cited
    assert "AY-FREEZE" in cited
    debts = AZ0_PRODUCT_GEN_CHARTER["debts"]
    ids = {d["id"] for d in debts}
    assert {
        "heldout_false_hit_zero",
        "overrefuse_exact_gold",
        "ay_named_intent_hold",
        "hard_natural_hold",
        "false_hit_zero",
        "latency_publish",
        "kb_holes_publish",
        "mode_ui_always",
        "decode_content_law",
        "gen_defer_stance",
    } <= ids
    bars = AZ0_PRODUCT_GEN_CHARTER["bars"]
    assert int(bars["heldout_false_hit_max"]) == 0
    assert int(bars["overrefuse_miss_max"]) == 0
    assert int(bars["named_intent_false_hit_max"]) == 0
    assert float(bars["hard_natural_para_hit_min"]) >= 0.70
    assert int(bars["false_hit_max"]) == 0
    assert int(bars["heldout_fp_min_n"]) >= 12
    assert int(bars["heldout_fp_classes_min"]) >= 3
    assert int(bars["overrefuse_min_n"]) >= 3
    assert bars["decode_gibberish_neq_content_ok"] is True
    assert bars["default_ask_intent_mismatch"] == "ABSTAIN"
    assert bars["default_ask_near_miss"] == "ABSTAIN"
    assert bars["default_ask_exact_gold"] == "LOOKUP"
    assert bars["eval_eq_prod_ask"] is True
    assert bars["named_fh_neq_heldout"] is True
    assert bars["bank_stuff_forbidden"] is True
    assert bars["regression_hold"] is True
    assert set(bars["modes_required"]) == AZ0_MODES
    metrics = set(AZ0_PRODUCT_GEN_CHARTER["metrics"])
    assert {
        "heldout_false_hit",
        "overrefuse_miss",
        "named_intent_false_hit",
        "hard_natural_para_hit",
        "false_hit",
        "decode_content_ok",
        "true_continue_ablated",
    } <= metrics


def test_given_heldout_fp_when_read_then_div_sub_wrong_slot() -> None:
    assert AZ0_HELDOUT_FP_PROTOCOL["held_out"] is True
    assert AZ0_HELDOUT_FP_PROTOCOL["bank_stuff_forbidden"] is True
    assert AZ0_HELDOUT_FP_PROTOCOL["neq_ay_named_intent"] is True
    assert AZ0_HELDOUT_FP_PROTOCOL["intent_mismatch_is_false_hit"] is True
    assert AZ0_HELDOUT_FP_PROTOCOL["wrong_slot_is_false_hit"] is True
    assert AZ0_HELDOUT_FP_PROTOCOL["named_fh_neq_heldout"] is True
    assert AZ0_HELDOUT_FP_PROTOCOL["live_fp_id"] == "AZ-HFP-01"
    assert int(AZ0_HELDOUT_FP_PROTOCOL["min_n"]) >= 12
    assert len(AZ0_HELDOUT_FP_ROWS) >= 12
    ids = [p["id"] for p in AZ0_HELDOUT_FP_ROWS]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("AZ-HFP-") for i in ids)
    assert all(str(p["question"]).strip() for p in AZ0_HELDOUT_FP_ROWS)
    assert all(p["expect_mode"] == "ABSTAIN" for p in AZ0_HELDOUT_FP_ROWS)
    classes = {p["class"] for p in AZ0_HELDOUT_FP_ROWS}
    assert {"ops_div", "ops_sub", "wrong_slot"} <= classes
    ay_q = {str(p["question"]).strip() for p in AY0_INTENT_FP_ROWS}
    az_q = {str(p["question"]).strip() for p in AZ0_HELDOUT_FP_ROWS}
    assert ay_q.isdisjoint(az_q)
    live = AZ0_HELDOUT_FP_ROWS[0]["question"]
    assert "div" in live.lower()


def test_given_overrefuse_when_read_then_exact_clear_lookup() -> None:
    assert AZ0_OVERREFUSE_PROTOCOL["exact_gold_must_lookup"] is True
    assert AZ0_OVERREFUSE_PROTOCOL["overrefuse_is_miss"] is True
    assert AZ0_OVERREFUSE_PROTOCOL["bank_stuff_forbidden"] is True
    assert AZ0_OVERREFUSE_PROTOCOL["live_orf_id"] == "AZ-ORF-01"
    assert int(AZ0_OVERREFUSE_PROTOCOL["min_n"]) >= 3
    assert len(AZ0_OVERREFUSE_ROWS) >= 3
    ids = [p["id"] for p in AZ0_OVERREFUSE_ROWS]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("AZ-ORF-") for i in ids)
    assert all(p["expect_mode"] == "LOOKUP" for p in AZ0_OVERREFUSE_ROWS)
    assert all("clear" in str(p["gold"]) for p in AZ0_OVERREFUSE_ROWS)
    live = AZ0_OVERREFUSE_ROWS[0]["question"].lower()
    assert "clear" in live or "remove all" in live or "empty" in live


def test_given_gen_stance_when_read_then_defer_not_nanogen10_rename() -> None:
    assert AZ0_GEN_STANCE["stance"] == "defer"
    assert "defer" in AZ0_GEN_STANCE["allowed_stances"]
    assert AZ0_GEN_STANCE["capcheck"] == "closed"
    assert AZ0_GEN_STANCE["named_hyp"] == "H-NANOGEN10"
    assert AZ0_GEN_STANCE["named_prod"] == "H-PRODGEN"
    assert AZ0_GEN_STANCE["named_ship"] == "H-SHIPAZ"
    assert AZ0_GEN_STANCE["nanogen10_rename_forbidden"] is True
    assert AZ0_GEN_STANCE["nanogen6_hold_cited"] is True
    assert AZ0_GEN_STANCE["nanogen7_hold_cited"] is True
    assert AZ0_GEN_STANCE["nanogen8_defer_cited"] is True
    assert AZ0_GEN_STANCE["nanogen9_defer_cited"] is True
    rat = str(AZ0_GEN_STANCE["rationale"]).lower()
    assert "defer" in rat
    assert "nanogen" in rat
    judge = AZ0_TRUE_GEN_JUDGE
    assert judge["span_fallback_neq_gen"] is True
    assert judge["nanogen10_rename_forbidden"] is True
    assert judge["nanogen9_defer_archived"] is True
    assert "true_continue" in str(judge["scoring"])


def test_given_real_eval_when_read_then_live_and_nanogen10_gated() -> None:
    assert AZ0_REAL_EVAL_PROTOCOL["live_ask_battery"] is True
    assert AZ0_REAL_EVAL_PROTOCOL["summary_only_forbidden"] is True
    assert AZ0_REAL_EVAL_PROTOCOL["wall_ms_n_new_mandatory"] is True
    assert AZ0_REAL_EVAL_PROTOCOL["eval_eq_prod_ask"] is True
    assert AZ0_REAL_EVAL_PROTOCOL["intent_mismatch_is_false_hit"] is True
    assert AZ0_REAL_EVAL_PROTOCOL["exact_gold_abstain_is_miss"] is True
    assert AZ0_REAL_EVAL_PROTOCOL["gold_substring_neq_gen"] is True
    assert AZ0_REAL_EVAL_PROTOCOL["gibberish_tail_fails"] is True
    assert AZ0_REAL_EVAL_PROTOCOL["span_fallback_neq_gen"] is True
    assert AZ0_REAL_EVAL_PROTOCOL["named_fh_neq_heldout"] is True
    assert AZ0_REAL_EVAL_PROTOCOL[
        "wall_ms_n_new_insufficient_for_decode_quality"
    ] is True
    claim = str(AZ0_REAL_EVAL_PROTOCOL["gen_claim_rule"]).lower()
    assert "nanogen10" in claim
    assert "rename" in claim
    assert "span" in claim or "fallback" in claim


def test_given_battery_when_scan_then_covers_modes_and_debts() -> None:
    assert len(AZ0_ASK_BATTERY) >= 4
    modes = {p["expect_mode"] for p in AZ0_ASK_BATTERY}
    assert modes == AZ0_MODES
    kinds = {p["kind"] for p in AZ0_ASK_BATTERY}
    assert {
        "near_miss",
        "heldout_intent_fp",
        "overrefuse_gold",
        "ay_named_hold",
        "labeled_peak",
        "junk_trap",
        "decode_content",
    } <= kinds
    ids = [p["id"] for p in AZ0_ASK_BATTERY]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("AZ-ASK-") for i in ids)


def test_given_notes_when_read_then_anti_fp_and_north_star() -> None:
    assert "≠" in AZ0_SAFE_NOTE
    assert "LOOKUP" in AZ0_ANTI_FP
    assert "eval path = prod" in AZ0_ANTI_FP.lower()
    assert "NANOGEN10" in AZ0_ANTI_FP or "nanogen10" in AZ0_ANTI_FP.lower()
    assert "≤5M" in AZ0_NORTH_STAR
    assert "defer" in AZ0_NORTH_STAR.lower()
    assert "gibberish-tail" in AZ0_SHIP_LOCK
    assert "TAC" in AZ0_SHIP_LOCK
    assert "PRODGEN" in AZ0_THESIS or "AZ1" in AZ0_THESIS
    assert "defer" in AZ0_THESIS.lower()
    assert "div" in AZ0_THESIS.lower() or "held-out" in AZ0_THESIS.lower()


def test_given_ready_when_decide_then_promote() -> None:
    out = decide_az0_session(trials_dir_ready=True, anti_fp_signed=True)
    assert out.startswith("PROMOTE")
    assert AZ0_ID in out


def test_given_no_trials_when_decide_then_kill() -> None:
    out = decide_az0_session(trials_dir_ready=False, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "trials" in out


def test_given_unsigned_anti_fp_when_decide_then_kill() -> None:
    out = decide_az0_session(trials_dir_ready=True, anti_fp_signed=False)
    assert out.startswith("KILL")
    assert "anti-FP" in out


def test_given_incomplete_battery_when_decide_then_kill() -> None:
    bad = [dict(p) for p in AZ0_ASK_BATTERY if p["expect_mode"] != "PEAK"]
    out = decide_az0_session(
        trials_dir_ready=True, anti_fp_signed=True, battery=bad
    )
    assert out.startswith("KILL")
    assert "battery" in out.lower() or "modes" in out.lower()
