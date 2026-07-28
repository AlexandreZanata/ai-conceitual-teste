"""Contract: Wave BF0 SESSION — freeze BF-FOREVER/BA…BE-hold/util/gen-SKIP."""

from __future__ import annotations

from az_session_ops import AZ0_HELDOUT_FP_ROWS, AZ0_OVERREFUSE_ROWS
from ba_session_ops import BA0_FOREVER_ROWS
from bb_session_ops import BB0_FOREVER_ROWS
from bc_session_ops import BC0_FOREVER_ROWS
from bd_session_ops import BD0_FOREVER_ROWS
from be_session_ops import BE0_FOREVER_ROWS
from bf_session_ops import (
    BF0_ANTI_FP,
    BF0_ASK_BATTERY,
    BF0_AZ_HOLD_PROTOCOL,
    BF0_BA_HOLD_PROTOCOL,
    BF0_BB_HOLD_PROTOCOL,
    BF0_BC_HOLD_PROTOCOL,
    BF0_BD_HOLD_PROTOCOL,
    BF0_BE_HOLD_PROTOCOL,
    BF0_CITED_BE_LOCKS,
    BF0_CTX_BASELINE,
    BF0_FOREVER_PROTOCOL,
    BF0_FOREVER_ROWS,
    BF0_GEN_STANCE,
    BF0_ID,
    BF0_LATENCY_PATHS,
    BF0_MODES,
    BF0_NORTH_STAR,
    BF0_REAL_EVAL_PROTOCOL,
    BF0_SAFE_NOTE,
    BF0_SCOREBOARD,
    BF0_SHIP_LOCK,
    BF0_SPEED_BASELINE,
    BF0_THESIS,
    BF0_TRUE_GEN_JUDGE,
    BF0_UTIL_TRACK,
    decide_bf0_session,
    map_bf_product_mode,
)


def test_given_modes_when_map_then_lookup_peak_decode_abstain() -> None:
    # GIVEN/WHEN/THEN: pesquisa §9 BF0 — four product modes
    assert map_bf_product_mode("WRAP_LOOKUP") == "LOOKUP"
    assert map_bf_product_mode("SEMWRAP_LOOKUP") == "LOOKUP"
    assert map_bf_product_mode("WRAP_DECODE") == "DECODE"
    assert map_bf_product_mode("NO_ANSWER") == "ABSTAIN"
    assert map_bf_product_mode("ABSTAIN") == "ABSTAIN"
    assert set(BF0_LATENCY_PATHS) == BF0_MODES
    assert "ABSTAIN" in BF0_MODES


def test_given_scoreboard_when_read_then_cites_be_and_debts() -> None:
    # GIVEN BE locks · WHEN freeze scoreboard · THEN cite + ≥15 debts + bars
    cited = set(BF0_SCOREBOARD["cite_be_locks"])
    assert cited == BF0_CITED_BE_LOCKS
    assert "H-COMPINT" in cited
    assert "H-NANOGEN15" in cited
    assert "BE-FREEZE" in cited
    debts = BF0_SCOREBOARD["debts"]
    ids = {d["id"] for d in debts}
    assert {
        "bf_forever_false_hit_zero",
        "ba_forever_hold_zero",
        "bb_forever_hold_zero",
        "bc_forever_hold_zero",
        "bd_forever_hold_zero",
        "be_forever_hold_zero",
        "az_hold_zero",
        "overrefuse_exact_gold",
        "live_ask_scoreboard",
        "speed_baseline_publish",
        "ctx_baseline_publish",
        "mode_ui_always",
        "decode_content_law",
        "gen_skip_stance",
        "paraphrase_eval_rule",
        "utilization_track_a_plus",
    } <= ids
    bars = BF0_SCOREBOARD["bars"]
    assert int(bars["bf_forever_false_hit_max"]) == 0
    assert int(bars["ba_forever_false_hit_max"]) == 0
    assert int(bars["bb_forever_false_hit_max"]) == 0
    assert int(bars["bc_forever_false_hit_max"]) == 0
    assert int(bars["bd_forever_false_hit_max"]) == 0
    assert int(bars["be_forever_false_hit_max"]) == 0
    assert int(bars["az_hold_false_hit_max"]) == 0
    assert int(bars["overrefuse_miss_max"]) == 0
    assert int(bars["bf_forever_min_n"]) >= 12
    assert int(bars["bf_forever_classes_min"]) >= 3
    assert int(bars["novel_probes_min"]) >= 10
    assert bars["decode_gibberish_neq_content_ok"] is True
    assert bars["default_ask_intent_mismatch"] == "ABSTAIN"
    assert bars["default_ask_exact_gold"] == "LOOKUP"
    assert bars["eval_eq_prod_ask"] is True
    assert bars["pack_pass_neq_forever"] is True
    assert bars["ba_bb_bc_bd_be_pass_neq_bf_forever"] is True
    assert bars["bank_stuff_forbidden"] is True
    assert bars["paraphrase_required"] is True
    assert bars["predicate_gate_preferred"] is True
    assert bars["regression_hold"] is True
    assert bars["speed_baseline_published"] is True
    assert bars["ctx_baseline_published"] is True
    assert bars["utilization_track_frozen"] is True
    assert bars["l_eff_alone_forbidden"] is True
    assert set(bars["modes_required"]) == BF0_MODES
    metrics = set(BF0_SCOREBOARD["metrics"])
    assert {
        "bf_forever_false_hit",
        "ba_forever_false_hit",
        "bb_forever_false_hit",
        "bc_forever_false_hit",
        "bd_forever_false_hit",
        "be_forever_false_hit",
        "az_hold_false_hit",
        "ctx_content_ok",
        "true_continue_ablated",
        "utilization_ok",
    } <= metrics


