"""Contract: Wave BE0 SESSION — freeze BE-FOREVER/BA…BD-hold/util/gen-defer."""

from __future__ import annotations

from az_session_ops import AZ0_HELDOUT_FP_ROWS, AZ0_OVERREFUSE_ROWS
from ba_session_ops import BA0_FOREVER_ROWS
from bb_session_ops import BB0_FOREVER_ROWS
from bc_session_ops import BC0_FOREVER_ROWS
from bd_session_ops import BD0_FOREVER_ROWS
from be_session_ops import (
    BE0_ANTI_FP,
    BE0_ASK_BATTERY,
    BE0_AZ_HOLD_PROTOCOL,
    BE0_BA_HOLD_PROTOCOL,
    BE0_BB_HOLD_PROTOCOL,
    BE0_BC_HOLD_PROTOCOL,
    BE0_BD_HOLD_PROTOCOL,
    BE0_CITED_BD_LOCKS,
    BE0_CTX_BASELINE,
    BE0_FOREVER_PROTOCOL,
    BE0_FOREVER_ROWS,
    BE0_GEN_STANCE,
    BE0_ID,
    BE0_LATENCY_PATHS,
    BE0_MODES,
    BE0_NORTH_STAR,
    BE0_REAL_EVAL_PROTOCOL,
    BE0_SAFE_NOTE,
    BE0_SCOREBOARD,
    BE0_SHIP_LOCK,
    BE0_SPEED_BASELINE,
    BE0_THESIS,
    BE0_TRUE_GEN_JUDGE,
    BE0_UTIL_TRACK,
    decide_be0_session,
    map_be_product_mode,
)


def test_given_modes_when_map_then_lookup_peak_decode_abstain() -> None:
    # GIVEN/WHEN/THEN: pesquisa §9 BE0 — four product modes
    assert map_be_product_mode("WRAP_LOOKUP") == "LOOKUP"
    assert map_be_product_mode("SEMWRAP_LOOKUP") == "LOOKUP"
    assert map_be_product_mode("WRAP_DECODE") == "DECODE"
    assert map_be_product_mode("NO_ANSWER") == "ABSTAIN"
    assert map_be_product_mode("ABSTAIN") == "ABSTAIN"
    assert set(BE0_LATENCY_PATHS) == BE0_MODES
    assert "ABSTAIN" in BE0_MODES


def test_given_scoreboard_when_read_then_cites_bd_and_debts() -> None:
    # GIVEN BD locks · WHEN freeze scoreboard · THEN cite + ≥14 debts + bars
    cited = set(BE0_SCOREBOARD["cite_bd_locks"])
    assert cited == BE0_CITED_BD_LOCKS
    assert "H-SEMINT" in cited
    assert "H-NANOGEN14" in cited
    assert "BD-FREEZE" in cited
    debts = BE0_SCOREBOARD["debts"]
    ids = {d["id"] for d in debts}
    assert {
        "be_forever_false_hit_zero",
        "ba_forever_hold_zero",
        "bb_forever_hold_zero",
        "bc_forever_hold_zero",
        "bd_forever_hold_zero",
        "az_hold_zero",
        "overrefuse_exact_gold",
        "live_ask_scoreboard",
        "speed_baseline_publish",
        "ctx_baseline_publish",
        "mode_ui_always",
        "decode_content_law",
        "gen_defer_stance",
        "paraphrase_eval_rule",
        "utilization_track_a",
    } <= ids
    bars = BE0_SCOREBOARD["bars"]
    assert int(bars["be_forever_false_hit_max"]) == 0
    assert int(bars["ba_forever_false_hit_max"]) == 0
    assert int(bars["bb_forever_false_hit_max"]) == 0
    assert int(bars["bc_forever_false_hit_max"]) == 0
    assert int(bars["bd_forever_false_hit_max"]) == 0
    assert int(bars["az_hold_false_hit_max"]) == 0
    assert int(bars["overrefuse_miss_max"]) == 0
    assert int(bars["be_forever_min_n"]) >= 12
    assert int(bars["be_forever_classes_min"]) >= 3
    assert int(bars["novel_probes_min"]) >= 10
    assert bars["decode_gibberish_neq_content_ok"] is True
    assert bars["default_ask_intent_mismatch"] == "ABSTAIN"
    assert bars["default_ask_exact_gold"] == "LOOKUP"
    assert bars["eval_eq_prod_ask"] is True
    assert bars["pack_pass_neq_forever"] is True
    assert bars["ba_bb_bc_bd_pass_neq_be_forever"] is True
    assert bars["bank_stuff_forbidden"] is True
    assert bars["paraphrase_required"] is True
    assert bars["compositional_gate_preferred"] is True
    assert bars["regression_hold"] is True
    assert bars["speed_baseline_published"] is True
    assert bars["ctx_baseline_published"] is True
    assert bars["utilization_track_frozen"] is True
    assert bars["l_eff_alone_forbidden"] is True
    assert set(bars["modes_required"]) == BE0_MODES
    metrics = set(BE0_SCOREBOARD["metrics"])
    assert {
        "be_forever_false_hit",
        "ba_forever_false_hit",
        "bb_forever_false_hit",
        "bc_forever_false_hit",
        "bd_forever_false_hit",
        "az_hold_false_hit",
        "ctx_content_ok",
        "true_continue_ablated",
        "utilization_ok",
    } <= metrics


