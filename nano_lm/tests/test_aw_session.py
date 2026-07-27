"""Contract: Wave AW0 SESSION — freeze product-keep/pressure-para/NANOGEN7 TAC/eval."""

from __future__ import annotations

from au_session_ops import AU0_HUMAN_PARA_ROWS
from av_session_ops import AV0_EXTERNAL_PARA_ROWS
from aw_session_ops import (
    AW0_ANTI_FP,
    AW0_ASK_BATTERY,
    AW0_CITED_AV_LOCKS,
    AW0_ID,
    AW0_LATENCY_PATHS,
    AW0_MODES,
    AW0_NANOGEN7_HYPOTHESIS,
    AW0_NORTH_STAR,
    AW0_PRESSURE_PARA_PROTOCOL,
    AW0_PRESSURE_PARA_ROWS,
    AW0_PRODUCT_KEEP_CHARTER,
    AW0_REAL_EVAL_PROTOCOL,
    AW0_SAFE_NOTE,
    AW0_SHIP_LOCK,
    AW0_THESIS,
    AW0_TRUE_GEN_JUDGE,
    decide_aw0_session,
    map_aw_product_mode,
)


def test_given_modes_when_map_then_lookup_peak_decode_abstain() -> None:
    # GIVEN/WHEN/THEN: pesquisa §2 AW0 — four product modes
    assert map_aw_product_mode("WRAP_LOOKUP") == "LOOKUP"
    assert map_aw_product_mode("SEMWRAP_LOOKUP") == "LOOKUP"
    assert map_aw_product_mode("WRAP_DECODE") == "DECODE"
    assert map_aw_product_mode("NO_ANSWER") == "ABSTAIN"
    assert map_aw_product_mode("ABSTAIN") == "ABSTAIN"
    assert set(AW0_LATENCY_PATHS) == AW0_MODES
    assert "ABSTAIN" in AW0_MODES


def test_given_product_keep_when_read_then_cites_av_and_debts() -> None:
    # GIVEN AV locks · WHEN freeze product-keep · THEN cite + 6 debts + bars
    cited = set(AW0_PRODUCT_KEEP_CHARTER["cite_av_locks"])
    assert cited == AW0_CITED_AV_LOCKS
    assert "H-PRODSHIP" in cited
    assert "H-NANOGEN6" in cited
    assert "AV-FREEZE" in cited
    debts = AW0_PRODUCT_KEEP_CHARTER["debts"]
    ids = {d["id"] for d in debts}
    assert {
        "product_regression_hold",
        "pressure_human_para",
        "false_hit_zero",
        "mode_ui_always",
        "true_continue_unmet",
        "span_fallback_neq_gen",
    } <= ids
    bars = AW0_PRODUCT_KEEP_CHARTER["bars"]
    assert float(bars["para_hit_min"]) >= 0.70
    assert int(bars["false_hit_max"]) == 0
    assert int(bars["pressure_para_min_n"]) >= 20
    assert bars["decode_gibberish_neq_content_ok"] is True
    assert bars["default_ask_near_miss"] == "ABSTAIN"
    assert bars["eval_eq_prod_ask"] is True
    assert bars["regression_hold"] is True
    assert set(bars["modes_required"]) == AW0_MODES
    metrics = set(AW0_PRODUCT_KEEP_CHARTER["metrics"])
    assert {"para_hit", "false_hit", "decode_content_ok", "true_continue_ablated"} <= metrics


def test_given_pressure_para_when_read_then_held_out_neq_av_au() -> None:
    assert AW0_PRESSURE_PARA_PROTOCOL["held_out"] is True
    assert AW0_PRESSURE_PARA_PROTOCOL["bank_stuff_forbidden"] is True
    assert AW0_PRESSURE_PARA_PROTOCOL["neq_av_pack"] is True
    assert AW0_PRESSURE_PARA_PROTOCOL["neq_au_pack"] is True
    assert int(AW0_PRESSURE_PARA_PROTOCOL["min_n"]) >= 20
    assert len(AW0_PRESSURE_PARA_ROWS) >= 20
    ids = [p["id"] for p in AW0_PRESSURE_PARA_ROWS]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("AW-PARA-") for i in ids)
    assert all(str(p["question"]).strip() for p in AW0_PRESSURE_PARA_ROWS)
    au_q = {str(p["question"]).strip() for p in AU0_HUMAN_PARA_ROWS}
    av_q = {str(p["question"]).strip() for p in AV0_EXTERNAL_PARA_ROWS}
    aw_q = {str(p["question"]).strip() for p in AW0_PRESSURE_PARA_ROWS}
    assert au_q.isdisjoint(aw_q)
    assert av_q.isdisjoint(aw_q)


