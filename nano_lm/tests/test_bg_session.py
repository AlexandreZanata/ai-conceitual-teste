"""Contract: Wave BG0 SESSION — freeze BG-FOREVER/BA…BF-hold/util/gen-SKIP."""

from __future__ import annotations

from az_session_ops import AZ0_HELDOUT_FP_ROWS, AZ0_OVERREFUSE_ROWS
from ba_session_ops import BA0_FOREVER_ROWS
from bb_session_ops import BB0_FOREVER_ROWS
from bc_session_ops import BC0_FOREVER_ROWS
from bd_session_ops import BD0_FOREVER_ROWS
from be_session_ops import BE0_FOREVER_ROWS
from bf_session_ops import BF0_FOREVER_ROWS
from bg_session_ops import (
    BG0_ANTI_FP,
    BG0_ASK_BATTERY,
    BG0_AZ_HOLD_PROTOCOL,
    BG0_BA_HOLD_PROTOCOL,
    BG0_BB_HOLD_PROTOCOL,
    BG0_BC_HOLD_PROTOCOL,
    BG0_BD_HOLD_PROTOCOL,
    BG0_BE_HOLD_PROTOCOL,
    BG0_BF_HOLD_PROTOCOL,
    BG0_CITED_BF_LOCKS,
    BG0_CTX_BASELINE,
    BG0_FOREVER_PROTOCOL,
    BG0_FOREVER_ROWS,
    BG0_GEN_STANCE,
    BG0_ID,
    BG0_LATENCY_PATHS,
    BG0_MODES,
    BG0_NORTH_STAR,
    BG0_REAL_EVAL_PROTOCOL,
    BG0_SAFE_NOTE,
    BG0_SCOREBOARD,
    BG0_SHIP_LOCK,
    BG0_SPEED_BASELINE,
    BG0_THESIS,
    BG0_TRUE_GEN_JUDGE,
    BG0_UTIL_TRACK,
    decide_bg0_session,
    map_bg_product_mode,
)


def test_given_modes_when_map_then_lookup_peak_decode_abstain() -> None:
    # GIVEN/WHEN/THEN: pesquisa §9 BG0 — four product modes
    assert map_bg_product_mode("WRAP_LOOKUP") == "LOOKUP"
    assert map_bg_product_mode("SEMWRAP_LOOKUP") == "LOOKUP"
    assert map_bg_product_mode("WRAP_DECODE") == "DECODE"
    assert map_bg_product_mode("NO_ANSWER") == "ABSTAIN"
    assert map_bg_product_mode("ABSTAIN") == "ABSTAIN"
    assert set(BG0_LATENCY_PATHS) == BG0_MODES
    assert "ABSTAIN" in BG0_MODES