def test_given_forever_when_read_then_protocol_flags() -> None:
    assert BE0_FOREVER_PROTOCOL["held_out"] is True
    assert BE0_FOREVER_PROTOCOL["forever"] is True
    assert BE0_FOREVER_PROTOCOL["bank_stuff_forbidden"] is True
    assert BE0_FOREVER_PROTOCOL["paraphrase_required"] is True
    assert BE0_FOREVER_PROTOCOL["compositional_gate_preferred"] is True
    assert BE0_FOREVER_PROTOCOL["neq_ba_forever"] is True
    assert BE0_FOREVER_PROTOCOL["neq_bb_forever"] is True
    assert BE0_FOREVER_PROTOCOL["neq_bc_forever"] is True
    assert BE0_FOREVER_PROTOCOL["neq_bd_forever"] is True
    assert BE0_FOREVER_PROTOCOL["neq_az_heldout"] is True
    assert BE0_FOREVER_PROTOCOL["type_coercion_mismatch_is_false_hit"] is True
    assert BE0_FOREVER_PROTOCOL["pack_pass_neq_forever"] is True
    assert BE0_FOREVER_PROTOCOL["ba_bb_bc_bd_pass_neq_be_forever"] is True
    assert BE0_FOREVER_PROTOCOL["live_fp_id"] == "BE-FH-01"
    assert int(BE0_FOREVER_PROTOCOL["min_n"]) >= 12


def test_given_forever_when_read_then_type_coercion_classes() -> None:
    assert len(BE0_FOREVER_ROWS) >= 12
    ids = [p["id"] for p in BE0_FOREVER_ROWS]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("BE-FH-") for i in ids)
    assert all(str(p["question"]).strip() for p in BE0_FOREVER_ROWS)
    assert all(p["expect_mode"] == "ABSTAIN" for p in BE0_FOREVER_ROWS)
    classes = {p["class"] for p in BE0_FOREVER_ROWS}
    need = {"type_coercion", "type_coercion_para", "type_schema_neighbor"}
    assert need <= classes
    live = str(BE0_FOREVER_ROWS[0]["question"]).lower()
    assert "convert" in live and "string" in live and "integer" in live


def test_given_forever_when_scan_then_disjoint_from_ba_bb_bc_bd_az() -> None:
    prior = {str(p["question"]).strip() for p in BA0_FOREVER_ROWS}
    prior |= {str(p["question"]).strip() for p in BB0_FOREVER_ROWS}
    prior |= {str(p["question"]).strip() for p in BC0_FOREVER_ROWS}
    prior |= {str(p["question"]).strip() for p in BD0_FOREVER_ROWS}
    prior |= {str(p["question"]).strip() for p in AZ0_HELDOUT_FP_ROWS}
    prior |= {str(p["question"]).strip() for p in AZ0_OVERREFUSE_ROWS}
    be_q = {str(p["question"]).strip() for p in BE0_FOREVER_ROWS}
    assert prior.isdisjoint(be_q)


