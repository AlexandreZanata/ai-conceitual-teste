"""Contract: Wave BD0 SESSION — freeze BD-FOREVER/BA/BB/BC-hold/scoreboard/gen-defer."""

from __future__ import annotations

from az_session_ops import AZ0_HELDOUT_FP_ROWS, AZ0_OVERREFUSE_ROWS
from ba_session_ops import BA0_FOREVER_ROWS
from bb_session_ops import BB0_FOREVER_ROWS
from bc_session_ops import BC0_FOREVER_ROWS
from bd_session_ops import (
    BD0_ANTI_FP,
    BD0_ASK_BATTERY,
    BD0_AZ_HOLD_PROTOCOL,
    BD0_BA_HOLD_PROTOCOL,
    BD0_BB_HOLD_PROTOCOL,
    BD0_BC_HOLD_PROTOCOL,
    BD0_CITED_BC_LOCKS,
    BD0_CTX_BASELINE,
    BD0_FOREVER_PROTOCOL,
    BD0_FOREVER_ROWS,
    BD0_GEN_STANCE,
    BD0_ID,
    BD0_LATENCY_PATHS,
    BD0_MODES,
    BD0_NORTH_STAR,
    BD0_REAL_EVAL_PROTOCOL,
    BD0_SAFE_NOTE,
    BD0_SCOREBOARD,
    BD0_SHIP_LOCK,
    BD0_SPEED_BASELINE,
    BD0_THESIS,
    BD0_TRUE_GEN_JUDGE,
    decide_bd0_session,
    map_bd_product_mode,
)


def test_given_modes_when_map_then_lookup_peak_decode_abstain() -> None:
    # GIVEN/WHEN/THEN: pesquisa §9 BD0 — four product modes
    assert map_bd_product_mode("WRAP_LOOKUP") == "LOOKUP"
    assert map_bd_product_mode("SEMWRAP_LOOKUP") == "LOOKUP"
    assert map_bd_product_mode("WRAP_DECODE") == "DECODE"
    assert map_bd_product_mode("NO_ANSWER") == "ABSTAIN"
    assert map_bd_product_mode("ABSTAIN") == "ABSTAIN"
    assert set(BD0_LATENCY_PATHS) == BD0_MODES
    assert "ABSTAIN" in BD0_MODES