def test_given_scoreboard_when_read_then_cites_bf_and_debts() -> None:
    # GIVEN BF locks · WHEN freeze scoreboard · THEN cite + ≥16 debts + bars
    cited = set(BG0_SCOREBOARD["cite_bf_locks"])
    assert cited == BG0_CITED_BF_LOCKS
    assert "H-PREDINT" in cited
    assert "H-NANOGEN16" in cited
    assert "BF-FREEZE" in cited
    debts = BG0_SCOREBOARD["debts"]
    ids = {d["id"] for d in debts}
    assert {
        "bg_forever_false_hit_zero",
        "ba_forever_hold_zero",
        "bb_forever_hold_zero",
        "bc_forever_hold_zero",
        "bd_forever_hold_zero",
        "be_forever_hold_zero",
        "bf_forever_hold_zero",
        "az_hold_zero",
        "overrefuse_exact_gold",
        "live_ask_scoreboard",
        "speed_baseline_publish",
        "ctx_baseline_publish",
        "mode_ui_always",
        "decode_content_law",
        "gen_skip_stance",
        "paraphrase_eval_rule",
        "utilization_track_a_plus_plus",
    } <= ids
    bars = BG0_SCOREBOARD["bars"]
    assert int(bars["bg_forever_false_hit_max"]) == 0
    assert int(bars["ba_forever_false_hit_max"]) == 0
    assert int(bars["bb_forever_false_hit_max"]) == 0
    assert int(bars["bc_forever_false_hit_max"]) == 0
    assert int(bars["bd_forever_false_hit_max"]) == 0
    assert int(bars["be_forever_false_hit_max"]) == 0
    assert int(bars["bf_forever_false_hit_max"]) == 0
    assert int(bars["az_hold_false_hit_max"]) == 0
    assert int(bars["overrefuse_miss_max"]) == 0
    assert int(bars["bg_forever_min_n"]) >= 12
    assert int(bars["bg_forever_classes_min"]) >= 4
    assert int(bars["novel_probes_min"]) >= 10
    assert bars["decode_gibberish_neq_content_ok"] is True
    assert bars["default_ask_intent_mismatch"] == "ABSTAIN"
    assert bars["default_ask_exact_gold"] == "LOOKUP"
    assert bars["eval_eq_prod_ask"] is True
    assert bars["pack_pass_neq_forever"] is True
    assert bars["ba_bb_bc_bd_be_bf_pass_neq_bg_forever"] is True
    assert bars["bank_stuff_forbidden"] is True
    assert bars["paraphrase_required"] is True
    assert bars["unary_transform_gate_preferred"] is True
    assert bars["regression_hold"] is True
    assert bars["speed_baseline_published"] is True
    assert bars["ctx_baseline_published"] is True
    assert bars["utilization_track_frozen"] is True
    assert bars["l_eff_alone_forbidden"] is True
    assert set(bars["modes_required"]) == BG0_MODES
    metrics = set(BG0_SCOREBOARD["metrics"])
    assert {
        "bg_forever_false_hit",
        "ba_forever_false_hit",
        "bb_forever_false_hit",
        "bc_forever_false_hit",
        "bd_forever_false_hit",
        "be_forever_false_hit",
        "bf_forever_false_hit",
        "az_hold_false_hit",
        "ctx_content_ok",
        "true_continue_ablated",
        "utilization_ok",
    } <= metrics


def test_given_forever_when_read_then_protocol_flags() -> None:
    assert BG0_FOREVER_PROTOCOL["held_out"] is True
    assert BG0_FOREVER_PROTOCOL["forever"] is True
    assert BG0_FOREVER_PROTOCOL["bank_stuff_forbidden"] is True
    assert BG0_FOREVER_PROTOCOL["paraphrase_required"] is True
    assert BG0_FOREVER_PROTOCOL["unary_transform_gate_preferred"] is True
    assert BG0_FOREVER_PROTOCOL["neq_ba_forever"] is True
    assert BG0_FOREVER_PROTOCOL["neq_bb_forever"] is True
    assert BG0_FOREVER_PROTOCOL["neq_bc_forever"] is True
    assert BG0_FOREVER_PROTOCOL["neq_bd_forever"] is True
    assert BG0_FOREVER_PROTOCOL["neq_be_forever"] is True
    assert BG0_FOREVER_PROTOCOL["neq_bf_forever"] is True
    assert BG0_FOREVER_PROTOCOL["neq_az_heldout"] is True
    assert BG0_FOREVER_PROTOCOL["unary_mismatch_is_false_hit"] is True
    assert BG0_FOREVER_PROTOCOL["transform_mismatch_is_false_hit"] is True
    assert BG0_FOREVER_PROTOCOL["pack_pass_neq_forever"] is True
    assert BG0_FOREVER_PROTOCOL["ba_bb_bc_bd_be_bf_pass_neq_bg_forever"] is True
    assert BG0_FOREVER_PROTOCOL["live_fp_id"] == "BG-FH-01"
    assert int(BG0_FOREVER_PROTOCOL["min_n"]) >= 12