def test_given_forever_when_read_then_protocol_flags() -> None:
    assert BF0_FOREVER_PROTOCOL["held_out"] is True
    assert BF0_FOREVER_PROTOCOL["forever"] is True
    assert BF0_FOREVER_PROTOCOL["bank_stuff_forbidden"] is True
    assert BF0_FOREVER_PROTOCOL["paraphrase_required"] is True
    assert BF0_FOREVER_PROTOCOL["predicate_gate_preferred"] is True
    assert BF0_FOREVER_PROTOCOL["neq_ba_forever"] is True
    assert BF0_FOREVER_PROTOCOL["neq_bb_forever"] is True
    assert BF0_FOREVER_PROTOCOL["neq_bc_forever"] is True
    assert BF0_FOREVER_PROTOCOL["neq_bd_forever"] is True
    assert BF0_FOREVER_PROTOCOL["neq_be_forever"] is True
    assert BF0_FOREVER_PROTOCOL["neq_az_heldout"] is True
    assert BF0_FOREVER_PROTOCOL["predicate_mismatch_is_false_hit"] is True
    assert BF0_FOREVER_PROTOCOL["pack_pass_neq_forever"] is True
    assert BF0_FOREVER_PROTOCOL["ba_bb_bc_bd_be_pass_neq_bf_forever"] is True
    assert BF0_FOREVER_PROTOCOL["live_fp_id"] == "BF-FH-01"
    assert int(BF0_FOREVER_PROTOCOL["min_n"]) >= 12


def test_given_forever_when_read_then_predicate_classes() -> None:
    assert len(BF0_FOREVER_ROWS) >= 12
    ids = [p["id"] for p in BF0_FOREVER_ROWS]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("BF-FH-") for i in ids)
    assert all(str(p["question"]).strip() for p in BF0_FOREVER_ROWS)
    assert all(p["expect_mode"] == "ABSTAIN" for p in BF0_FOREVER_ROWS)
    classes = {p["class"] for p in BF0_FOREVER_ROWS}
    need = {
        "predicate_boolean",
        "predicate_boolean_para",
        "predicate_schema_neighbor",
    }
    assert need <= classes
    live = str(BF0_FOREVER_ROWS[0]["question"]).lower()
    assert "even" in live and "true" in live


def test_given_forever_when_scan_then_disjoint_from_ba_bb_bc_bd_be_az() -> None:
    prior = {str(p["question"]).strip() for p in BA0_FOREVER_ROWS}
    prior |= {str(p["question"]).strip() for p in BB0_FOREVER_ROWS}
    prior |= {str(p["question"]).strip() for p in BC0_FOREVER_ROWS}
    prior |= {str(p["question"]).strip() for p in BD0_FOREVER_ROWS}
    prior |= {str(p["question"]).strip() for p in BE0_FOREVER_ROWS}
    prior |= {str(p["question"]).strip() for p in AZ0_HELDOUT_FP_ROWS}
    prior |= {str(p["question"]).strip() for p in AZ0_OVERREFUSE_ROWS}
    bf_q = {str(p["question"]).strip() for p in BF0_FOREVER_ROWS}
    assert prior.isdisjoint(bf_q)