def test_given_scoreboard_when_read_then_cites_bc_and_debts() -> None:
    # GIVEN BC locks · WHEN freeze scoreboard · THEN cite + 13 debts + bars
    cited = set(BD0_SCOREBOARD["cite_bc_locks"])
    assert cited == BD0_CITED_BC_LOCKS
    assert "H-OPSFAM" in cited
    assert "H-NANOGEN13" in cited
    assert "BC-FREEZE" in cited
    debts = BD0_SCOREBOARD["debts"]
    ids = {d["id"] for d in debts}
    assert {
        "bd_forever_false_hit_zero",
        "ba_forever_hold_zero",
        "bb_forever_hold_zero",
        "bc_forever_hold_zero",
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
    bars = BD0_SCOREBOARD["bars"]
    assert int(bars["bd_forever_false_hit_max"]) == 0
    assert int(bars["ba_forever_false_hit_max"]) == 0
    assert int(bars["bb_forever_false_hit_max"]) == 0
    assert int(bars["bc_forever_false_hit_max"]) == 0
    assert int(bars["az_hold_false_hit_max"]) == 0
    assert int(bars["overrefuse_miss_max"]) == 0
    assert int(bars["bd_forever_min_n"]) >= 12
    assert int(bars["bd_forever_classes_min"]) >= 3
    assert int(bars["novel_probes_min"]) >= 10
    assert bars["decode_gibberish_neq_content_ok"] is True
    assert bars["default_ask_intent_mismatch"] == "ABSTAIN"
    assert bars["default_ask_exact_gold"] == "LOOKUP"
    assert bars["eval_eq_prod_ask"] is True
    assert bars["pack_pass_neq_forever"] is True
    assert bars["ba_bb_bc_pass_neq_bd_forever"] is True
    assert bars["bank_stuff_forbidden"] is True
    assert bars["paraphrase_required"] is True
    assert bars["regression_hold"] is True
    assert bars["speed_baseline_published"] is True
    assert bars["ctx_baseline_published"] is True
    assert bars["l_eff_alone_forbidden"] is True
    assert set(bars["modes_required"]) == BD0_MODES
    metrics = set(BD0_SCOREBOARD["metrics"])
    assert {
        "bd_forever_false_hit",
        "ba_forever_false_hit",
        "bb_forever_false_hit",
        "bc_forever_false_hit",
        "az_hold_false_hit",
        "ctx_content_ok",
        "true_continue_ablated",
    } <= metrics


def test_given_forever_when_read_then_protocol_flags() -> None:
    assert BD0_FOREVER_PROTOCOL["held_out"] is True
    assert BD0_FOREVER_PROTOCOL["forever"] is True
    assert BD0_FOREVER_PROTOCOL["bank_stuff_forbidden"] is True
    assert BD0_FOREVER_PROTOCOL["paraphrase_required"] is True
    assert BD0_FOREVER_PROTOCOL["neq_ba_forever"] is True
    assert BD0_FOREVER_PROTOCOL["neq_bb_forever"] is True
    assert BD0_FOREVER_PROTOCOL["neq_bc_forever"] is True
    assert BD0_FOREVER_PROTOCOL["neq_az_heldout"] is True
    assert BD0_FOREVER_PROTOCOL["intent_mismatch_is_false_hit"] is True
    assert BD0_FOREVER_PROTOCOL["semantic_wrong_bank_is_false_hit"] is True
    assert BD0_FOREVER_PROTOCOL["pack_pass_neq_forever"] is True
    assert BD0_FOREVER_PROTOCOL["ba_bb_bc_pass_neq_bd_forever"] is True
    assert BD0_FOREVER_PROTOCOL["live_fp_id"] == "BD-FH-01"
    assert int(BD0_FOREVER_PROTOCOL["min_n"]) >= 12


def test_given_forever_when_read_then_reverse_mul_neighbor() -> None:
    assert len(BD0_FOREVER_ROWS) >= 12
    ids = [p["id"] for p in BD0_FOREVER_ROWS]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("BD-FH-") for i in ids)
    assert all(str(p["question"]).strip() for p in BD0_FOREVER_ROWS)
    assert all(p["expect_mode"] == "ABSTAIN" for p in BD0_FOREVER_ROWS)
    classes = {p["class"] for p in BD0_FOREVER_ROWS}
    need = {"semantic_reverse", "semantic_mul", "wrong_bank_neighbor"}
    assert need <= classes
    live = str(BD0_FOREVER_ROWS[0]["question"]).lower()
    assert "reverse" in live
    mul = str(BD0_FOREVER_ROWS[4]["question"]).lower()
    assert "multipl" in mul or "product" in mul


def test_given_forever_when_scan_then_disjoint_from_ba_bb_bc_az() -> None:
    prior = {str(p["question"]).strip() for p in BA0_FOREVER_ROWS}
    prior |= {str(p["question"]).strip() for p in BB0_FOREVER_ROWS}
    prior |= {str(p["question"]).strip() for p in BC0_FOREVER_ROWS}
    prior |= {str(p["question"]).strip() for p in AZ0_HELDOUT_FP_ROWS}
    prior |= {str(p["question"]).strip() for p in AZ0_OVERREFUSE_ROWS}
    bd_q = {str(p["question"]).strip() for p in BD0_FOREVER_ROWS}
    assert prior.isdisjoint(bd_q)