def test_given_forever_when_read_then_unary_transform_classes() -> None:
    assert len(BG0_FOREVER_ROWS) >= 12
    ids = [p["id"] for p in BG0_FOREVER_ROWS]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("BG-FH-") for i in ids)
    assert all(str(p["question"]).strip() for p in BG0_FOREVER_ROWS)
    assert all(p["expect_mode"] == "ABSTAIN" for p in BG0_FOREVER_ROWS)
    classes = {p["class"] for p in BG0_FOREVER_ROWS}
    need = {
        "unary_math",
        "unary_math_para",
        "string_transform",
        "string_transform_para",
        "aggregate_predicate",
        "arity_transform_neighbor",
    }
    assert need <= classes
    live = str(BG0_FOREVER_ROWS[0]["question"]).lower()
    assert "absolute" in live or "abs" in live


def test_given_forever_when_scan_then_disjoint_from_ba_through_bf_az() -> None:
    prior = {str(p["question"]).strip() for p in BA0_FOREVER_ROWS}
    prior |= {str(p["question"]).strip() for p in BB0_FOREVER_ROWS}
    prior |= {str(p["question"]).strip() for p in BC0_FOREVER_ROWS}
    prior |= {str(p["question"]).strip() for p in BD0_FOREVER_ROWS}
    prior |= {str(p["question"]).strip() for p in BE0_FOREVER_ROWS}
    prior |= {str(p["question"]).strip() for p in BF0_FOREVER_ROWS}
    prior |= {str(p["question"]).strip() for p in AZ0_HELDOUT_FP_ROWS}
    prior |= {str(p["question"]).strip() for p in AZ0_OVERREFUSE_ROWS}
    bg_q = {str(p["question"]).strip() for p in BG0_FOREVER_ROWS}
    assert prior.isdisjoint(bg_q)


def test_given_hold_when_read_then_ba_through_bf_az_regression_bars() -> None:
    assert int(BG0_BA_HOLD_PROTOCOL["forever_false_hit_max"]) == 0
    assert BG0_BA_HOLD_PROTOCOL["regression_hold"] is True
    assert int(BG0_BA_HOLD_PROTOCOL["heldout_n"]) >= 15
    assert int(BG0_BB_HOLD_PROTOCOL["forever_false_hit_max"]) == 0
    assert BG0_BB_HOLD_PROTOCOL["regression_hold"] is True
    assert int(BG0_BB_HOLD_PROTOCOL["heldout_n"]) >= 15
    assert int(BG0_BC_HOLD_PROTOCOL["forever_false_hit_max"]) == 0
    assert BG0_BC_HOLD_PROTOCOL["regression_hold"] is True
    assert int(BG0_BC_HOLD_PROTOCOL["heldout_n"]) >= 18
    assert int(BG0_BD_HOLD_PROTOCOL["forever_false_hit_max"]) == 0
    assert BG0_BD_HOLD_PROTOCOL["regression_hold"] is True
    assert int(BG0_BD_HOLD_PROTOCOL["heldout_n"]) >= 12
    assert int(BG0_BE_HOLD_PROTOCOL["forever_false_hit_max"]) == 0
    assert BG0_BE_HOLD_PROTOCOL["regression_hold"] is True
    assert int(BG0_BE_HOLD_PROTOCOL["heldout_n"]) >= 12
    assert int(BG0_BF_HOLD_PROTOCOL["forever_false_hit_max"]) == 0
    assert BG0_BF_HOLD_PROTOCOL["regression_hold"] is True
    assert int(BG0_BF_HOLD_PROTOCOL["heldout_n"]) >= 12
    assert int(BG0_AZ_HOLD_PROTOCOL["heldout_false_hit_max"]) == 0
    assert int(BG0_AZ_HOLD_PROTOCOL["overrefuse_miss_max"]) == 0
    assert BG0_AZ_HOLD_PROTOCOL["regression_hold"] is True
    assert int(BG0_AZ_HOLD_PROTOCOL["heldout_n"]) >= 12
    assert int(BG0_AZ_HOLD_PROTOCOL["overrefuse_n"]) >= 3


