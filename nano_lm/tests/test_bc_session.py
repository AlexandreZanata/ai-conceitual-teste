"""Contract: Wave BC0 SESSION — freeze BC-FOREVER/BA/BB-hold/scoreboard/gen-defer."""

from __future__ import annotations

from az_session_ops import AZ0_HELDOUT_FP_ROWS, AZ0_OVERREFUSE_ROWS
from ba_session_ops import BA0_FOREVER_ROWS
from bb_session_ops import BB0_FOREVER_ROWS
from bc_session_ops import (
    BC0_ANTI_FP,
    BC0_ASK_BATTERY,
    BC0_AZ_HOLD_PROTOCOL,
    BC0_BA_HOLD_PROTOCOL,
    BC0_BB_HOLD_PROTOCOL,
    BC0_CITED_BB_LOCKS,
    BC0_CTX_BASELINE,
    BC0_FOREVER_PROTOCOL,
    BC0_FOREVER_ROWS,
    BC0_GEN_STANCE,
    BC0_ID,
    BC0_LATENCY_PATHS,
    BC0_MODES,
    BC0_NORTH_STAR,
    BC0_REAL_EVAL_PROTOCOL,
    BC0_SAFE_NOTE,
    BC0_SCOREBOARD,
    BC0_SHIP_LOCK,
    BC0_SPEED_BASELINE,
    BC0_THESIS,
    BC0_TRUE_GEN_JUDGE,
    decide_bc0_session,
    map_bc_product_mode,
)


def test_given_modes_when_map_then_lookup_peak_decode_abstain() -> None:
    # GIVEN/WHEN/THEN: pesquisa §9 BC0 — four product modes
    assert map_bc_product_mode("WRAP_LOOKUP") == "LOOKUP"
    assert map_bc_product_mode("SEMWRAP_LOOKUP") == "LOOKUP"
    assert map_bc_product_mode("WRAP_DECODE") == "DECODE"
    assert map_bc_product_mode("NO_ANSWER") == "ABSTAIN"
    assert map_bc_product_mode("ABSTAIN") == "ABSTAIN"
    assert set(BC0_LATENCY_PATHS) == BC0_MODES
    assert "ABSTAIN" in BC0_MODES


