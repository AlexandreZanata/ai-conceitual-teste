"""Contract: Wave BH0 SESSION — freeze IQ battery plan / gold holes / BA…BG hold."""

from __future__ import annotations

from az_session_ops import AZ0_HELDOUT_FP_ROWS, AZ0_OVERREFUSE_ROWS
from ba_session_ops import BA0_FOREVER_ROWS
from bb_session_ops import BB0_FOREVER_ROWS
from bc_session_ops import BC0_FOREVER_ROWS
from bd_session_ops import BD0_FOREVER_ROWS
from be_session_ops import BE0_FOREVER_ROWS
from bf_session_ops import BF0_FOREVER_ROWS
from bg_session_ops import BG0_FOREVER_ROWS
from bh_session_ops import (
    BH0_ANTI_FP,
    BH0_ASK_BATTERY,
    BH0_AZ_HOLD_PROTOCOL,
    BH0_BA_HOLD_PROTOCOL,
    BH0_BB_HOLD_PROTOCOL,
    BH0_BC_HOLD_PROTOCOL,
    BH0_BD_HOLD_PROTOCOL,
    BH0_BE_HOLD_PROTOCOL,
    BH0_BF_HOLD_PROTOCOL,
    BH0_BG_HOLD_PROTOCOL,
    BH0_CITED_BG_LOCKS,
    BH0_CTX_BASELINE,
    BH0_GEN_STANCE,
    BH0_GOLD_HOLES,
    BH0_ID,
    BH0_IQ_BATTERY_PROTOCOL,
    BH0_IQ_SEED_ROWS,
    BH0_LATENCY_PATHS,
    BH0_MODES,
    BH0_NORTH_STAR,
    BH0_REAL_EVAL_PROTOCOL,
    BH0_SAFE_NOTE,
    BH0_SCOREBOARD,
    BH0_SHIP_LOCK,
    BH0_SPEED_BASELINE,
    BH0_THESIS,
    BH0_TRUE_GEN_JUDGE,
    BH0_UTIL_TRACK,
    decide_bh0_session,
    map_bh_product_mode,
)


def test_given_modes_when_map_then_lookup_peak_decode_abstain() -> None:
    # GIVEN/WHEN/THEN: pesquisa §9 BH0 — four product modes
    assert map_bh_product_mode("WRAP_LOOKUP") == "LOOKUP"
    assert map_bh_product_mode("SEMWRAP_LOOKUP") == "LOOKUP"
    assert map_bh_product_mode("WRAP_DECODE") == "DECODE"
    assert map_bh_product_mode("NO_ANSWER") == "ABSTAIN"
    assert map_bh_product_mode("ABSTAIN") == "ABSTAIN"
    assert set(BH0_LATENCY_PATHS) == BH0_MODES
    assert "ABSTAIN" in BH0_MODES


def test_given_scoreboard_when_read_then_cites_bg_and_debts() -> None:
    # GIVEN BG locks · WHEN freeze scoreboard · THEN cite + ≥16 debts + bars
    cited = set(BH0_SCOREBOARD["cite_bg_locks"])
    assert cited == BH0_CITED_BG_LOCKS
    assert "H-UNARYINT" in cited
    assert "H-NANOGEN17" in cited
    assert "BG-FREEZE" in cited
    debts = BH0_SCOREBOARD["debts"]
    ids = {d["id"] for d in debts}
    assert {
        "iq_battery_v0",
        "rust_gold_miss",
        "add_truncation_miss",
        "ba_forever_hold_zero",
        "bb_forever_hold_zero",
        "bc_forever_hold_zero",
        "bd_forever_hold_zero",
        "be_forever_hold_zero",
        "bf_forever_hold_zero",
        "bg_forever_hold_zero",
        "az_hold_zero",
        "live_ask_scoreboard",
        "speed_baseline_publish",
        "ctx_baseline_publish",
        "mode_ui_always",
        "decode_content_law",
        "gen_skip_stance",
        "utilization_track_a_plus_plus",
    } <= ids
    bars = BH0_SCOREBOARD["bars"]
    assert int(bars["iq_battery_min_n"]) >= 40
    assert int(bars["novel_fp_max"]) == 0
    assert int(bars["gold_miss_max"]) == 0
    assert int(bars["gold_rust_miss_max"]) == 0
    assert int(bars["gold_add_truncation_miss_max"]) == 0
    assert int(bars["ba_forever_false_hit_max"]) == 0
    assert int(bars["bg_forever_false_hit_max"]) == 0
    assert int(bars["az_hold_false_hit_max"]) == 0
    assert int(bars["overrefuse_miss_max"]) == 0
    assert int(bars["novel_probes_min"]) >= 10
    assert bars["decode_gibberish_neq_content_ok"] is True
    assert bars["default_ask_intent_mismatch"] == "ABSTAIN"
    assert bars["default_ask_exact_gold"] == "LOOKUP"
    assert bars["truncated_gold_is_miss"] is True
    assert bars["eval_eq_prod_ask"] is True
    assert bars["pack_pass_neq_iq"] is True
    assert bars["bank_stuff_forbidden"] is True
    assert bars["iq_battery_plan_frozen"] is True
    assert bars["gold_holes_frozen"] is True
    assert bars["utilization_track_frozen"] is True
    assert set(bars["modes_required"]) == BH0_MODES
    metrics = set(BH0_SCOREBOARD["metrics"])
    assert {
        "iq_score",
        "novel_fp",
        "gold_miss_rate",
        "bg_forever_false_hit",
        "ctx_content_ok",
        "true_continue_ablated",
        "utilization_ok",
    } <= metrics


