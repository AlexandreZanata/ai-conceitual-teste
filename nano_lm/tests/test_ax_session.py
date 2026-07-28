"""Contract: Wave AX0 SESSION — freeze hard-natural/PRODNAT/gen-defer/eval."""

from __future__ import annotations

from au_session_ops import AU0_HUMAN_PARA_ROWS
from av_session_ops import AV0_EXTERNAL_PARA_ROWS
from aw_session_ops import AW0_PRESSURE_PARA_ROWS
from ax_session_ops import (
    AX0_ANTI_FP,
    AX0_ASK_BATTERY,
    AX0_CITED_AW_LOCKS,
    AX0_GEN_STANCE,
    AX0_HARD_NATURAL_PROTOCOL,
    AX0_HARD_NATURAL_ROWS,
    AX0_ID,
    AX0_LATENCY_PATHS,
    AX0_MODES,
    AX0_NORTH_STAR,
    AX0_PRODUCT_NAT_CHARTER,
    AX0_REAL_EVAL_PROTOCOL,
    AX0_SAFE_NOTE,
    AX0_SHIP_LOCK,
    AX0_THESIS,
    AX0_TRUE_GEN_JUDGE,
    decide_ax0_session,
    map_ax_product_mode,
)


def test_given_modes_when_map_then_lookup_peak_decode_abstain() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AX0 — four product modes
    assert map_ax_product_mode("WRAP_LOOKUP") == "LOOKUP"
    assert map_ax_product_mode("SEMWRAP_LOOKUP") == "LOOKUP"
    assert map_ax_product_mode("WRAP_DECODE") == "DECODE"
    assert map_ax_product_mode("NO_ANSWER") == "ABSTAIN"
    assert map_ax_product_mode("ABSTAIN") == "ABSTAIN"
    assert set(AX0_LATENCY_PATHS) == AX0_MODES
    assert "ABSTAIN" in AX0_MODES


def test_given_product_nat_when_read_then_cites_aw_and_debts() -> None:
    # GIVEN AW locks · WHEN freeze product-nat · THEN cite + 7 debts + bars
    cited = set(AX0_PRODUCT_NAT_CHARTER["cite_aw_locks"])
    assert cited == AX0_CITED_AW_LOCKS
    assert "H-PRODKEEP" in cited
    assert "H-NANOGEN7" in cited
    assert "AW-FREEZE" in cited
    debts = AX0_PRODUCT_NAT_CHARTER["debts"]
    ids = {d["id"] for d in debts}
    assert {
        "hard_natural_para",
        "false_hit_zero",
        "latency_publish",
        "kb_holes_publish",
        "mode_ui_always",
        "decode_content_law",
        "gen_defer_stance",
    } <= ids
    bars = AX0_PRODUCT_NAT_CHARTER["bars"]
    assert float(bars["hard_natural_para_hit_min"]) >= 0.70
    assert int(bars["false_hit_max"]) == 0
    assert int(bars["hard_natural_min_n"]) >= 15
    assert bars["decode_gibberish_neq_content_ok"] is True
    assert bars["default_ask_near_miss"] == "ABSTAIN"
    assert bars["eval_eq_prod_ask"] is True
    assert bars["pressure_para_neq_hard_natural"] is True
    assert bars["regression_hold"] is True
    assert set(bars["modes_required"]) == AX0_MODES
    metrics = set(AX0_PRODUCT_NAT_CHARTER["metrics"])
    assert {
        "hard_natural_para_hit",
        "false_hit",
        "decode_content_ok",
        "true_continue_ablated",
    } <= metrics


def test_given_hard_natural_when_read_then_held_out_neq_aw_av_au() -> None:
    assert AX0_HARD_NATURAL_PROTOCOL["held_out"] is True
    assert AX0_HARD_NATURAL_PROTOCOL["bank_stuff_forbidden"] is True
    assert AX0_HARD_NATURAL_PROTOCOL["neq_aw_pack"] is True
    assert AX0_HARD_NATURAL_PROTOCOL["neq_av_pack"] is True
    assert AX0_HARD_NATURAL_PROTOCOL["neq_au_pack"] is True
    assert AX0_HARD_NATURAL_PROTOCOL["pressure_para_neq_hard_natural"] is True
    assert AX0_HARD_NATURAL_PROTOCOL["live_miss_id"] == "AX-NAT-01"
    assert int(AX0_HARD_NATURAL_PROTOCOL["min_n"]) >= 15
    assert len(AX0_HARD_NATURAL_ROWS) >= 15
    ids = [p["id"] for p in AX0_HARD_NATURAL_ROWS]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("AX-NAT-") for i in ids)
    assert all(str(p["question"]).strip() for p in AX0_HARD_NATURAL_ROWS)
    au_q = {str(p["question"]).strip() for p in AU0_HUMAN_PARA_ROWS}
    av_q = {str(p["question"]).strip() for p in AV0_EXTERNAL_PARA_ROWS}
    aw_q = {str(p["question"]).strip() for p in AW0_PRESSURE_PARA_ROWS}
    ax_q = {str(p["question"]).strip() for p in AX0_HARD_NATURAL_ROWS}
    assert au_q.isdisjoint(ax_q)
    assert av_q.isdisjoint(ax_q)
    assert aw_q.isdisjoint(ax_q)
    live = AX0_HARD_NATURAL_ROWS[0]["question"]
    assert "Python helper" in live
    assert "name it add" in live


