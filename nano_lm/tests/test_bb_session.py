"""Contract: Wave BB0 SESSION — freeze BB-FOREVER/BA-hold/scoreboard/gen-defer."""

from __future__ import annotations

from az_session_ops import AZ0_HELDOUT_FP_ROWS, AZ0_OVERREFUSE_ROWS
from ba_session_ops import BA0_FOREVER_ROWS
from bb_session_ops import (
    BB0_ANTI_FP,
    BB0_ASK_BATTERY,
    BB0_AZ_HOLD_PROTOCOL,
    BB0_BA_HOLD_PROTOCOL,
    BB0_CITED_BA_LOCKS,
    BB0_CTX_BASELINE,
    BB0_FOREVER_PROTOCOL,
    BB0_FOREVER_ROWS,
    BB0_GEN_STANCE,
    BB0_ID,
    BB0_LATENCY_PATHS,
    BB0_MODES,
    BB0_NORTH_STAR,
    BB0_REAL_EVAL_PROTOCOL,
    BB0_SAFE_NOTE,
    BB0_SCOREBOARD,
    BB0_SHIP_LOCK,
    BB0_SPEED_BASELINE,
    BB0_THESIS,
    BB0_TRUE_GEN_JUDGE,
    decide_bb0_session,
    map_bb_product_mode,
)


def test_given_modes_when_map_then_lookup_peak_decode_abstain() -> None:
    # GIVEN/WHEN/THEN: pesquisa §8 BB0 — four product modes
    assert map_bb_product_mode("WRAP_LOOKUP") == "LOOKUP"
    assert map_bb_product_mode("SEMWRAP_LOOKUP") == "LOOKUP"
    assert map_bb_product_mode("WRAP_DECODE") == "DECODE"
    assert map_bb_product_mode("NO_ANSWER") == "ABSTAIN"
    assert map_bb_product_mode("ABSTAIN") == "ABSTAIN"
    assert set(BB0_LATENCY_PATHS) == BB0_MODES
    assert "ABSTAIN" in BB0_MODES


def test_given_scoreboard_when_read_then_cites_ba_and_debts() -> None:
    # GIVEN BA locks · WHEN freeze scoreboard · THEN cite + 11 debts + bars
    cited = set(BB0_SCOREBOARD["cite_ba_locks"])
    assert cited == BB0_CITED_BA_LOCKS
    assert "H-REALGAIN" in cited
    assert "H-NANOGEN11" in cited
    assert "BA-FREEZE" in cited
    debts = BB0_SCOREBOARD["debts"]
    ids = {d["id"] for d in debts}
    assert {
        "bb_forever_false_hit_zero",
        "ba_forever_hold_zero",
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
    bars = BB0_SCOREBOARD["bars"]
    assert int(bars["bb_forever_false_hit_max"]) == 0
    assert int(bars["ba_forever_false_hit_max"]) == 0
    assert int(bars["az_hold_false_hit_max"]) == 0
    assert int(bars["overrefuse_miss_max"]) == 0
    assert int(bars["bb_forever_min_n"]) >= 15
    assert int(bars["bb_forever_classes_min"]) >= 5
    assert bars["decode_gibberish_neq_content_ok"] is True
    assert bars["default_ask_intent_mismatch"] == "ABSTAIN"
    assert bars["default_ask_exact_gold"] == "LOOKUP"
    assert bars["eval_eq_prod_ask"] is True
    assert bars["pack_pass_neq_forever"] is True
    assert bars["ba_pass_neq_bb_forever"] is True
    assert bars["bank_stuff_forbidden"] is True
    assert bars["paraphrase_required"] is True
    assert bars["regression_hold"] is True
    assert bars["speed_baseline_published"] is True
    assert bars["ctx_baseline_published"] is True
    assert bars["l_eff_alone_forbidden"] is True
    assert set(bars["modes_required"]) == BB0_MODES
    metrics = set(BB0_SCOREBOARD["metrics"])
    assert {
        "bb_forever_false_hit",
        "ba_forever_false_hit",
        "az_hold_false_hit",
        "ctx_content_ok",
        "true_continue_ablated",
    } <= metrics


def test_given_forever_when_read_then_min_xor_absdiff_and_or() -> None:
    assert BB0_FOREVER_PROTOCOL["held_out"] is True
    assert BB0_FOREVER_PROTOCOL["forever"] is True
    assert BB0_FOREVER_PROTOCOL["bank_stuff_forbidden"] is True
    assert BB0_FOREVER_PROTOCOL["paraphrase_required"] is True
    assert BB0_FOREVER_PROTOCOL["neq_ba_forever"] is True
    assert BB0_FOREVER_PROTOCOL["neq_az_heldout"] is True
    assert BB0_FOREVER_PROTOCOL["intent_mismatch_is_false_hit"] is True
    assert BB0_FOREVER_PROTOCOL["pack_pass_neq_forever"] is True
    assert BB0_FOREVER_PROTOCOL["ba_pass_neq_bb_forever"] is True
    assert BB0_FOREVER_PROTOCOL["live_fp_id"] == "BB-FH-01"
    assert int(BB0_FOREVER_PROTOCOL["min_n"]) >= 15
    assert len(BB0_FOREVER_ROWS) >= 15
    ids = [p["id"] for p in BB0_FOREVER_ROWS]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("BB-FH-") for i in ids)
    assert all(str(p["question"]).strip() for p in BB0_FOREVER_ROWS)
    assert all(p["expect_mode"] == "ABSTAIN" for p in BB0_FOREVER_ROWS)
    classes = {p["class"] for p in BB0_FOREVER_ROWS}
    assert {
        "ops_min",
        "ops_xor",
        "ops_absdiff",
        "ops_and",
        "ops_or",
    } <= classes
    prior = {str(p["question"]).strip() for p in BA0_FOREVER_ROWS}
    prior |= {str(p["question"]).strip() for p in AZ0_HELDOUT_FP_ROWS}
    prior |= {str(p["question"]).strip() for p in AZ0_OVERREFUSE_ROWS}
    bb_q = {str(p["question"]).strip() for p in BB0_FOREVER_ROWS}
    assert prior.isdisjoint(bb_q)
    live = BB0_FOREVER_ROWS[0]["question"]
    assert "min" in live.lower()