def test_given_iq_protocol_when_read_then_v0_mix_and_schema() -> None:
    # GIVEN pesquisa §0c · WHEN freeze IQ plan · THEN v0 mix ≥40 + schema
    assert BH0_IQ_BATTERY_PROTOCOL["version"] == "v0"
    assert int(BH0_IQ_BATTERY_PROTOCOL["mix_min"]["total"]) >= 40
    assert int(BH0_IQ_BATTERY_PROTOCOL["mix_min"]["novel"]) >= 10
    assert int(BH0_IQ_BATTERY_PROTOCOL["mix_min"]["gold"]) >= 8
    splits = set(BH0_IQ_BATTERY_PROTOCOL["splits_required"])
    assert {
        "gold",
        "para",
        "forever",
        "adversary",
        "novel",
        "ood",
        "gen",
    } <= splits
    fields = set(BH0_IQ_BATTERY_PROTOCOL["schema_fields"])
    assert {
        "id",
        "split",
        "family",
        "expect",
        "question",
        "min_gold_substr",
    } <= fields
    assert BH0_IQ_BATTERY_PROTOCOL["pack_pass_neq_iq"] is True
    assert BH0_IQ_BATTERY_PROTOCOL["eval_eq_prod_ask"] is True
    assert BH0_IQ_BATTERY_PROTOCOL["read_completion_text"] is True
    assert BH0_IQ_BATTERY_PROTOCOL["bank_stuff_forbidden"] is True
    assert {
        "OK",
        "FP",
        "MISS",
        "ABSTAIN-OK",
    } <= set(BH0_IQ_BATTERY_PROTOCOL["score_labels"])
    assert BH0_IQ_BATTERY_PROTOCOL["promote_requires"]["Novel_FP"] == 0
    assert "iq-battery" in str(BH0_IQ_BATTERY_PROTOCOL["runner_target"])


def test_given_iq_seed_when_scan_then_covers_splits_and_gold_holes() -> None:
    assert len(BH0_IQ_SEED_ROWS) >= 10
    ids = [str(p["id"]) for p in BH0_IQ_SEED_ROWS]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("IQ-") for i in ids)
    splits = {str(p["split"]) for p in BH0_IQ_SEED_ROWS}
    assert {"gold", "forever", "adversary", "novel", "ood", "gen"} <= splits
    gold = [p for p in BH0_IQ_SEED_ROWS if p["split"] == "gold"]
    assert any(p["family"] == "rust_gold" for p in gold)
    assert any(p["family"] == "binary_add" for p in gold)
    add = next(p for p in gold if p["family"] == "binary_add")
    assert "a + b" in list(add["min_gold_substr"])


def test_given_gold_holes_when_read_then_rust_and_add_truncation() -> None:
    holes = BH0_GOLD_HOLES["holes"]
    ids = {h["id"] for h in holes}
    assert {"BH-GOLD-01", "BH-GOLD-02"} <= ids
    rust = next(h for h in holes if h["id"] == "BH-GOLD-01")
    add = next(h for h in holes if h["id"] == "BH-GOLD-02")
    assert rust["expect"] == "LOOKUP"
    assert rust["live_mode"] == "ABSTAIN"
    assert add["expect"] == "LOOKUP"
    assert "a + b" in list(add["min_gold_substr"])
    assert BH0_GOLD_HOLES["anti_fp_hold_required"] is True
    assert BH0_GOLD_HOLES["bank_stuff_forbidden"] is True
    assert "GOLDFIX" in str(BH0_GOLD_HOLES["bh2_gate"])