def test_given_hold_when_read_then_ba_bb_bc_az_regression_bars() -> None:
    assert int(BD0_BA_HOLD_PROTOCOL["forever_false_hit_max"]) == 0
    assert BD0_BA_HOLD_PROTOCOL["regression_hold"] is True
    assert int(BD0_BA_HOLD_PROTOCOL["heldout_n"]) >= 15
    assert int(BD0_BB_HOLD_PROTOCOL["forever_false_hit_max"]) == 0
    assert BD0_BB_HOLD_PROTOCOL["regression_hold"] is True
    assert int(BD0_BB_HOLD_PROTOCOL["heldout_n"]) >= 15
    assert int(BD0_BC_HOLD_PROTOCOL["forever_false_hit_max"]) == 0
    assert BD0_BC_HOLD_PROTOCOL["regression_hold"] is True
    assert int(BD0_BC_HOLD_PROTOCOL["heldout_n"]) >= 18
    assert int(BD0_AZ_HOLD_PROTOCOL["heldout_false_hit_max"]) == 0
    assert int(BD0_AZ_HOLD_PROTOCOL["overrefuse_miss_max"]) == 0
    assert BD0_AZ_HOLD_PROTOCOL["regression_hold"] is True
    assert int(BD0_AZ_HOLD_PROTOCOL["heldout_n"]) >= 12
    assert int(BD0_AZ_HOLD_PROTOCOL["overrefuse_n"]) >= 3


def test_given_baselines_when_read_then_speed_and_ctx() -> None:
    paths = BD0_SPEED_BASELINE["paths"]
    assert set(paths) == BD0_MODES
    assert BD0_SPEED_BASELINE["quality_regress_forbidden"] is True
    assert "FASTLIFT" in str(BD0_SPEED_BASELINE["source"])
    assert BD0_CTX_BASELINE["l_eff_alone_insufficient"] is True
    assert BD0_CTX_BASELINE["content_bars_required"] is True
    assert "CTXGAIN" in str(BD0_CTX_BASELINE["bd3_gate"])


def test_given_gen_stance_when_read_then_defer_not_nanogen14_rename() -> None:
    assert BD0_GEN_STANCE["stance"] == "defer"
    assert set(BD0_GEN_STANCE["allowed_stances"]) == {"M1", "M2", "M3", "defer"}
    assert BD0_GEN_STANCE["capcheck"] == "closed"
    assert BD0_GEN_STANCE["named_hyp"] == "H-NANOGEN14"
    assert BD0_GEN_STANCE["named_semint"] == "H-SEMINT"
    assert BD0_GEN_STANCE["named_fast"] == "H-FASTGAIN"
    assert BD0_GEN_STANCE["named_ctx"] == "H-CTXGAIN"
    assert BD0_GEN_STANCE["nanogen14_rename_forbidden"] is True
    assert BD0_GEN_STANCE["nanogen13_defer_cited"] is True
    assert BD0_GEN_STANCE["nanogen6_hold_cited"] is True
    methods = BD0_GEN_STANCE["method_candidates"]
    assert set(methods) == {"M1", "M2", "M3"}
    rat = str(BD0_GEN_STANCE["rationale"]).lower()
    assert "defer" in rat
    assert "nanogen" in rat
    judge = BD0_TRUE_GEN_JUDGE
    assert judge["span_fallback_neq_gen"] is True
    assert judge["nanogen14_rename_forbidden"] is True
    assert judge["nanogen13_defer_archived"] is True
    assert "true_continue" in str(judge["scoring"])