def test_given_hold_when_read_then_ba_bb_bc_bd_az_regression_bars() -> None:
    assert int(BE0_BA_HOLD_PROTOCOL["forever_false_hit_max"]) == 0
    assert BE0_BA_HOLD_PROTOCOL["regression_hold"] is True
    assert int(BE0_BA_HOLD_PROTOCOL["heldout_n"]) >= 15
    assert int(BE0_BB_HOLD_PROTOCOL["forever_false_hit_max"]) == 0
    assert BE0_BB_HOLD_PROTOCOL["regression_hold"] is True
    assert int(BE0_BB_HOLD_PROTOCOL["heldout_n"]) >= 15
    assert int(BE0_BC_HOLD_PROTOCOL["forever_false_hit_max"]) == 0
    assert BE0_BC_HOLD_PROTOCOL["regression_hold"] is True
    assert int(BE0_BC_HOLD_PROTOCOL["heldout_n"]) >= 18
    assert int(BE0_BD_HOLD_PROTOCOL["forever_false_hit_max"]) == 0
    assert BE0_BD_HOLD_PROTOCOL["regression_hold"] is True
    assert int(BE0_BD_HOLD_PROTOCOL["heldout_n"]) >= 12
    assert int(BE0_AZ_HOLD_PROTOCOL["heldout_false_hit_max"]) == 0
    assert int(BE0_AZ_HOLD_PROTOCOL["overrefuse_miss_max"]) == 0
    assert BE0_AZ_HOLD_PROTOCOL["regression_hold"] is True
    assert int(BE0_AZ_HOLD_PROTOCOL["heldout_n"]) >= 12
    assert int(BE0_AZ_HOLD_PROTOCOL["overrefuse_n"]) >= 3


def test_given_baselines_when_read_then_speed_ctx_and_util() -> None:
    paths = BE0_SPEED_BASELINE["paths"]
    assert set(paths) == BE0_MODES
    assert BE0_SPEED_BASELINE["quality_regress_forbidden"] is True
    assert "FASTGAIN" in str(BE0_SPEED_BASELINE["source"])
    assert BE0_CTX_BASELINE["l_eff_alone_insufficient"] is True
    assert BE0_CTX_BASELINE["content_bars_required"] is True
    assert "CTXBE" in str(BE0_CTX_BASELINE["be4_gate"])
    assert BE0_UTIL_TRACK["gpt_claim_forbidden"] is True
    assert BE0_UTIL_TRACK["known_ask_hitl"] is True
    assert len(BE0_UTIL_TRACK["checklist"]) >= 4
    assert "SHIPUSE" in str(BE0_UTIL_TRACK["be2_gate"])


def test_given_gen_stance_when_read_then_defer_not_nanogen15_rename() -> None:
    assert BE0_GEN_STANCE["stance"] == "defer"
    assert set(BE0_GEN_STANCE["allowed_stances"]) == {"M1", "M2", "M3", "defer"}
    assert BE0_GEN_STANCE["capcheck"] == "closed"
    assert BE0_GEN_STANCE["named_hyp"] == "H-NANOGEN15"
    assert BE0_GEN_STANCE["named_compint"] == "H-COMPINT"
    assert BE0_GEN_STANCE["named_shipuse"] == "H-SHIPUSE"
    assert BE0_GEN_STANCE["named_fast"] == "H-FASTBE"
    assert BE0_GEN_STANCE["named_ctx"] == "H-CTXBE"
    assert BE0_GEN_STANCE["nanogen15_rename_forbidden"] is True
    assert BE0_GEN_STANCE["nanogen14_defer_cited"] is True
    assert BE0_GEN_STANCE["defer_once_stop_rule"] is True
    assert BE0_GEN_STANCE["nanogen6_hold_cited"] is True
    methods = BE0_GEN_STANCE["method_candidates"]
    assert set(methods) == {"M1", "M2", "M3"}
    rat = str(BE0_GEN_STANCE["rationale"]).lower()
    assert "defer" in rat
    assert "nanogen" in rat
    judge = BE0_TRUE_GEN_JUDGE
    assert judge["span_fallback_neq_gen"] is True
    assert judge["nanogen15_rename_forbidden"] is True
    assert judge["nanogen14_defer_archived"] is True
    assert "true_continue" in str(judge["scoring"])