def test_given_hold_when_read_then_ba_through_bg_az_regression_bars() -> None:
    assert int(BH0_BA_HOLD_PROTOCOL["forever_false_hit_max"]) == 0
    assert BH0_BA_HOLD_PROTOCOL["regression_hold"] is True
    assert int(BH0_BA_HOLD_PROTOCOL["heldout_n"]) >= 15
    assert int(BH0_BB_HOLD_PROTOCOL["heldout_n"]) >= 15
    assert int(BH0_BC_HOLD_PROTOCOL["heldout_n"]) >= 18
    assert int(BH0_BD_HOLD_PROTOCOL["heldout_n"]) >= 12
    assert int(BH0_BE_HOLD_PROTOCOL["heldout_n"]) >= 12
    assert int(BH0_BF_HOLD_PROTOCOL["heldout_n"]) >= 12
    assert int(BH0_BG_HOLD_PROTOCOL["forever_false_hit_max"]) == 0
    assert BH0_BG_HOLD_PROTOCOL["regression_hold"] is True
    assert int(BH0_BG_HOLD_PROTOCOL["heldout_n"]) >= 12
    assert int(BH0_AZ_HOLD_PROTOCOL["heldout_false_hit_max"]) == 0
    assert int(BH0_AZ_HOLD_PROTOCOL["overrefuse_miss_max"]) == 0
    assert BH0_AZ_HOLD_PROTOCOL["regression_hold"] is True
    assert int(BH0_AZ_HOLD_PROTOCOL["heldout_n"]) >= 12
    assert int(BH0_AZ_HOLD_PROTOCOL["overrefuse_n"]) >= 3
    assert len(BA0_FOREVER_ROWS) >= 15
    assert len(BG0_FOREVER_ROWS) >= 12
    assert len(AZ0_HELDOUT_FP_ROWS) >= 12
    assert len(AZ0_OVERREFUSE_ROWS) >= 3
    assert len(BB0_FOREVER_ROWS) >= 15
    assert len(BC0_FOREVER_ROWS) >= 18
    assert len(BD0_FOREVER_ROWS) >= 12
    assert len(BE0_FOREVER_ROWS) >= 12
    assert len(BF0_FOREVER_ROWS) >= 12


def test_given_baselines_when_read_then_speed_ctx_and_util() -> None:
    paths = BH0_SPEED_BASELINE["paths"]
    assert set(paths) == BH0_MODES
    assert BH0_SPEED_BASELINE["quality_regress_forbidden"] is True
    assert "FASTBG" in str(BH0_SPEED_BASELINE["source"])
    assert BH0_CTX_BASELINE["l_eff_alone_insufficient"] is True
    assert BH0_CTX_BASELINE["content_bars_required"] is True
    assert "CTXBH" in str(BH0_CTX_BASELINE["bh5_gate"])
    assert BH0_UTIL_TRACK["gpt_claim_forbidden"] is True
    assert BH0_UTIL_TRACK["known_ask_hitl"] is True
    assert BH0_UTIL_TRACK["paper_arxiv_sync"] is True
    assert BH0_UTIL_TRACK["iq_battery_cited_in_paper"] is True
    assert len(BH0_UTIL_TRACK["checklist"]) >= 4
    assert "SHIPIQ" in str(BH0_UTIL_TRACK["bh3_gate"])


def test_given_gen_stance_when_read_then_skip_not_nanogen18_rename() -> None:
    assert BH0_GEN_STANCE["stance"] == "skip"
    assert set(BH0_GEN_STANCE["allowed_stances"]) == {"M1", "M2", "M3", "skip"}
    assert BH0_GEN_STANCE["method_plan_attached"] is False
    assert BH0_GEN_STANCE["capcheck"] == "closed"
    assert BH0_GEN_STANCE["named_hyp"] == "H-NANOGEN18"
    assert BH0_GEN_STANCE["named_iqbat"] == "H-IQBAT"
    assert BH0_GEN_STANCE["named_goldfix"] == "H-GOLDFIX"
    assert BH0_GEN_STANCE["named_shipiq"] == "H-SHIPIQ"
    assert BH0_GEN_STANCE["named_fast"] == "H-FASTBH"
    assert BH0_GEN_STANCE["named_ctx"] == "H-CTXBH"
    assert BH0_GEN_STANCE["nanogen18_rename_forbidden"] is True
    assert BH0_GEN_STANCE["nanogen18_without_plan_forbidden"] is True
    assert BH0_GEN_STANCE["skip_gen_stop_rule"] is True
    assert BH0_GEN_STANCE["nanogen17_skip_cited"] is True
    methods = BH0_GEN_STANCE["method_candidates"]
    assert set(methods) == {"M1", "M2", "M3"}
    rat = str(BH0_GEN_STANCE["rationale"]).lower()
    assert "skip" in rat
    assert "nanogen" in rat
    judge = BH0_TRUE_GEN_JUDGE
    assert judge["span_fallback_neq_gen"] is True
    assert judge["nanogen18_without_plan_forbidden"] is True
    assert "true_continue" in str(judge["scoring"])


