"""Contract: Wave BA0 SESSION — freeze BA-FOREVER/AZ-hold/scoreboard/gen-defer."""

from __future__ import annotations

from az_session_ops import AZ0_HELDOUT_FP_ROWS, AZ0_OVERREFUSE_ROWS
from ba_session_ops import (
    BA0_ANTI_FP,
    BA0_ASK_BATTERY,
    BA0_AZ_HOLD_PROTOCOL,
    BA0_CITED_AZ_LOCKS,
    BA0_CTX_BASELINE,
    BA0_FOREVER_PROTOCOL,
    BA0_FOREVER_ROWS,
    BA0_GEN_STANCE,
    BA0_ID,
    BA0_LATENCY_PATHS,
    BA0_MODES,
    BA0_NORTH_STAR,
    BA0_REAL_EVAL_PROTOCOL,
    BA0_SAFE_NOTE,
    BA0_SCOREBOARD,
    BA0_SHIP_LOCK,
    BA0_SPEED_BASELINE,
    BA0_THESIS,
    BA0_TRUE_GEN_JUDGE,
    decide_ba0_session,
    map_ba_product_mode,
)


def test_given_modes_when_map_then_lookup_peak_decode_abstain() -> None:
    # GIVEN/WHEN/THEN: pesquisa §8 BA0 — four product modes
    assert map_ba_product_mode("WRAP_LOOKUP") == "LOOKUP"
    assert map_ba_product_mode("SEMWRAP_LOOKUP") == "LOOKUP"
    assert map_ba_product_mode("WRAP_DECODE") == "DECODE"
    assert map_ba_product_mode("NO_ANSWER") == "ABSTAIN"
    assert map_ba_product_mode("ABSTAIN") == "ABSTAIN"
    assert set(BA0_LATENCY_PATHS) == BA0_MODES
    assert "ABSTAIN" in BA0_MODES


def test_given_scoreboard_when_read_then_cites_az_and_debts() -> None:
    # GIVEN AZ locks · WHEN freeze scoreboard · THEN cite + 10 debts + bars
    cited = set(BA0_SCOREBOARD["cite_az_locks"])
    assert cited == BA0_CITED_AZ_LOCKS
    assert "H-PRODGEN" in cited
    assert "H-NANOGEN10" in cited
    assert "AZ-FREEZE" in cited
    debts = BA0_SCOREBOARD["debts"]
    ids = {d["id"] for d in debts}
    assert {
        "forever_false_hit_zero",
        "az_hold_zero",
        "overrefuse_exact_gold",
        "live_ask_scoreboard",
        "speed_baseline_publish",
        "ctx_baseline_publish",
        "mode_ui_always",
        "decode_content_law",
        "gen_defer_stance",
        "paraphrase_eval_rule",
    } <= ids
    bars = BA0_SCOREBOARD["bars"]
    assert int(bars["forever_false_hit_max"]) == 0
    assert int(bars["az_hold_false_hit_max"]) == 0
    assert int(bars["overrefuse_miss_max"]) == 0
    assert int(bars["forever_min_n"]) >= 15
    assert int(bars["forever_classes_min"]) >= 5
    assert bars["decode_gibberish_neq_content_ok"] is True
    assert bars["default_ask_intent_mismatch"] == "ABSTAIN"
    assert bars["default_ask_exact_gold"] == "LOOKUP"
    assert bars["eval_eq_prod_ask"] is True
    assert bars["pack_pass_neq_forever"] is True
    assert bars["bank_stuff_forbidden"] is True
    assert bars["paraphrase_required"] is True
    assert bars["regression_hold"] is True
    assert bars["speed_baseline_published"] is True
    assert bars["ctx_baseline_published"] is True
    assert bars["l_eff_alone_forbidden"] is True
    assert set(bars["modes_required"]) == BA0_MODES
    metrics = set(BA0_SCOREBOARD["metrics"])
    assert {
        "forever_false_hit",
        "az_hold_false_hit",
        "overrefuse_miss",
        "ctx_content_ok",
        "true_continue_ablated",
    } <= metrics