def test_given_nanogen7_when_read_then_tac_not_nanogen6_rename() -> None:
    hyp = AW0_NANOGEN7_HYPOTHESIS
    low = hyp.lower()
    assert "tac" in low or "teacher" in low
    assert "true_continue" in low or "ablated" in low
    assert "novel" in low
    assert "span" in low or "truncate" in low
    assert "nanogen6" in low
    assert "rename" in low or "refuse-or-continue" in low
    assert "top-k" in low or "topk" in low or "teacher" in low
    assert "bank-grounded short" not in low
    judge = AW0_TRUE_GEN_JUDGE
    assert judge["span_fallback_neq_gen"] is True
    assert judge["gold_substring_insufficient"] is True
    assert judge["gibberish_tail_fails"] is True
    assert judge["telemetry_neq_content_ok"] is True
    assert judge["teacher_topk_gate"] is True
    assert judge["novel_vs_span_required"] is True
    assert judge["nanogen6_refuse_or_continue_archived"] is True
    assert "true_continue" in str(judge["scoring"])


def test_given_real_eval_when_read_then_live_and_tac_gated() -> None:
    assert AW0_REAL_EVAL_PROTOCOL["live_ask_battery"] is True
    assert AW0_REAL_EVAL_PROTOCOL["summary_only_forbidden"] is True
    assert AW0_REAL_EVAL_PROTOCOL["wall_ms_n_new_mandatory"] is True
    assert AW0_REAL_EVAL_PROTOCOL["eval_eq_prod_ask"] is True
    assert AW0_REAL_EVAL_PROTOCOL["gold_substring_neq_gen"] is True
    assert AW0_REAL_EVAL_PROTOCOL["gibberish_tail_fails"] is True
    assert AW0_REAL_EVAL_PROTOCOL["span_fallback_neq_gen"] is True
    assert AW0_REAL_EVAL_PROTOCOL[
        "wall_ms_n_new_insufficient_for_decode_quality"
    ] is True
    claim = str(AW0_REAL_EVAL_PROTOCOL["gen_claim_rule"]).lower()
    assert "nanogen7" in claim
    assert "tac" in claim
    assert "span" in claim or "fallback" in claim


def test_given_battery_when_scan_then_covers_modes_and_debts() -> None:
    assert len(AW0_ASK_BATTERY) >= 4
    modes = {p["expect_mode"] for p in AW0_ASK_BATTERY}
    assert modes == AW0_MODES
    kinds = {p["kind"] for p in AW0_ASK_BATTERY}
    assert {
        "near_miss",
        "human_para",
        "labeled_peak",
        "junk_trap",
        "decode_content",
    } <= kinds
    ids = [p["id"] for p in AW0_ASK_BATTERY]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("AW-ASK-") for i in ids)


def test_given_notes_when_read_then_anti_fp_and_north_star() -> None:
    assert "≠" in AW0_SAFE_NOTE
    assert "LOOKUP" in AW0_ANTI_FP
    assert "eval path = prod" in AW0_ANTI_FP.lower()
    assert "truncate-to-span" in AW0_ANTI_FP.lower()
    assert "≤5M" in AW0_NORTH_STAR
    assert "NANOGEN7" in AW0_NORTH_STAR
    assert "TAC" in AW0_NORTH_STAR or "teacher" in AW0_NORTH_STAR.lower()
    assert "gibberish-tail" in AW0_SHIP_LOCK
    assert "PRODKEEP" in AW0_THESIS or "AW1" in AW0_THESIS
    assert "TAC" in AW0_THESIS or "teacher" in AW0_THESIS.lower()


def test_given_ready_when_decide_then_promote() -> None:
    out = decide_aw0_session(trials_dir_ready=True, anti_fp_signed=True)
    assert out.startswith("PROMOTE")
    assert AW0_ID in out


def test_given_no_trials_when_decide_then_kill() -> None:
    out = decide_aw0_session(trials_dir_ready=False, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "trials" in out


def test_given_unsigned_anti_fp_when_decide_then_kill() -> None:
    out = decide_aw0_session(trials_dir_ready=True, anti_fp_signed=False)
    assert out.startswith("KILL")
    assert "anti-FP" in out


def test_given_incomplete_battery_when_decide_then_kill() -> None:
    bad = [dict(p) for p in AW0_ASK_BATTERY if p["expect_mode"] != "PEAK"]
    out = decide_aw0_session(
        trials_dir_ready=True, anti_fp_signed=True, battery=bad
    )
    assert out.startswith("KILL")
    assert "battery" in out.lower() or "modes" in out.lower()
