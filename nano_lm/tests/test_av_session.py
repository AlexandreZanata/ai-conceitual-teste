"""Contract: Wave AV0 SESSION — freeze product-ship/external-para/NANOGEN6/eval."""

from __future__ import annotations

from au_session_ops import AU0_HUMAN_PARA_ROWS
from av_session_ops import (
    AV0_ANTI_FP,
    AV0_ASK_BATTERY,
    AV0_CITED_AU_LOCKS,
    AV0_EXTERNAL_PARA_PROTOCOL,
    AV0_EXTERNAL_PARA_ROWS,
    AV0_ID,
    AV0_LATENCY_PATHS,
    AV0_MODES,
    AV0_NANOGEN6_HYPOTHESIS,
    AV0_NORTH_STAR,
    AV0_PRODUCT_SHIP_CHARTER,
    AV0_REAL_EVAL_PROTOCOL,
    AV0_SAFE_NOTE,
    AV0_SHIP_LOCK,
    AV0_THESIS,
    AV0_TRUE_GEN_JUDGE,
    decide_av0_session,
    map_av_product_mode,
)


def test_given_modes_when_map_then_lookup_peak_decode_abstain() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AV0 — four product modes
    assert map_av_product_mode("WRAP_LOOKUP") == "LOOKUP"
    assert map_av_product_mode("SEMWRAP_LOOKUP") == "LOOKUP"
    assert map_av_product_mode("WRAP_DECODE") == "DECODE"
    assert map_av_product_mode("NO_ANSWER") == "ABSTAIN"
    assert map_av_product_mode("ABSTAIN") == "ABSTAIN"
    assert set(AV0_LATENCY_PATHS) == AV0_MODES
    assert "ABSTAIN" in AV0_MODES


def test_given_product_ship_when_read_then_cites_au_and_debts() -> None:
    # GIVEN AU locks · WHEN freeze product-ship · THEN cite + 6 debts + bars
    cited = set(AV0_PRODUCT_SHIP_CHARTER["cite_au_locks"])
    assert cited == AV0_CITED_AU_LOCKS
    assert "H-PRODHARD" in cited
    assert "H-NANOGEN5" in cited
    assert "AU-FREEZE" in cited
    debts = AV0_PRODUCT_SHIP_CHARTER["debts"]
    ids = {d["id"] for d in debts}
    assert {
        "decode_content_ok",
        "external_human_para",
        "false_hit_zero",
        "mode_ui_always",
        "kb_holes_honest",
        "latency_publish",
    } <= ids
    bars = AV0_PRODUCT_SHIP_CHARTER["bars"]
    assert float(bars["para_hit_min"]) >= 0.70
    assert int(bars["false_hit_max"]) == 0
    assert int(bars["external_para_min_n"]) >= 20
    assert bars["decode_gibberish_neq_content_ok"] is True
    assert bars["default_ask_near_miss"] == "ABSTAIN"
    assert bars["eval_eq_prod_ask"] is True
    assert set(bars["modes_required"]) == AV0_MODES
    metrics = set(AV0_PRODUCT_SHIP_CHARTER["metrics"])
    assert {"para_hit", "false_hit", "decode_content_ok", "p50_wall_ms"} <= metrics


def test_given_external_para_when_read_then_held_out_neq_au() -> None:
    assert AV0_EXTERNAL_PARA_PROTOCOL["held_out"] is True
    assert AV0_EXTERNAL_PARA_PROTOCOL["bank_stuff_forbidden"] is True
    assert AV0_EXTERNAL_PARA_PROTOCOL["neq_au_pack"] is True
    assert int(AV0_EXTERNAL_PARA_PROTOCOL["min_n"]) >= 20
    assert len(AV0_EXTERNAL_PARA_ROWS) >= 20
    ids = [p["id"] for p in AV0_EXTERNAL_PARA_ROWS]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("AV-PARA-") for i in ids)
    assert all(str(p["question"]).strip() for p in AV0_EXTERNAL_PARA_ROWS)
    au_q = {str(p["question"]).strip() for p in AU0_HUMAN_PARA_ROWS}
    av_q = {str(p["question"]).strip() for p in AV0_EXTERNAL_PARA_ROWS}
    assert au_q.isdisjoint(av_q)