def test_given_forever_when_read_then_pow_mod_max_sort_len() -> None:
    assert BA0_FOREVER_PROTOCOL["held_out"] is True
    assert BA0_FOREVER_PROTOCOL["forever"] is True
    assert BA0_FOREVER_PROTOCOL["bank_stuff_forbidden"] is True
    assert BA0_FOREVER_PROTOCOL["paraphrase_required"] is True
    assert BA0_FOREVER_PROTOCOL["neq_az_heldout"] is True
    assert BA0_FOREVER_PROTOCOL["intent_mismatch_is_false_hit"] is True
    assert BA0_FOREVER_PROTOCOL["pack_pass_neq_forever"] is True
    assert BA0_FOREVER_PROTOCOL["live_fp_id"] == "BA-FH-01"
    assert int(BA0_FOREVER_PROTOCOL["min_n"]) >= 15
    assert len(BA0_FOREVER_ROWS) >= 15
    ids = [p["id"] for p in BA0_FOREVER_ROWS]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("BA-FH-") for i in ids)
    assert all(str(p["question"]).strip() for p in BA0_FOREVER_ROWS)
    assert all(p["expect_mode"] == "ABSTAIN" for p in BA0_FOREVER_ROWS)
    classes = {p["class"] for p in BA0_FOREVER_ROWS}
    assert {"ops_pow", "ops_mod", "ops_max", "list_sort", "list_len"} <= classes
    az_q = {str(p["question"]).strip() for p in AZ0_HELDOUT_FP_ROWS}
    az_q |= {str(p["question"]).strip() for p in AZ0_OVERREFUSE_ROWS}
    ba_q = {str(p["question"]).strip() for p in BA0_FOREVER_ROWS}
    assert az_q.isdisjoint(ba_q)
    live = BA0_FOREVER_ROWS[0]["question"]
    assert "pow" in live.lower() or "power" in live.lower()


def test_given_az_hold_when_read_then_regression_bars() -> None:
    assert int(BA0_AZ_HOLD_PROTOCOL["heldout_false_hit_max"]) == 0
    assert int(BA0_AZ_HOLD_PROTOCOL["overrefuse_miss_max"]) == 0
    assert BA0_AZ_HOLD_PROTOCOL["regression_hold"] is True
    assert int(BA0_AZ_HOLD_PROTOCOL["heldout_n"]) >= 12
    assert int(BA0_AZ_HOLD_PROTOCOL["overrefuse_n"]) >= 3
    req = set(BA0_AZ_HOLD_PROTOCOL["required_classes"])
    assert {"ops_div", "ops_sub", "wrong_slot", "exact_clear"} <= req


def test_given_baselines_when_read_then_speed_and_ctx() -> None:
    paths = BA0_SPEED_BASELINE["paths"]
    assert set(paths) == BA0_MODES
    assert BA0_SPEED_BASELINE["quality_regress_forbidden"] is True
    assert BA0_CTX_BASELINE["l_eff_alone_insufficient"] is True
    assert BA0_CTX_BASELINE["content_bars_required"] is True
    assert "CTXREAL2" in str(BA0_CTX_BASELINE["ba3_gate"])


def test_given_gen_stance_when_read_then_defer_not_nanogen11_rename() -> None:
    assert BA0_GEN_STANCE["stance"] == "defer"
    assert set(BA0_GEN_STANCE["allowed_stances"]) == {"M1", "M2", "M3", "defer"}
    assert BA0_GEN_STANCE["capcheck"] == "closed"
    assert BA0_GEN_STANCE["named_hyp"] == "H-NANOGEN11"
    assert BA0_GEN_STANCE["named_realgain"] == "H-REALGAIN"
    assert BA0_GEN_STANCE["named_fast"] == "H-FASTREAL"
    assert BA0_GEN_STANCE["named_ctx"] == "H-CTXREAL2"
    assert BA0_GEN_STANCE["nanogen11_rename_forbidden"] is True
    assert BA0_GEN_STANCE["nanogen6_hold_cited"] is True
    assert BA0_GEN_STANCE["nanogen7_hold_cited"] is True
    assert BA0_GEN_STANCE["nanogen8_defer_cited"] is True
    assert BA0_GEN_STANCE["nanogen9_defer_cited"] is True
    assert BA0_GEN_STANCE["nanogen10_defer_cited"] is True
    methods = BA0_GEN_STANCE["method_candidates"]
    assert set(methods) == {"M1", "M2", "M3"}
    rat = str(BA0_GEN_STANCE["rationale"]).lower()
    assert "defer" in rat
    assert "nanogen" in rat
    judge = BA0_TRUE_GEN_JUDGE
    assert judge["span_fallback_neq_gen"] is True
    assert judge["nanogen11_rename_forbidden"] is True
    assert judge["nanogen10_defer_archived"] is True
    assert "true_continue" in str(judge["scoring"])


