"""Contract: Wave AI1b H-CAPRENEG — named size+budget after GENPLUS HOLD."""

from __future__ import annotations

from capreneg_ops import (
    BUDGET_VRAM_GB,
    BUDGET_WALL_S,
    CAPRENEG_ID,
    CAPRENEG_N,
    CAPRENEG_PACK,
    GENPLUS_GEN_MEAN,
    HARD_CAP_PARAMS,
    MIN_GEN_MEAN,
    MIN_LOOKUP_MEAN,
    PROBE_HF_ID,
    PROPOSAL_ID,
    PROPOSED_MAX_PARAMS,
    budget_ok,
    capreneg_stats,
    decide_capreneg,
    proposal_ok,
    score_capreneg_gen,
    score_capreneg_lookup,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AI1b H-CAPRENEG
    assert CAPRENEG_ID == "H-CAPRENEG"
    assert CAPRENEG_N == 10
    assert HARD_CAP_PARAMS == 5_000_000
    assert PROPOSAL_ID == "CAP-125M"
    assert PROPOSED_MAX_PARAMS == 130_000_000
    assert PROBE_HF_ID == "EleutherAI/gpt-neo-125M"
    assert BUDGET_WALL_S == 600
    assert BUDGET_VRAM_GB == 8
    assert MIN_LOOKUP_MEAN == 7.0
    assert MIN_GEN_MEAN == 5.0
    assert GENPLUS_GEN_MEAN == 4.0
    assert len(CAPRENEG_PACK) == 10


def test_given_pack_when_ids_then_ai_hitl() -> None:
    for item in CAPRENEG_PACK:
        assert item["id"].startswith("AI-HITL-")
        assert item["gold"].strip()


def test_given_proposal_when_probe_fits_then_ok() -> None:
    assert proposal_ok(proposed_max=130_000_000, probe_params=125_198_592)
    assert proposal_ok(proposed_max=130_000_000, probe_params=33_000_000)


def test_given_proposal_when_not_above_hard_then_fail() -> None:
    assert proposal_ok(proposed_max=5_000_000, probe_params=3_000_000) is False
    assert proposal_ok(proposed_max=130_000_000, probe_params=200_000_000) is False


def test_given_budget_when_within_then_ok() -> None:
    assert budget_ok(
        elapsed_s=100.0, vram_gb_peak=4.0, weight_update=False
    )


def test_given_budget_when_train_or_over_then_fail() -> None:
    assert (
        budget_ok(elapsed_s=100.0, vram_gb_peak=4.0, weight_update=True)
        is False
    )
    assert (
        budget_ok(elapsed_s=999.0, vram_gb_peak=4.0, weight_update=False)
        is False
    )


def test_given_lookup_true_hit_when_score_then_ok() -> None:
    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    score, err, notes = score_capreneg_lookup(
        mode="WRAP_LOOKUP",
        completion="gold",
        expected_gold="gold",
        lookup_kind="TRUE_HIT",
        payload=payload,
    )
    assert score >= 8.0 and err is False
    assert any("CAPRENEG" in n for n in notes)


def test_given_gen_contains_gold_when_score_then_seven() -> None:
    payload = {
        "mode": "PROBE-125M+GROUNDED",
        "wall_ms": 40.0,
        "n_new": 16,
    }
    score, err, notes = score_capreneg_gen(
        completion="The binary structure is 78 bytes.",
        expected_gold="78",
        payload=payload,
    )
    assert score == 7.0 and err is False
    assert any("CAP-125M" in n or "probe=" in n for n in notes)


def test_given_ready_gen_when_decide_then_promote() -> None:
    stats = capreneg_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[5.5] * 10,
        gen_errors=[False] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_period=0,
        n_fix=0,
        champion_params=3_348_928,
        probe_params=125_198_592,
        elapsed_s=120.0,
        vram_gb_peak=3.5,
        weight_update=False,
    )
    assert stats["pass_gen"] is True
    assert stats["proposal_ok"] is True
    assert decide_capreneg(stats) == "PROMOTE"


def test_given_low_gen_when_decide_then_hold() -> None:
    stats = capreneg_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[4.0] * 10,
        gen_errors=[True] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_period=0,
        n_fix=0,
        champion_params=3_348_928,
        probe_params=125_198_592,
        elapsed_s=120.0,
        vram_gb_peak=3.5,
        weight_update=False,
    )
    assert decide_capreneg(stats) == "HOLD"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = capreneg_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[5.5] * 10,
        gen_errors=[False] * 10,
        n_true_hit=9,
        n_false_hit=1,
        n_period=0,
        n_fix=0,
        champion_params=3_348_928,
        probe_params=125_198_592,
        elapsed_s=120.0,
        vram_gb_peak=3.5,
        weight_update=False,
    )
    assert decide_capreneg(stats) == "KILL"