def test_given_real_eval_when_read_then_live_and_nanogen14_gated() -> None:
    assert BD0_REAL_EVAL_PROTOCOL["live_ask_battery"] is True
    assert BD0_REAL_EVAL_PROTOCOL["summary_only_forbidden"] is True
    assert BD0_REAL_EVAL_PROTOCOL["wall_ms_n_new_mandatory"] is True
    assert BD0_REAL_EVAL_PROTOCOL["eval_eq_prod_ask"] is True
    assert BD0_REAL_EVAL_PROTOCOL["intent_mismatch_is_false_hit"] is True
    assert BD0_REAL_EVAL_PROTOCOL["semantic_wrong_bank_is_false_hit"] is True
    assert BD0_REAL_EVAL_PROTOCOL["exact_gold_abstain_is_miss"] is True
    assert BD0_REAL_EVAL_PROTOCOL["gold_substring_neq_gen"] is True
    assert BD0_REAL_EVAL_PROTOCOL["gibberish_tail_fails"] is True
    assert BD0_REAL_EVAL_PROTOCOL["span_fallback_neq_gen"] is True
    assert BD0_REAL_EVAL_PROTOCOL["pack_pass_neq_forever"] is True
    assert BD0_REAL_EVAL_PROTOCOL["ba_bb_bc_pass_neq_bd_forever"] is True
    assert int(BD0_REAL_EVAL_PROTOCOL["novel_probes_min"]) >= 10
    assert {
        "OK",
        "FP",
        "MISS",
        "ABSTAIN-OK",
    } <= set(BD0_REAL_EVAL_PROTOCOL["score_labels"])
    claim = str(BD0_REAL_EVAL_PROTOCOL["gen_claim_rule"]).lower()
    assert "nanogen14" in claim
    assert "rename" in claim


def test_given_battery_when_scan_then_covers_modes_and_debts() -> None:
    assert len(BD0_ASK_BATTERY) >= 4
    modes = {p["expect_mode"] for p in BD0_ASK_BATTERY}
    assert modes == BD0_MODES
    kinds = {p["kind"] for p in BD0_ASK_BATTERY}
    assert {
        "near_miss",
        "bd_forever_reverse_fp",
        "bd_forever_mul_fp",
        "bd_forever_neighbor_fp",
        "ba_forever_hold",
        "bb_forever_hold",
        "bc_forever_hold",
        "overrefuse_gold",
        "az_hold_div",
        "labeled_peak",
        "junk_trap",
        "decode_content",
    } <= kinds
    ids = [p["id"] for p in BD0_ASK_BATTERY]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("BD-ASK-") for i in ids)


def test_given_notes_when_read_then_anti_fp_and_north_star() -> None:
    assert "≠" in BD0_SAFE_NOTE
    assert "LOOKUP" in BD0_ANTI_FP
    assert "eval path = prod" in BD0_ANTI_FP.lower()
    assert "NANOGEN14" in BD0_ANTI_FP or "nanogen14" in BD0_ANTI_FP.lower()
    assert "reverse" in BD0_ANTI_FP.lower() or "BD-FOREVER" in BD0_ANTI_FP
    assert "≤5M" in BD0_NORTH_STAR
    assert "defer" in BD0_NORTH_STAR.lower()
    assert "gibberish-tail" in BD0_SHIP_LOCK
    assert "TAC" in BD0_SHIP_LOCK
    assert "SEMINT" in BD0_THESIS or "BD1" in BD0_THESIS
    assert "defer" in BD0_THESIS.lower()
    assert "reverse" in BD0_THESIS.lower() or "BD-FOREVER" in BD0_THESIS


def test_given_ready_when_decide_then_promote() -> None:
    out = decide_bd0_session(trials_dir_ready=True, anti_fp_signed=True)
    assert out.startswith("PROMOTE")
    assert BD0_ID in out


def test_given_no_trials_when_decide_then_kill() -> None:
    out = decide_bd0_session(trials_dir_ready=False, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "trials" in out


def test_given_unsigned_anti_fp_when_decide_then_kill() -> None:
    out = decide_bd0_session(trials_dir_ready=True, anti_fp_signed=False)
    assert out.startswith("KILL")
    assert "anti-FP" in out


def test_given_incomplete_battery_when_decide_then_kill() -> None:
    bad = [dict(p) for p in BD0_ASK_BATTERY if p["expect_mode"] != "PEAK"]
    out = decide_bd0_session(
        trials_dir_ready=True, anti_fp_signed=True, battery=bad
    )
    assert out.startswith("KILL")
    assert "battery" in out.lower() or "modes" in out.lower()