def test_given_hold_when_read_then_ba_bb_bc_bd_be_az_regression_bars() -> None:
    assert int(BF0_BA_HOLD_PROTOCOL["forever_false_hit_max"]) == 0
    assert BF0_BA_HOLD_PROTOCOL["regression_hold"] is True
    assert int(BF0_BA_HOLD_PROTOCOL["heldout_n"]) >= 15
    assert int(BF0_BB_HOLD_PROTOCOL["forever_false_hit_max"]) == 0
    assert BF0_BB_HOLD_PROTOCOL["regression_hold"] is True
    assert int(BF0_BB_HOLD_PROTOCOL["heldout_n"]) >= 15
    assert int(BF0_BC_HOLD_PROTOCOL["forever_false_hit_max"]) == 0
    assert BF0_BC_HOLD_PROTOCOL["regression_hold"] is True
    assert int(BF0_BC_HOLD_PROTOCOL["heldout_n"]) >= 18
    assert int(BF0_BD_HOLD_PROTOCOL["forever_false_hit_max"]) == 0
    assert BF0_BD_HOLD_PROTOCOL["regression_hold"] is True
    assert int(BF0_BD_HOLD_PROTOCOL["heldout_n"]) >= 12
    assert int(BF0_BE_HOLD_PROTOCOL["forever_false_hit_max"]) == 0
    assert BF0_BE_HOLD_PROTOCOL["regression_hold"] is True
    assert int(BF0_BE_HOLD_PROTOCOL["heldout_n"]) >= 12
    assert int(BF0_AZ_HOLD_PROTOCOL["heldout_false_hit_max"]) == 0
    assert int(BF0_AZ_HOLD_PROTOCOL["overrefuse_miss_max"]) == 0
    assert BF0_AZ_HOLD_PROTOCOL["regression_hold"] is True
    assert int(BF0_AZ_HOLD_PROTOCOL["heldout_n"]) >= 12
    assert int(BF0_AZ_HOLD_PROTOCOL["overrefuse_n"]) >= 3


def test_given_baselines_when_read_then_speed_ctx_and_util() -> None:
    paths = BF0_SPEED_BASELINE["paths"]
    assert set(paths) == BF0_MODES
    assert BF0_SPEED_BASELINE["quality_regress_forbidden"] is True
    assert "FASTBE" in str(BF0_SPEED_BASELINE["source"])
    assert BF0_CTX_BASELINE["l_eff_alone_insufficient"] is True
    assert BF0_CTX_BASELINE["content_bars_required"] is True
    assert "CTXBF" in str(BF0_CTX_BASELINE["bf4_gate"])
    assert BF0_UTIL_TRACK["gpt_claim_forbidden"] is True
    assert BF0_UTIL_TRACK["known_ask_hitl"] is True
    assert len(BF0_UTIL_TRACK["checklist"]) >= 4
    assert "SHIPUSE2" in str(BF0_UTIL_TRACK["bf2_gate"])


def test_given_gen_stance_when_read_then_skip_not_nanogen16_rename() -> None:
    assert BF0_GEN_STANCE["stance"] == "skip"
    assert set(BF0_GEN_STANCE["allowed_stances"]) == {"M1", "M2", "M3", "skip"}
    assert BF0_GEN_STANCE["method_plan_attached"] is False
    assert BF0_GEN_STANCE["capcheck"] == "closed"
    assert BF0_GEN_STANCE["named_hyp"] == "H-NANOGEN16"
    assert BF0_GEN_STANCE["named_predint"] == "H-PREDINT"
    assert BF0_GEN_STANCE["named_shipuse2"] == "H-SHIPUSE2"
    assert BF0_GEN_STANCE["named_fast"] == "H-FASTBF"
    assert BF0_GEN_STANCE["named_ctx"] == "H-CTXBF"
    assert BF0_GEN_STANCE["nanogen16_rename_forbidden"] is True
    assert BF0_GEN_STANCE["nanogen16_without_plan_forbidden"] is True
    assert BF0_GEN_STANCE["skip_gen_stop_rule"] is True
    assert BF0_GEN_STANCE["nanogen15_defer_cited"] is True
    methods = BF0_GEN_STANCE["method_candidates"]
    assert set(methods) == {"M1", "M2", "M3"}
    rat = str(BF0_GEN_STANCE["rationale"]).lower()
    assert "skip" in rat
    assert "nanogen" in rat
    judge = BF0_TRUE_GEN_JUDGE
    assert judge["span_fallback_neq_gen"] is True
    assert judge["nanogen16_without_plan_forbidden"] is True
    assert "true_continue" in str(judge["scoring"])