def test_given_scoreboard_when_read_then_cites_bb_and_debts() -> None:
    # GIVEN BB locks · WHEN freeze scoreboard · THEN cite + 12 debts + bars
    cited = set(BC0_SCOREBOARD["cite_bb_locks"])
    assert cited == BC0_CITED_BB_LOCKS
    assert "H-INTENTGEN" in cited
    assert "H-NANOGEN12" in cited
    assert "BB-FREEZE" in cited
    debts = BC0_SCOREBOARD["debts"]
    ids = {d["id"] for d in debts}
    assert {
        "bc_forever_false_hit_zero",
        "ba_forever_hold_zero",
        "bb_forever_hold_zero",
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
    bars = BC0_SCOREBOARD["bars"]
    assert int(bars["bc_forever_false_hit_max"]) == 0
    assert int(bars["ba_forever_false_hit_max"]) == 0
    assert int(bars["bb_forever_false_hit_max"]) == 0
    assert int(bars["az_hold_false_hit_max"]) == 0
    assert int(bars["overrefuse_miss_max"]) == 0
    assert int(bars["bc_forever_min_n"]) >= 18
    assert int(bars["bc_forever_classes_min"]) >= 6
    assert int(bars["novel_probes_min"]) >= 10
    assert bars["decode_gibberish_neq_content_ok"] is True
    assert bars["default_ask_intent_mismatch"] == "ABSTAIN"
    assert bars["default_ask_exact_gold"] == "LOOKUP"
    assert bars["eval_eq_prod_ask"] is True
    assert bars["pack_pass_neq_forever"] is True
    assert bars["ba_bb_pass_neq_bc_forever"] is True
    assert bars["bank_stuff_forbidden"] is True
    assert bars["paraphrase_required"] is True
    assert bars["regression_hold"] is True
    assert bars["speed_baseline_published"] is True
    assert bars["ctx_baseline_published"] is True
    assert bars["l_eff_alone_forbidden"] is True
    assert set(bars["modes_required"]) == BC0_MODES
    metrics = set(BC0_SCOREBOARD["metrics"])
    assert {
        "bc_forever_false_hit",
        "ba_forever_false_hit",
        "bb_forever_false_hit",
        "az_hold_false_hit",
        "ctx_content_ok",
        "true_continue_ablated",
    } <= metrics


def test_given_forever_when_read_then_protocol_flags() -> None:
    assert BC0_FOREVER_PROTOCOL["held_out"] is True
    assert BC0_FOREVER_PROTOCOL["forever"] is True
    assert BC0_FOREVER_PROTOCOL["bank_stuff_forbidden"] is True
    assert BC0_FOREVER_PROTOCOL["paraphrase_required"] is True
    assert BC0_FOREVER_PROTOCOL["neq_ba_forever"] is True
    assert BC0_FOREVER_PROTOCOL["neq_bb_forever"] is True
    assert BC0_FOREVER_PROTOCOL["neq_az_heldout"] is True
    assert BC0_FOREVER_PROTOCOL["intent_mismatch_is_false_hit"] is True
    assert BC0_FOREVER_PROTOCOL["pack_pass_neq_forever"] is True
    assert BC0_FOREVER_PROTOCOL["ba_bb_pass_neq_bc_forever"] is True
    assert BC0_FOREVER_PROTOCOL["live_fp_id"] == "BC-FH-01"
    assert int(BC0_FOREVER_PROTOCOL["min_n"]) >= 18


def test_given_forever_when_read_then_floordiv_neg_gcd_shift_nand() -> None:
    assert len(BC0_FOREVER_ROWS) >= 18
    ids = [p["id"] for p in BC0_FOREVER_ROWS]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("BC-FH-") for i in ids)
    assert all(str(p["question"]).strip() for p in BC0_FOREVER_ROWS)
    assert all(p["expect_mode"] == "ABSTAIN" for p in BC0_FOREVER_ROWS)
    classes = {p["class"] for p in BC0_FOREVER_ROWS}
    need = {
        "ops_floordiv",
        "ops_neg",
        "ops_gcd",
        "ops_lshift",
        "ops_rshift",
        "ops_nand",
    }
    assert need <= classes
    live = str(BC0_FOREVER_ROWS[0]["question"]).lower()
    assert "floordiv" in live or "//" in live


def test_given_forever_when_scan_then_disjoint_from_ba_bb_az() -> None:
    prior = {str(p["question"]).strip() for p in BA0_FOREVER_ROWS}
    prior |= {str(p["question"]).strip() for p in BB0_FOREVER_ROWS}
    prior |= {str(p["question"]).strip() for p in AZ0_HELDOUT_FP_ROWS}
    prior |= {str(p["question"]).strip() for p in AZ0_OVERREFUSE_ROWS}
    bc_q = {str(p["question"]).strip() for p in BC0_FOREVER_ROWS}
    assert prior.isdisjoint(bc_q)


def test_given_ba_hold_when_read_then_regression_bars() -> None:
    assert int(BC0_BA_HOLD_PROTOCOL["forever_false_hit_max"]) == 0
    assert BC0_BA_HOLD_PROTOCOL["regression_hold"] is True
    assert int(BC0_BA_HOLD_PROTOCOL["heldout_n"]) >= 15
    req = set(BC0_BA_HOLD_PROTOCOL["required_classes"])
    assert {
        "ops_pow",
        "ops_mod",
        "ops_max",
        "list_sort",
        "list_len",
    } <= req


def test_given_bb_hold_when_read_then_regression_bars() -> None:
    assert int(BC0_BB_HOLD_PROTOCOL["forever_false_hit_max"]) == 0
    assert BC0_BB_HOLD_PROTOCOL["regression_hold"] is True
    assert int(BC0_BB_HOLD_PROTOCOL["heldout_n"]) >= 15
    req = set(BC0_BB_HOLD_PROTOCOL["required_classes"])
    assert {
        "ops_min",
        "ops_xor",
        "ops_absdiff",
        "ops_and",
        "ops_or",
    } <= req


