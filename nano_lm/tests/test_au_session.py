"""Contract: Wave AU0 SESSION — freeze product-debt/human-para/NANOGEN5/eval."""

from __future__ import annotations

from au_session_ops import (
    AU0_ANTI_FP,
    AU0_ASK_BATTERY,
    AU0_CITED_AT_LOCKS,
    AU0_HUMAN_PARA_PROTOCOL,
    AU0_HUMAN_PARA_ROWS,
    AU0_ID,
    AU0_LATENCY_PATHS,
    AU0_MODES,
    AU0_NANOGEN5_HYPOTHESIS,
    AU0_NORTH_STAR,
    AU0_PRODUCT_DEBT_SUITE,
    AU0_REAL_EVAL_PROTOCOL,
    AU0_SAFE_NOTE,
    AU0_SHIP_LOCK,
    AU0_STRICT_GEN_JUDGE,
    AU0_THESIS,
    decide_au0_session,
    map_au_product_mode,
)


def test_given_modes_when_map_then_lookup_peak_decode_abstain() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AU0 — four product modes
    assert map_au_product_mode("WRAP_LOOKUP") == "LOOKUP"
    assert map_au_product_mode("SEMWRAP_LOOKUP") == "LOOKUP"
    assert map_au_product_mode("WRAP_DECODE") == "DECODE"
    assert map_au_product_mode("NO_ANSWER") == "ABSTAIN"
    assert map_au_product_mode("ABSTAIN") == "ABSTAIN"
    assert set(AU0_LATENCY_PATHS) == AU0_MODES
    assert "ABSTAIN" in AU0_MODES


def test_given_product_debt_when_read_then_cites_at_and_live_audit() -> None:
    # GIVEN AT locks · WHEN freeze product-debt · THEN cite + 4 debts + bars
    cited = set(AU0_PRODUCT_DEBT_SUITE["cite_at_locks"])
    assert cited == AU0_CITED_AT_LOCKS
    assert "H-PRODREG" in cited
    assert "H-NANOGEN4" in cited
    assert "AT-FREEZE" in cited
    debts = AU0_PRODUCT_DEBT_SUITE["debts"]
    ids = {d["id"] for d in debts}
    assert {
        "near_miss_default_ask",
        "human_para_heldout",
        "peak_usable_span",
        "answer_usability",
    } <= ids
    bars = AU0_PRODUCT_DEBT_SUITE["bars"]
    assert float(bars["para_hit_min"]) >= 0.70
    assert int(bars["false_hit_max"]) == 0
    assert bars["default_ask_near_miss"] == "ABSTAIN"
    assert bars["eval_eq_prod_ask"] is True
    assert bars["peak_usable_or_abstain"] is True
    assert set(bars["modes_required"]) == AU0_MODES
    metrics = set(AU0_PRODUCT_DEBT_SUITE["metrics"])
    assert {"para_hit", "false_hit", "peak_usable", "p50_wall_ms"} <= metrics


def test_given_human_para_when_read_then_held_out_no_bank_stuff() -> None:
    assert AU0_HUMAN_PARA_PROTOCOL["held_out"] is True
    assert AU0_HUMAN_PARA_PROTOCOL["bank_stuff_forbidden"] is True
    assert int(AU0_HUMAN_PARA_PROTOCOL["min_n"]) >= 8
    assert len(AU0_HUMAN_PARA_ROWS) >= 8
    ids = [p["id"] for p in AU0_HUMAN_PARA_ROWS]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("AU-PARA-") for i in ids)
    assert all(str(p["question"]).strip() for p in AU0_HUMAN_PARA_ROWS)


def test_given_nanogen5_when_read_then_strict_vs_nanogen4() -> None:
    hyp = AU0_NANOGEN5_HYPOTHESIS
    low = hyp.lower()
    assert "ablated" in low
    assert "5.5" in hyp
    assert "strict" in low
    assert "gold-substring" in low or "gold substring" in low
    assert "gibberish" in low
    assert "f1" in low or "hitl" in low
    assert "bank-grounded short" not in low
    judge = AU0_STRICT_GEN_JUDGE
    assert judge["gold_substring_insufficient"] is True
    assert judge["gibberish_tail_fails"] is True
    assert judge["scoring"] == "short_answer_f1_or_hitl"


def test_given_real_eval_when_read_then_live_and_eval_eq_prod() -> None:
    assert AU0_REAL_EVAL_PROTOCOL["live_ask_battery"] is True
    assert AU0_REAL_EVAL_PROTOCOL["summary_only_forbidden"] is True
    assert AU0_REAL_EVAL_PROTOCOL["wall_ms_n_new_mandatory"] is True
    assert AU0_REAL_EVAL_PROTOCOL["eval_eq_prod_ask"] is True
    assert AU0_REAL_EVAL_PROTOCOL["gold_substring_neq_gen"] is True
    assert AU0_REAL_EVAL_PROTOCOL["gibberish_tail_fails"] is True
    claim = str(AU0_REAL_EVAL_PROTOCOL["gen_claim_rule"]).lower()
    assert "nanogen5" in claim
    assert "5.5" in claim


def test_given_battery_when_scan_then_covers_modes_and_debts() -> None:
    assert len(AU0_ASK_BATTERY) >= 4
    modes = {p["expect_mode"] for p in AU0_ASK_BATTERY}
    assert modes == AU0_MODES
    kinds = {p["kind"] for p in AU0_ASK_BATTERY}
    assert {"near_miss", "human_para", "labeled_peak", "junk_trap"} <= kinds
    ids = [p["id"] for p in AU0_ASK_BATTERY]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("AU-ASK-") for i in ids)


def test_given_notes_when_read_then_anti_fp_and_north_star() -> None:
    assert "≠" in AU0_SAFE_NOTE
    assert "LOOKUP" in AU0_ANTI_FP
    assert "eval path = prod" in AU0_ANTI_FP.lower()
    assert "≤5M" in AU0_NORTH_STAR
    assert "NANOGEN5" in AU0_NORTH_STAR
    assert "snippet-prefix" in AU0_SHIP_LOCK
    assert "PRODHARD" in AU0_THESIS or "AU1" in AU0_THESIS


def test_given_ready_when_decide_then_promote() -> None:
    out = decide_au0_session(trials_dir_ready=True, anti_fp_signed=True)
    assert out.startswith("PROMOTE")
    assert AU0_ID in out


def test_given_no_trials_when_decide_then_kill() -> None:
    out = decide_au0_session(trials_dir_ready=False, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "trials" in out


def test_given_unsigned_anti_fp_when_decide_then_kill() -> None:
    out = decide_au0_session(trials_dir_ready=True, anti_fp_signed=False)
    assert out.startswith("KILL")
    assert "anti-FP" in out


def test_given_incomplete_battery_when_decide_then_kill() -> None:
    bad = [dict(p) for p in AU0_ASK_BATTERY if p["expect_mode"] != "PEAK"]
    out = decide_au0_session(
        trials_dir_ready=True, anti_fp_signed=True, battery=bad
    )
    assert out.startswith("KILL")
    assert "battery" in out.lower() or "modes" in out.lower()