def test_given_nanogen6_when_read_then_true_continue_not_truncate_clone() -> None:
    hyp = AV0_NANOGEN6_HYPOTHESIS
    low = hyp.lower()
    assert "true_continue" in low or "ablated" in low
    assert "span" in low or "truncate" in low
    assert "fallback" in low
    assert "nanogen5" in low or "5.5" in hyp
    assert "clone" in low
    assert "bank-grounded short" not in low
    judge = AV0_TRUE_GEN_JUDGE
    assert judge["span_fallback_neq_gen"] is True
    assert judge["gold_substring_insufficient"] is True
    assert judge["gibberish_tail_fails"] is True
    assert judge["telemetry_neq_content_ok"] is True
    assert judge["nanogen5_truncate_bar_archived"] is True
    assert "true_continue" in str(judge["scoring"])


def test_given_real_eval_when_read_then_live_and_span_forbidden() -> None:
    assert AV0_REAL_EVAL_PROTOCOL["live_ask_battery"] is True
    assert AV0_REAL_EVAL_PROTOCOL["summary_only_forbidden"] is True
    assert AV0_REAL_EVAL_PROTOCOL["wall_ms_n_new_mandatory"] is True
    assert AV0_REAL_EVAL_PROTOCOL["eval_eq_prod_ask"] is True
    assert AV0_REAL_EVAL_PROTOCOL["gold_substring_neq_gen"] is True
    assert AV0_REAL_EVAL_PROTOCOL["gibberish_tail_fails"] is True
    assert AV0_REAL_EVAL_PROTOCOL["span_fallback_neq_gen"] is True
    assert AV0_REAL_EVAL_PROTOCOL[
        "wall_ms_n_new_insufficient_for_decode_quality"
    ] is True
    claim = str(AV0_REAL_EVAL_PROTOCOL["gen_claim_rule"]).lower()
    assert "nanogen6" in claim
    assert "span" in claim or "fallback" in claim


def test_given_battery_when_scan_then_covers_modes_and_debts() -> None:
    assert len(AV0_ASK_BATTERY) >= 4
    modes = {p["expect_mode"] for p in AV0_ASK_BATTERY}
    assert modes == AV0_MODES
    kinds = {p["kind"] for p in AV0_ASK_BATTERY}
    assert {
        "near_miss",
        "human_para",
        "labeled_peak",
        "junk_trap",
        "decode_content",
    } <= kinds
    ids = [p["id"] for p in AV0_ASK_BATTERY]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("AV-ASK-") for i in ids)


def test_given_notes_when_read_then_anti_fp_and_north_star() -> None:
    assert "≠" in AV0_SAFE_NOTE
    assert "LOOKUP" in AV0_ANTI_FP
    assert "eval path = prod" in AV0_ANTI_FP.lower()
    assert "truncate-to-span" in AV0_ANTI_FP.lower()
    assert "≤5M" in AV0_NORTH_STAR
    assert "NANOGEN6" in AV0_NORTH_STAR
    assert "gibberish-tail" in AV0_SHIP_LOCK
    assert "PRODSHIP" in AV0_THESIS or "AV1" in AV0_THESIS


def test_given_ready_when_decide_then_promote() -> None:
    out = decide_av0_session(trials_dir_ready=True, anti_fp_signed=True)
    assert out.startswith("PROMOTE")
    assert AV0_ID in out


def test_given_no_trials_when_decide_then_kill() -> None:
    out = decide_av0_session(trials_dir_ready=False, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "trials" in out


def test_given_unsigned_anti_fp_when_decide_then_kill() -> None:
    out = decide_av0_session(trials_dir_ready=True, anti_fp_signed=False)
    assert out.startswith("KILL")
    assert "anti-FP" in out


def test_given_incomplete_battery_when_decide_then_kill() -> None:
    bad = [dict(p) for p in AV0_ASK_BATTERY if p["expect_mode"] != "PEAK"]
    out = decide_av0_session(
        trials_dir_ready=True, anti_fp_signed=True, battery=bad
    )
    assert out.startswith("KILL")
    assert "battery" in out.lower() or "modes" in out.lower()