def test_given_az_hold_when_read_then_regression_bars() -> None:
    assert int(BC0_AZ_HOLD_PROTOCOL["heldout_false_hit_max"]) == 0
    assert int(BC0_AZ_HOLD_PROTOCOL["overrefuse_miss_max"]) == 0
    assert BC0_AZ_HOLD_PROTOCOL["regression_hold"] is True
    assert int(BC0_AZ_HOLD_PROTOCOL["heldout_n"]) >= 12
    assert int(BC0_AZ_HOLD_PROTOCOL["overrefuse_n"]) >= 3
    req = set(BC0_AZ_HOLD_PROTOCOL["required_classes"])
    assert {"ops_div", "ops_sub", "wrong_slot", "exact_clear"} <= req


def test_given_baselines_when_read_then_speed_and_ctx() -> None:
    paths = BC0_SPEED_BASELINE["paths"]
    assert set(paths) == BC0_MODES
    assert BC0_SPEED_BASELINE["quality_regress_forbidden"] is True
    assert "FASTHOLD" in str(BC0_SPEED_BASELINE["source"])
    assert BC0_CTX_BASELINE["l_eff_alone_insufficient"] is True
    assert BC0_CTX_BASELINE["content_bars_required"] is True
    assert "CTXLIFT2" in str(BC0_CTX_BASELINE["bc3_gate"])


def test_given_gen_stance_when_read_then_defer_not_nanogen13_rename() -> None:
    assert BC0_GEN_STANCE["stance"] == "defer"
    assert set(BC0_GEN_STANCE["allowed_stances"]) == {"M1", "M2", "M3", "defer"}
    assert BC0_GEN_STANCE["capcheck"] == "closed"
    assert BC0_GEN_STANCE["named_hyp"] == "H-NANOGEN13"
    assert BC0_GEN_STANCE["named_opsfam"] == "H-OPSFAM"
    assert BC0_GEN_STANCE["named_fast"] == "H-FASTLIFT"
    assert BC0_GEN_STANCE["named_ctx"] == "H-CTXLIFT2"
    assert BC0_GEN_STANCE["nanogen13_rename_forbidden"] is True
    assert BC0_GEN_STANCE["nanogen6_hold_cited"] is True
    assert BC0_GEN_STANCE["nanogen7_hold_cited"] is True
    assert BC0_GEN_STANCE["nanogen8_defer_cited"] is True
    assert BC0_GEN_STANCE["nanogen9_defer_cited"] is True
    assert BC0_GEN_STANCE["nanogen10_defer_cited"] is True
    assert BC0_GEN_STANCE["nanogen11_defer_cited"] is True
    assert BC0_GEN_STANCE["nanogen12_defer_cited"] is True
    methods = BC0_GEN_STANCE["method_candidates"]
    assert set(methods) == {"M1", "M2", "M3"}
    rat = str(BC0_GEN_STANCE["rationale"]).lower()
    assert "defer" in rat
    assert "nanogen" in rat
    judge = BC0_TRUE_GEN_JUDGE
    assert judge["span_fallback_neq_gen"] is True
    assert judge["nanogen13_rename_forbidden"] is True
    assert judge["nanogen12_defer_archived"] is True
    assert "true_continue" in str(judge["scoring"])