def test_given_ba_hold_when_read_then_regression_bars() -> None:
    assert int(BB0_BA_HOLD_PROTOCOL["forever_false_hit_max"]) == 0
    assert BB0_BA_HOLD_PROTOCOL["regression_hold"] is True
    assert int(BB0_BA_HOLD_PROTOCOL["heldout_n"]) >= 15
    req = set(BB0_BA_HOLD_PROTOCOL["required_classes"])
    assert {
        "ops_pow",
        "ops_mod",
        "ops_max",
        "list_sort",
        "list_len",
    } <= req


def test_given_az_hold_when_read_then_regression_bars() -> None:
    assert int(BB0_AZ_HOLD_PROTOCOL["heldout_false_hit_max"]) == 0
    assert int(BB0_AZ_HOLD_PROTOCOL["overrefuse_miss_max"]) == 0
    assert BB0_AZ_HOLD_PROTOCOL["regression_hold"] is True
    assert int(BB0_AZ_HOLD_PROTOCOL["heldout_n"]) >= 12
    assert int(BB0_AZ_HOLD_PROTOCOL["overrefuse_n"]) >= 3
    req = set(BB0_AZ_HOLD_PROTOCOL["required_classes"])
    assert {"ops_div", "ops_sub", "wrong_slot", "exact_clear"} <= req


def test_given_baselines_when_read_then_speed_and_ctx() -> None:
    paths = BB0_SPEED_BASELINE["paths"]
    assert set(paths) == BB0_MODES
    assert BB0_SPEED_BASELINE["quality_regress_forbidden"] is True
    assert "FASTREAL" in str(BB0_SPEED_BASELINE["source"])
    assert BB0_CTX_BASELINE["l_eff_alone_insufficient"] is True
    assert BB0_CTX_BASELINE["content_bars_required"] is True
    assert "CTXHOLD" in str(BB0_CTX_BASELINE["bb3_gate"])


def test_given_gen_stance_when_read_then_defer_not_nanogen12_rename() -> None:
    assert BB0_GEN_STANCE["stance"] == "defer"
    assert set(BB0_GEN_STANCE["allowed_stances"]) == {"M1", "M2", "M3", "defer"}
    assert BB0_GEN_STANCE["capcheck"] == "closed"
    assert BB0_GEN_STANCE["named_hyp"] == "H-NANOGEN12"
    assert BB0_GEN_STANCE["named_intentgen"] == "H-INTENTGEN"
    assert BB0_GEN_STANCE["named_fast"] == "H-FASTHOLD"
    assert BB0_GEN_STANCE["named_ctx"] == "H-CTXHOLD"
    assert BB0_GEN_STANCE["nanogen12_rename_forbidden"] is True
    assert BB0_GEN_STANCE["nanogen6_hold_cited"] is True
    assert BB0_GEN_STANCE["nanogen7_hold_cited"] is True
    assert BB0_GEN_STANCE["nanogen8_defer_cited"] is True
    assert BB0_GEN_STANCE["nanogen9_defer_cited"] is True
    assert BB0_GEN_STANCE["nanogen10_defer_cited"] is True
    assert BB0_GEN_STANCE["nanogen11_defer_cited"] is True
    methods = BB0_GEN_STANCE["method_candidates"]
    assert set(methods) == {"M1", "M2", "M3"}
    rat = str(BB0_GEN_STANCE["rationale"]).lower()
    assert "defer" in rat
    assert "nanogen" in rat
    judge = BB0_TRUE_GEN_JUDGE
    assert judge["span_fallback_neq_gen"] is True
    assert judge["nanogen12_rename_forbidden"] is True
    assert judge["nanogen11_defer_archived"] is True
    assert "true_continue" in str(judge["scoring"])