def test_given_gen_stance_when_read_then_defer_not_nanogen8_rename() -> None:
    assert AX0_GEN_STANCE["stance"] == "defer"
    assert "defer" in AX0_GEN_STANCE["allowed_stances"]
    assert AX0_GEN_STANCE["capcheck"] == "closed"
    assert AX0_GEN_STANCE["nanogen8_rename_forbidden"] is True
    assert AX0_GEN_STANCE["nanogen6_hold_cited"] is True
    assert AX0_GEN_STANCE["nanogen7_hold_cited"] is True
    rat = str(AX0_GEN_STANCE["rationale"]).lower()
    assert "defer" in rat
    assert "nanogen" in rat
    judge = AX0_TRUE_GEN_JUDGE
    assert judge["span_fallback_neq_gen"] is True
    assert judge["nanogen8_rename_forbidden"] is True
    assert judge["nanogen7_tac_hold_archived"] is True
    assert "true_continue" in str(judge["scoring"])


def test_given_real_eval_when_read_then_live_and_nanogen8_gated() -> None:
    assert AX0_REAL_EVAL_PROTOCOL["live_ask_battery"] is True
    assert AX0_REAL_EVAL_PROTOCOL["summary_only_forbidden"] is True
    assert AX0_REAL_EVAL_PROTOCOL["wall_ms_n_new_mandatory"] is True
    assert AX0_REAL_EVAL_PROTOCOL["eval_eq_prod_ask"] is True
    assert AX0_REAL_EVAL_PROTOCOL["gold_substring_neq_gen"] is True
    assert AX0_REAL_EVAL_PROTOCOL["gibberish_tail_fails"] is True
    assert AX0_REAL_EVAL_PROTOCOL["span_fallback_neq_gen"] is True
    assert AX0_REAL_EVAL_PROTOCOL["pack_para_neq_hard_natural"] is True
    assert AX0_REAL_EVAL_PROTOCOL[
        "wall_ms_n_new_insufficient_for_decode_quality"
    ] is True
    claim = str(AX0_REAL_EVAL_PROTOCOL["gen_claim_rule"]).lower()
    assert "nanogen8" in claim
    assert "rename" in claim
    assert "span" in claim or "fallback" in claim


def test_given_battery_when_scan_then_covers_modes_and_debts() -> None:
    assert len(AX0_ASK_BATTERY) >= 4
    modes = {p["expect_mode"] for p in AX0_ASK_BATTERY}
    assert modes == AX0_MODES
    kinds = {p["kind"] for p in AX0_ASK_BATTERY}
    assert {
        "near_miss",
        "hard_natural",
        "labeled_peak",
        "junk_trap",
        "decode_content",
    } <= kinds
    ids = [p["id"] for p in AX0_ASK_BATTERY]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("AX-ASK-") for i in ids)


def test_given_notes_when_read_then_anti_fp_and_north_star() -> None:
    assert "≠" in AX0_SAFE_NOTE
    assert "hard natural" in AX0_SAFE_NOTE.lower()
    assert "LOOKUP" in AX0_ANTI_FP
    assert "eval path = prod" in AX0_ANTI_FP.lower()
    assert "hard natural" in AX0_ANTI_FP.lower()
    assert "NANOGEN8" in AX0_ANTI_FP or "nanogen8" in AX0_ANTI_FP.lower()
    assert "≤5M" in AX0_NORTH_STAR
    assert "defer" in AX0_NORTH_STAR.lower()
    assert "gibberish-tail" in AX0_SHIP_LOCK
    assert "TAC" in AX0_SHIP_LOCK
    assert "PRODNAT" in AX0_THESIS or "AX1" in AX0_THESIS
    assert "defer" in AX0_THESIS.lower()


def test_given_ready_when_decide_then_promote() -> None:
    out = decide_ax0_session(trials_dir_ready=True, anti_fp_signed=True)
    assert out.startswith("PROMOTE")
    assert AX0_ID in out


def test_given_no_trials_when_decide_then_kill() -> None:
    out = decide_ax0_session(trials_dir_ready=False, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "trials" in out


def test_given_unsigned_anti_fp_when_decide_then_kill() -> None:
    out = decide_ax0_session(trials_dir_ready=True, anti_fp_signed=False)
    assert out.startswith("KILL")
    assert "anti-FP" in out


def test_given_incomplete_battery_when_decide_then_kill() -> None:
    bad = [dict(p) for p in AX0_ASK_BATTERY if p["expect_mode"] != "PEAK"]
    out = decide_ax0_session(
        trials_dir_ready=True, anti_fp_signed=True, battery=bad
    )
    assert out.startswith("KILL")
    assert "battery" in out.lower() or "modes" in out.lower()