def test_given_real_eval_when_read_then_live_and_nanogen11_gated() -> None:
    assert BA0_REAL_EVAL_PROTOCOL["live_ask_battery"] is True
    assert BA0_REAL_EVAL_PROTOCOL["summary_only_forbidden"] is True
    assert BA0_REAL_EVAL_PROTOCOL["wall_ms_n_new_mandatory"] is True
    assert BA0_REAL_EVAL_PROTOCOL["eval_eq_prod_ask"] is True
    assert BA0_REAL_EVAL_PROTOCOL["intent_mismatch_is_false_hit"] is True
    assert BA0_REAL_EVAL_PROTOCOL["exact_gold_abstain_is_miss"] is True
    assert BA0_REAL_EVAL_PROTOCOL["gold_substring_neq_gen"] is True
    assert BA0_REAL_EVAL_PROTOCOL["gibberish_tail_fails"] is True
    assert BA0_REAL_EVAL_PROTOCOL["span_fallback_neq_gen"] is True
    assert BA0_REAL_EVAL_PROTOCOL["pack_pass_neq_forever"] is True
    assert {
        "OK",
        "FP",
        "MISS",
        "ABSTAIN-OK",
    } <= set(BA0_REAL_EVAL_PROTOCOL["score_labels"])
    claim = str(BA0_REAL_EVAL_PROTOCOL["gen_claim_rule"]).lower()
    assert "nanogen11" in claim
    assert "rename" in claim


def test_given_battery_when_scan_then_covers_modes_and_debts() -> None:
    assert len(BA0_ASK_BATTERY) >= 4
    modes = {p["expect_mode"] for p in BA0_ASK_BATTERY}
    assert modes == BA0_MODES
    kinds = {p["kind"] for p in BA0_ASK_BATTERY}
    assert {
        "near_miss",
        "forever_intent_fp",
        "forever_list_fp",
        "overrefuse_gold",
        "az_hold_div",
        "labeled_peak",
        "junk_trap",
        "decode_content",
    } <= kinds
    ids = [p["id"] for p in BA0_ASK_BATTERY]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("BA-ASK-") for i in ids)


def test_given_notes_when_read_then_anti_fp_and_north_star() -> None:
    assert "≠" in BA0_SAFE_NOTE
    assert "LOOKUP" in BA0_ANTI_FP
    assert "eval path = prod" in BA0_ANTI_FP.lower()
    assert "NANOGEN11" in BA0_ANTI_FP or "nanogen11" in BA0_ANTI_FP.lower()
    assert "≤5M" in BA0_NORTH_STAR
    assert "defer" in BA0_NORTH_STAR.lower()
    assert "gibberish-tail" in BA0_SHIP_LOCK
    assert "TAC" in BA0_SHIP_LOCK
    assert "REALGAIN" in BA0_THESIS or "BA1" in BA0_THESIS
    assert "defer" in BA0_THESIS.lower()
    assert "forever" in BA0_THESIS.lower() or "pow" in BA0_THESIS.lower()


def test_given_ready_when_decide_then_promote() -> None:
    out = decide_ba0_session(trials_dir_ready=True, anti_fp_signed=True)
    assert out.startswith("PROMOTE")
    assert BA0_ID in out


def test_given_no_trials_when_decide_then_kill() -> None:
    out = decide_ba0_session(trials_dir_ready=False, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "trials" in out


def test_given_unsigned_anti_fp_when_decide_then_kill() -> None:
    out = decide_ba0_session(trials_dir_ready=True, anti_fp_signed=False)
    assert out.startswith("KILL")
    assert "anti-FP" in out


def test_given_incomplete_battery_when_decide_then_kill() -> None:
    bad = [dict(p) for p in BA0_ASK_BATTERY if p["expect_mode"] != "PEAK"]
    out = decide_ba0_session(
        trials_dir_ready=True, anti_fp_signed=True, battery=bad
    )
    assert out.startswith("KILL")
    assert "battery" in out.lower() or "modes" in out.lower()