def test_given_real_eval_when_read_then_live_and_nanogen12_gated() -> None:
    assert BB0_REAL_EVAL_PROTOCOL["live_ask_battery"] is True
    assert BB0_REAL_EVAL_PROTOCOL["summary_only_forbidden"] is True
    assert BB0_REAL_EVAL_PROTOCOL["wall_ms_n_new_mandatory"] is True
    assert BB0_REAL_EVAL_PROTOCOL["eval_eq_prod_ask"] is True
    assert BB0_REAL_EVAL_PROTOCOL["intent_mismatch_is_false_hit"] is True
    assert BB0_REAL_EVAL_PROTOCOL["exact_gold_abstain_is_miss"] is True
    assert BB0_REAL_EVAL_PROTOCOL["gold_substring_neq_gen"] is True
    assert BB0_REAL_EVAL_PROTOCOL["gibberish_tail_fails"] is True
    assert BB0_REAL_EVAL_PROTOCOL["span_fallback_neq_gen"] is True
    assert BB0_REAL_EVAL_PROTOCOL["pack_pass_neq_forever"] is True
    assert BB0_REAL_EVAL_PROTOCOL["ba_pass_neq_bb_forever"] is True
    assert {
        "OK",
        "FP",
        "MISS",
        "ABSTAIN-OK",
    } <= set(BB0_REAL_EVAL_PROTOCOL["score_labels"])
    claim = str(BB0_REAL_EVAL_PROTOCOL["gen_claim_rule"]).lower()
    assert "nanogen12" in claim
    assert "rename" in claim


def test_given_battery_when_scan_then_covers_modes_and_debts() -> None:
    assert len(BB0_ASK_BATTERY) >= 4
    modes = {p["expect_mode"] for p in BB0_ASK_BATTERY}
    assert modes == BB0_MODES
    kinds = {p["kind"] for p in BB0_ASK_BATTERY}
    assert {
        "near_miss",
        "bb_forever_intent_fp",
        "bb_forever_xor_fp",
        "bb_forever_absdiff_fp",
        "ba_forever_hold",
        "overrefuse_gold",
        "az_hold_div",
        "labeled_peak",
        "junk_trap",
        "decode_content",
    } <= kinds
    ids = [p["id"] for p in BB0_ASK_BATTERY]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("BB-ASK-") for i in ids)


def test_given_notes_when_read_then_anti_fp_and_north_star() -> None:
    assert "≠" in BB0_SAFE_NOTE
    assert "LOOKUP" in BB0_ANTI_FP
    assert "eval path = prod" in BB0_ANTI_FP.lower()
    assert "NANOGEN12" in BB0_ANTI_FP or "nanogen12" in BB0_ANTI_FP.lower()
    assert "≤5M" in BB0_NORTH_STAR
    assert "defer" in BB0_NORTH_STAR.lower()
    assert "gibberish-tail" in BB0_SHIP_LOCK
    assert "TAC" in BB0_SHIP_LOCK
    assert "INTENTGEN" in BB0_THESIS or "BB1" in BB0_THESIS
    assert "defer" in BB0_THESIS.lower()
    assert "min" in BB0_THESIS.lower() or "BB-FOREVER" in BB0_THESIS


def test_given_ready_when_decide_then_promote() -> None:
    out = decide_bb0_session(trials_dir_ready=True, anti_fp_signed=True)
    assert out.startswith("PROMOTE")
    assert BB0_ID in out


def test_given_no_trials_when_decide_then_kill() -> None:
    out = decide_bb0_session(trials_dir_ready=False, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "trials" in out


def test_given_unsigned_anti_fp_when_decide_then_kill() -> None:
    out = decide_bb0_session(trials_dir_ready=True, anti_fp_signed=False)
    assert out.startswith("KILL")
    assert "anti-FP" in out


def test_given_incomplete_battery_when_decide_then_kill() -> None:
    bad = [dict(p) for p in BB0_ASK_BATTERY if p["expect_mode"] != "PEAK"]
    out = decide_bb0_session(
        trials_dir_ready=True, anti_fp_signed=True, battery=bad
    )
    assert out.startswith("KILL")
    assert "battery" in out.lower() or "modes" in out.lower()