def test_given_real_eval_when_read_then_live_and_nanogen16_gated() -> None:
    assert BF0_REAL_EVAL_PROTOCOL["live_ask_battery"] is True
    assert BF0_REAL_EVAL_PROTOCOL["summary_only_forbidden"] is True
    assert BF0_REAL_EVAL_PROTOCOL["wall_ms_n_new_mandatory"] is True
    assert BF0_REAL_EVAL_PROTOCOL["eval_eq_prod_ask"] is True
    assert BF0_REAL_EVAL_PROTOCOL["intent_mismatch_is_false_hit"] is True
    assert BF0_REAL_EVAL_PROTOCOL["predicate_mismatch_is_false_hit"] is True
    assert BF0_REAL_EVAL_PROTOCOL["exact_gold_abstain_is_miss"] is True
    assert BF0_REAL_EVAL_PROTOCOL["gold_substring_neq_gen"] is True
    assert BF0_REAL_EVAL_PROTOCOL["gibberish_tail_fails"] is True
    assert BF0_REAL_EVAL_PROTOCOL["span_fallback_neq_gen"] is True
    assert BF0_REAL_EVAL_PROTOCOL["pack_pass_neq_forever"] is True
    assert BF0_REAL_EVAL_PROTOCOL["ba_bb_bc_bd_be_pass_neq_bf_forever"] is True
    assert BF0_REAL_EVAL_PROTOCOL["utilization_scored"] is True
    assert int(BF0_REAL_EVAL_PROTOCOL["novel_probes_min"]) >= 10
    assert {
        "OK",
        "FP",
        "MISS",
        "ABSTAIN-OK",
    } <= set(BF0_REAL_EVAL_PROTOCOL["score_labels"])
    claim = str(BF0_REAL_EVAL_PROTOCOL["gen_claim_rule"]).lower()
    assert "nanogen16" in claim
    assert "skip" in claim


def test_given_battery_when_scan_then_covers_modes_and_debts() -> None:
    assert len(BF0_ASK_BATTERY) >= 4
    modes = {p["expect_mode"] for p in BF0_ASK_BATTERY}
    assert modes == BF0_MODES
    kinds = {p["kind"] for p in BF0_ASK_BATTERY}
    assert {
        "near_miss",
        "bf_forever_predicate_fp",
        "bf_forever_neighbor_fp",
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
    ids = [p["id"] for p in BF0_ASK_BATTERY]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("BF-ASK-") for i in ids)


def test_given_notes_when_read_then_anti_fp_and_north_star() -> None:
    assert "≠" in BF0_SAFE_NOTE
    assert "LOOKUP" in BF0_ANTI_FP
    assert "eval path = prod" in BF0_ANTI_FP.lower()
    assert "NANOGEN16" in BF0_ANTI_FP or "nanogen16" in BF0_ANTI_FP.lower()
    assert "predicate" in BF0_ANTI_FP.lower() or "BF-FOREVER" in BF0_ANTI_FP
    assert "≤5M" in BF0_NORTH_STAR
    assert "skip" in BF0_NORTH_STAR.lower()
    assert "gibberish-tail" in BF0_SHIP_LOCK
    assert "TAC" in BF0_SHIP_LOCK
    assert "PREDINT" in BF0_THESIS or "BF1" in BF0_THESIS
    assert "skip" in BF0_THESIS.lower()
    assert "predicate" in BF0_THESIS.lower() or "BF-FOREVER" in BF0_THESIS


def test_given_ready_when_decide_then_promote() -> None:
    out = decide_bf0_session(trials_dir_ready=True, anti_fp_signed=True)
    assert out.startswith("PROMOTE")
    assert BF0_ID in out


def test_given_no_trials_when_decide_then_kill() -> None:
    out = decide_bf0_session(trials_dir_ready=False, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "trials" in out


def test_given_unsigned_anti_fp_when_decide_then_kill() -> None:
    out = decide_bf0_session(trials_dir_ready=True, anti_fp_signed=False)
    assert out.startswith("KILL")
    assert "anti-FP" in out


def test_given_incomplete_battery_when_decide_then_kill() -> None:
    bad = [dict(p) for p in BF0_ASK_BATTERY if p["expect_mode"] != "PEAK"]
    out = decide_bf0_session(
        trials_dir_ready=True, anti_fp_signed=True, battery=bad
    )
    assert out.startswith("KILL")
    assert "battery" in out.lower() or "modes" in out.lower()