def test_given_baselines_when_read_then_speed_ctx_and_util() -> None:
    paths = BG0_SPEED_BASELINE["paths"]
    assert set(paths) == BG0_MODES
    assert BG0_SPEED_BASELINE["quality_regress_forbidden"] is True
    assert "FASTBF" in str(BG0_SPEED_BASELINE["source"])
    assert BG0_CTX_BASELINE["l_eff_alone_insufficient"] is True
    assert BG0_CTX_BASELINE["content_bars_required"] is True
    assert "CTXBG" in str(BG0_CTX_BASELINE["bg4_gate"])
    assert BG0_UTIL_TRACK["gpt_claim_forbidden"] is True
    assert BG0_UTIL_TRACK["known_ask_hitl"] is True
    assert BG0_UTIL_TRACK["paper_arxiv_sync"] is True
    assert len(BG0_UTIL_TRACK["checklist"]) >= 4
    assert "SHIPPUB" in str(BG0_UTIL_TRACK["bg2_gate"])


def test_given_gen_stance_when_read_then_skip_not_nanogen17_rename() -> None:
    assert BG0_GEN_STANCE["stance"] == "skip"
    assert set(BG0_GEN_STANCE["allowed_stances"]) == {"M1", "M2", "M3", "skip"}
    assert BG0_GEN_STANCE["method_plan_attached"] is False
    assert BG0_GEN_STANCE["capcheck"] == "closed"
    assert BG0_GEN_STANCE["named_hyp"] == "H-NANOGEN17"
    assert BG0_GEN_STANCE["named_unaryint"] == "H-UNARYINT"
    assert BG0_GEN_STANCE["named_shippub"] == "H-SHIPPUB"
    assert BG0_GEN_STANCE["named_fast"] == "H-FASTBG"
    assert BG0_GEN_STANCE["named_ctx"] == "H-CTXBG"
    assert BG0_GEN_STANCE["nanogen17_rename_forbidden"] is True
    assert BG0_GEN_STANCE["nanogen17_without_plan_forbidden"] is True
    assert BG0_GEN_STANCE["skip_gen_stop_rule"] is True
    assert BG0_GEN_STANCE["nanogen16_skip_cited"] is True
    methods = BG0_GEN_STANCE["method_candidates"]
    assert set(methods) == {"M1", "M2", "M3"}
    rat = str(BG0_GEN_STANCE["rationale"]).lower()
    assert "skip" in rat
    assert "nanogen" in rat
    judge = BG0_TRUE_GEN_JUDGE
    assert judge["span_fallback_neq_gen"] is True
    assert judge["nanogen17_without_plan_forbidden"] is True
    assert "true_continue" in str(judge["scoring"])