def test_given_real_eval_when_read_then_live_and_nanogen15_gated() -> None:
    assert BE0_REAL_EVAL_PROTOCOL["live_ask_battery"] is True
    assert BE0_REAL_EVAL_PROTOCOL["summary_only_forbidden"] is True
    assert BE0_REAL_EVAL_PROTOCOL["wall_ms_n_new_mandatory"] is True
    assert BE0_REAL_EVAL_PROTOCOL["eval_eq_prod_ask"] is True
    assert BE0_REAL_EVAL_PROTOCOL["intent_mismatch_is_false_hit"] is True
    assert BE0_REAL_EVAL_PROTOCOL["type_coercion_mismatch_is_false_hit"] is True
    assert BE0_REAL_EVAL_PROTOCOL["exact_gold_abstain_is_miss"] is True
    assert BE0_REAL_EVAL_PROTOCOL["gold_substring_neq_gen"] is True
    assert BE0_REAL_EVAL_PROTOCOL["gibberish_tail_fails"] is True
    assert BE0_REAL_EVAL_PROTOCOL["span_fallback_neq_gen"] is True
    assert BE0_REAL_EVAL_PROTOCOL["pack_pass_neq_forever"] is True
    assert BE0_REAL_EVAL_PROTOCOL["ba_bb_bc_bd_pass_neq_be_forever"] is True
    assert BE0_REAL_EVAL_PROTOCOL["utilization_scored"] is True
    assert int(BE0_REAL_EVAL_PROTOCOL["novel_probes_min"]) >= 10
    assert {
        "OK",
        "FP",
        "MISS",
        "ABSTAIN-OK",
    } <= set(BE0_REAL_EVAL_PROTOCOL["score_labels"])
    claim = str(BE0_REAL_EVAL_PROTOCOL["gen_claim_rule"]).lower()
    assert "nanogen15" in claim
    assert "rename" in claim


def test_given_battery_when_scan_then_covers_modes_and_debts() -> None:
    assert len(BE0_ASK_BATTERY) >= 4
    modes = {p["expect_mode"] for p in BE0_ASK_BATTERY}
    assert modes == BE0_MODES
    kinds = {p["kind"] for p in BE0_ASK_BATTERY}
    assert {
        "near_miss",
        "be_forever_type_fp",
        "be_forever_neighbor_fp",
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
    ids = [p["id"] for p in BE0_ASK_BATTERY]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("BE-ASK-") for i in ids)


def test_given_notes_when_read_then_anti_fp_and_north_star() -> None:
    assert "≠" in BE0_SAFE_NOTE
    assert "LOOKUP" in BE0_ANTI_FP
    assert "eval path = prod" in BE0_ANTI_FP.lower()
    assert "NANOGEN15" in BE0_ANTI_FP or "nanogen15" in BE0_ANTI_FP.lower()
    assert "type" in BE0_ANTI_FP.lower() or "BE-FOREVER" in BE0_ANTI_FP
    assert "≤5M" in BE0_NORTH_STAR
    assert "defer" in BE0_NORTH_STAR.lower()
    assert "gibberish-tail" in BE0_SHIP_LOCK
    assert "TAC" in BE0_SHIP_LOCK
    assert "COMPINT" in BE0_THESIS or "BE1" in BE0_THESIS
    assert "defer" in BE0_THESIS.lower()
    assert "type" in BE0_THESIS.lower() or "BE-FOREVER" in BE0_THESIS


def test_given_ready_when_decide_then_promote() -> None:
    out = decide_be0_session(trials_dir_ready=True, anti_fp_signed=True)
    assert out.startswith("PROMOTE")
    assert BE0_ID in out


def test_given_no_trials_when_decide_then_kill() -> None:
    out = decide_be0_session(trials_dir_ready=False, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "trials" in out


def test_given_unsigned_anti_fp_when_decide_then_kill() -> None:
    out = decide_be0_session(trials_dir_ready=True, anti_fp_signed=False)
    assert out.startswith("KILL")
    assert "anti-FP" in out


def test_given_incomplete_battery_when_decide_then_kill() -> None:
    bad = [dict(p) for p in BE0_ASK_BATTERY if p["expect_mode"] != "PEAK"]
    out = decide_be0_session(
        trials_dir_ready=True, anti_fp_signed=True, battery=bad
    )
    assert out.startswith("KILL")
    assert "battery" in out.lower() or "modes" in out.lower()