def test_given_real_eval_when_read_then_live_and_nanogen13_gated() -> None:
    assert BC0_REAL_EVAL_PROTOCOL["live_ask_battery"] is True
    assert BC0_REAL_EVAL_PROTOCOL["summary_only_forbidden"] is True
    assert BC0_REAL_EVAL_PROTOCOL["wall_ms_n_new_mandatory"] is True
    assert BC0_REAL_EVAL_PROTOCOL["eval_eq_prod_ask"] is True
    assert BC0_REAL_EVAL_PROTOCOL["intent_mismatch_is_false_hit"] is True
    assert BC0_REAL_EVAL_PROTOCOL["exact_gold_abstain_is_miss"] is True
    assert BC0_REAL_EVAL_PROTOCOL["gold_substring_neq_gen"] is True
    assert BC0_REAL_EVAL_PROTOCOL["gibberish_tail_fails"] is True
    assert BC0_REAL_EVAL_PROTOCOL["span_fallback_neq_gen"] is True
    assert BC0_REAL_EVAL_PROTOCOL["pack_pass_neq_forever"] is True
    assert BC0_REAL_EVAL_PROTOCOL["ba_bb_pass_neq_bc_forever"] is True
    assert int(BC0_REAL_EVAL_PROTOCOL["novel_probes_min"]) >= 10
    assert {
        "OK",
        "FP",
        "MISS",
        "ABSTAIN-OK",
    } <= set(BC0_REAL_EVAL_PROTOCOL["score_labels"])
    claim = str(BC0_REAL_EVAL_PROTOCOL["gen_claim_rule"]).lower()
    assert "nanogen13" in claim
    assert "rename" in claim


def test_given_battery_when_scan_then_covers_modes_and_debts() -> None:
    assert len(BC0_ASK_BATTERY) >= 4
    modes = {p["expect_mode"] for p in BC0_ASK_BATTERY}
    assert modes == BC0_MODES
    kinds = {p["kind"] for p in BC0_ASK_BATTERY}
    assert {
        "near_miss",
        "bc_forever_intent_fp",
        "bc_forever_gcd_fp",
        "bc_forever_shift_fp",
        "ba_forever_hold",
        "bb_forever_hold",
        "overrefuse_gold",
        "az_hold_div",
        "labeled_peak",
        "junk_trap",
        "decode_content",
    } <= kinds
    ids = [p["id"] for p in BC0_ASK_BATTERY]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("BC-ASK-") for i in ids)


def test_given_notes_when_read_then_anti_fp_and_north_star() -> None:
    assert "≠" in BC0_SAFE_NOTE
    assert "LOOKUP" in BC0_ANTI_FP
    assert "eval path = prod" in BC0_ANTI_FP.lower()
    assert "NANOGEN13" in BC0_ANTI_FP or "nanogen13" in BC0_ANTI_FP.lower()
    assert "floordiv" in BC0_ANTI_FP.lower() or "BC-FOREVER" in BC0_ANTI_FP
    assert "≤5M" in BC0_NORTH_STAR
    assert "defer" in BC0_NORTH_STAR.lower()
    assert "gibberish-tail" in BC0_SHIP_LOCK
    assert "TAC" in BC0_SHIP_LOCK
    assert "OPSFAM" in BC0_THESIS or "BC1" in BC0_THESIS
    assert "defer" in BC0_THESIS.lower()
    assert "floordiv" in BC0_THESIS.lower() or "BC-FOREVER" in BC0_THESIS


def test_given_ready_when_decide_then_promote() -> None:
    out = decide_bc0_session(trials_dir_ready=True, anti_fp_signed=True)
    assert out.startswith("PROMOTE")
    assert BC0_ID in out


def test_given_no_trials_when_decide_then_kill() -> None:
    out = decide_bc0_session(trials_dir_ready=False, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "trials" in out


def test_given_unsigned_anti_fp_when_decide_then_kill() -> None:
    out = decide_bc0_session(trials_dir_ready=True, anti_fp_signed=False)
    assert out.startswith("KILL")
    assert "anti-FP" in out


def test_given_incomplete_battery_when_decide_then_kill() -> None:
    bad = [dict(p) for p in BC0_ASK_BATTERY if p["expect_mode"] != "PEAK"]
    out = decide_bc0_session(
        trials_dir_ready=True, anti_fp_signed=True, battery=bad
    )
    assert out.startswith("KILL")
    assert "battery" in out.lower() or "modes" in out.lower()