def test_given_real_eval_when_read_then_live_and_nanogen17_gated() -> None:
    assert BG0_REAL_EVAL_PROTOCOL["live_ask_battery"] is True
    assert BG0_REAL_EVAL_PROTOCOL["summary_only_forbidden"] is True
    assert BG0_REAL_EVAL_PROTOCOL["wall_ms_n_new_mandatory"] is True
    assert BG0_REAL_EVAL_PROTOCOL["eval_eq_prod_ask"] is True
    assert BG0_REAL_EVAL_PROTOCOL["intent_mismatch_is_false_hit"] is True
    assert BG0_REAL_EVAL_PROTOCOL["unary_mismatch_is_false_hit"] is True
    assert BG0_REAL_EVAL_PROTOCOL["transform_mismatch_is_false_hit"] is True
    assert BG0_REAL_EVAL_PROTOCOL["exact_gold_abstain_is_miss"] is True
    assert BG0_REAL_EVAL_PROTOCOL["gold_substring_neq_gen"] is True
    assert BG0_REAL_EVAL_PROTOCOL["gibberish_tail_fails"] is True
    assert BG0_REAL_EVAL_PROTOCOL["span_fallback_neq_gen"] is True
    assert BG0_REAL_EVAL_PROTOCOL["pack_pass_neq_forever"] is True
    assert BG0_REAL_EVAL_PROTOCOL["ba_bb_bc_bd_be_bf_pass_neq_bg_forever"] is True
    assert BG0_REAL_EVAL_PROTOCOL["utilization_scored"] is True
    assert int(BG0_REAL_EVAL_PROTOCOL["novel_probes_min"]) >= 10
    assert {
        "OK",
        "FP",
        "MISS",
        "ABSTAIN-OK",
    } <= set(BG0_REAL_EVAL_PROTOCOL["score_labels"])
    claim = str(BG0_REAL_EVAL_PROTOCOL["gen_claim_rule"]).lower()
    assert "nanogen17" in claim
    assert "skip" in claim


def test_given_battery_when_scan_then_covers_modes_and_debts() -> None:
    assert len(BG0_ASK_BATTERY) >= 4
    modes = {p["expect_mode"] for p in BG0_ASK_BATTERY}
    assert modes == BG0_MODES
    kinds = {p["kind"] for p in BG0_ASK_BATTERY}
    assert {
        "near_miss",
        "bg_forever_unary_fp",
        "bg_forever_transform_fp",
        "bf_forever_hold",
        "be_forever_hold",
        "bd_forever_hold",
        "ba_forever_hold",
        "bb_forever_hold",
        "bc_forever_hold",
        "overrefuse_gold",
        "az_hold_div",
        "labeled_peak",
        "junk_trap",
        "decode_content",
        "utilization_smoke",
    } <= kinds
    ids = [p["id"] for p in BG0_ASK_BATTERY]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("BG-ASK-") for i in ids)


def test_given_notes_when_read_then_anti_fp_and_north_star() -> None:
    assert "≠" in BG0_SAFE_NOTE
    assert "LOOKUP" in BG0_ANTI_FP
    assert "eval path = prod" in BG0_ANTI_FP.lower()
    assert "NANOGEN17" in BG0_ANTI_FP or "nanogen17" in BG0_ANTI_FP.lower()
    assert "unary" in BG0_ANTI_FP.lower() or "BG-FOREVER" in BG0_ANTI_FP
    assert "≤5M" in BG0_NORTH_STAR
    assert "skip" in BG0_NORTH_STAR.lower()
    assert "gibberish-tail" in BG0_SHIP_LOCK
    assert "TAC" in BG0_SHIP_LOCK
    assert "UNARYINT" in BG0_THESIS or "BG1" in BG0_THESIS
    assert "skip" in BG0_THESIS.lower()
    assert "unary" in BG0_THESIS.lower() or "BG-FOREVER" in BG0_THESIS


def test_given_ready_when_decide_then_promote() -> None:
    out = decide_bg0_session(trials_dir_ready=True, anti_fp_signed=True)
    assert out.startswith("PROMOTE")
    assert BG0_ID in out


def test_given_no_trials_when_decide_then_kill() -> None:
    out = decide_bg0_session(trials_dir_ready=False, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "trials" in out


def test_given_unsigned_anti_fp_when_decide_then_kill() -> None:
    out = decide_bg0_session(trials_dir_ready=True, anti_fp_signed=False)
    assert out.startswith("KILL")
    assert "anti-FP" in out


def test_given_incomplete_battery_when_decide_then_kill() -> None:
    bad = [dict(p) for p in BG0_ASK_BATTERY if p["expect_mode"] != "PEAK"]
    out = decide_bg0_session(
        trials_dir_ready=True, anti_fp_signed=True, battery=bad
    )
    assert out.startswith("KILL")
    assert "battery" in out.lower() or "modes" in out.lower()