def test_given_real_eval_when_read_then_iq_and_nanogen18_gated() -> None:
    assert BH0_REAL_EVAL_PROTOCOL["live_ask_battery"] is True
    assert BH0_REAL_EVAL_PROTOCOL["iq_battery_required"] is True
    assert BH0_REAL_EVAL_PROTOCOL["summary_only_forbidden"] is True
    assert BH0_REAL_EVAL_PROTOCOL["wall_ms_n_new_mandatory"] is True
    assert BH0_REAL_EVAL_PROTOCOL["eval_eq_prod_ask"] is True
    assert BH0_REAL_EVAL_PROTOCOL["read_completion_text"] is True
    assert BH0_REAL_EVAL_PROTOCOL["truncated_gold_is_miss"] is True
    assert BH0_REAL_EVAL_PROTOCOL["exact_gold_abstain_is_miss"] is True
    assert BH0_REAL_EVAL_PROTOCOL["intent_mismatch_is_false_hit"] is True
    assert BH0_REAL_EVAL_PROTOCOL["gold_substring_neq_gen"] is True
    assert BH0_REAL_EVAL_PROTOCOL["gibberish_tail_fails"] is True
    assert BH0_REAL_EVAL_PROTOCOL["span_fallback_neq_gen"] is True
    assert BH0_REAL_EVAL_PROTOCOL["pack_pass_neq_iq"] is True
    assert BH0_REAL_EVAL_PROTOCOL["utilization_scored"] is True
    assert int(BH0_REAL_EVAL_PROTOCOL["novel_probes_min"]) >= 10
    assert {
        "OK",
        "FP",
        "MISS",
        "ABSTAIN-OK",
    } <= set(BH0_REAL_EVAL_PROTOCOL["score_labels"])
    claim = str(BH0_REAL_EVAL_PROTOCOL["gen_claim_rule"]).lower()
    assert "nanogen18" in claim
    assert "skip" in claim


def test_given_battery_when_scan_then_covers_modes_and_gold_debts() -> None:
    assert len(BH0_ASK_BATTERY) >= 4
    modes = {p["expect_mode"] for p in BH0_ASK_BATTERY}
    assert modes == BH0_MODES
    kinds = {p["kind"] for p in BH0_ASK_BATTERY}
    assert {
        "near_miss",
        "gold_rust_miss",
        "known_lookup_add",
        "bg_forever_hold",
        "bg_forever_transform",
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
        "novel_cube",
    } <= kinds
    ids = [p["id"] for p in BH0_ASK_BATTERY]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("BH-ASK-") for i in ids)


def test_given_notes_when_read_then_anti_fp_and_north_star() -> None:
    assert "≠" in BH0_SAFE_NOTE
    assert "LOOKUP" in BH0_ANTI_FP
    assert "eval path = prod" in BH0_ANTI_FP.lower()
    assert "NANOGEN18" in BH0_ANTI_FP or "nanogen18" in BH0_ANTI_FP.lower()
    assert "IQ" in BH0_ANTI_FP or "iq" in BH0_ANTI_FP.lower()
    assert "≤5M" in BH0_NORTH_STAR
    assert "skip" in BH0_NORTH_STAR.lower()
    assert "gibberish-tail" in BH0_SHIP_LOCK
    assert "TAC" in BH0_SHIP_LOCK
    assert "IQ" in BH0_THESIS or "iq" in BH0_THESIS.lower()
    assert "skip" in BH0_THESIS.lower()
    assert "gold" in BH0_THESIS.lower()


def test_given_ready_when_decide_then_promote() -> None:
    out = decide_bh0_session(trials_dir_ready=True, anti_fp_signed=True)
    assert out.startswith("PROMOTE")
    assert BH0_ID in out


def test_given_no_trials_when_decide_then_kill() -> None:
    out = decide_bh0_session(trials_dir_ready=False, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "trials" in out


def test_given_unsigned_anti_fp_when_decide_then_kill() -> None:
    out = decide_bh0_session(trials_dir_ready=True, anti_fp_signed=False)
    assert out.startswith("KILL")
    assert "anti-FP" in out


def test_given_incomplete_battery_when_decide_then_kill() -> None:
    bad = [dict(p) for p in BH0_ASK_BATTERY if p["expect_mode"] != "PEAK"]
    out = decide_bh0_session(
        trials_dir_ready=True, anti_fp_signed=True, battery=bad
    )
    assert out.startswith("KILL")
    assert "battery" in out.lower() or "modes" in out.lower()
