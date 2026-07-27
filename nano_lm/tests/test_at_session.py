"""Contract: Wave AT0 SESSION — freeze PRODREG/SHIPAPP/NANOGEN4/real-eval."""

from __future__ import annotations

from at_session_ops import (
    AT0_ANTI_FP,
    AT0_ASK_BATTERY,
    AT0_CITED_AS_GATES,
    AT0_ID,
    AT0_LATENCY_PATHS,
    AT0_MODES,
    AT0_NANOGEN4_HYPOTHESIS,
    AT0_NORTH_STAR,
    AT0_PRODREG_SUITE,
    AT0_REAL_EVAL_PROTOCOL,
    AT0_SAFE_NOTE,
    AT0_SHIPAPP_CHARTER,
    AT0_THESIS,
    decide_at0_session,
    map_at_product_mode,
)


def test_given_modes_when_map_then_lookup_peak_decode_abstain() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AT0 — four product modes
    assert map_at_product_mode("WRAP_LOOKUP") == "LOOKUP"
    assert map_at_product_mode("SEMWRAP_LOOKUP") == "LOOKUP"
    assert map_at_product_mode("WRAP_DECODE") == "DECODE"
    assert map_at_product_mode("NO_ANSWER") == "ABSTAIN"
    assert map_at_product_mode("ABSTAIN") == "ABSTAIN"
    assert set(AT0_LATENCY_PATHS) == AT0_MODES
    assert "ABSTAIN" in AT0_MODES


def test_given_prodreg_when_read_then_cites_as_gates_and_bars() -> None:
    # GIVEN AS locked product trust · WHEN freeze PRODREG · THEN cite + bars
    cited = set(AT0_PRODREG_SUITE["cite_as_gates"])
    assert cited == AT0_CITED_AS_GATES
    assert "H-ADVSAFE" in cited
    assert "H-PARAEXT2" in cited
    assert "H-NANOGEN3" in cited
    bars = AT0_PRODREG_SUITE["bars"]
    assert float(bars["para_hit_min"]) >= 0.70
    assert int(bars["false_hit_max"]) == 0
    assert bars["default_ask_ood"] == "ABSTAIN"
    assert set(bars["modes_required"]) == AT0_MODES
    metrics = set(AT0_PRODREG_SUITE["metrics"])
    assert {"para_hit", "false_hit", "p50_wall_ms", "p99_wall_ms"} <= metrics


def test_given_shipapp_when_read_then_four_modes_on_ship_demo() -> None:
    paths = AT0_SHIPAPP_CHARTER["paths"]
    assert "ship/demo" in paths
    assert "nano:z:ask" in paths
    assert set(AT0_SHIPAPP_CHARTER["required_modes"]) == AT0_MODES
    assert AT0_SHIPAPP_CHARTER["smoke"] == "4/4"
    banner = AT0_SHIPAPP_CHARTER["banner"]
    for token in ("LOOKUP", "PEAK", "DECODE", "ABSTAIN"):
        assert token in banner


def test_given_nanogen4_when_read_then_new_idea_vs_nanogen3() -> None:
    hyp = AT0_NANOGEN4_HYPOTHESIS
    low = hyp.lower()
    assert "ablated" in low
    assert "5.0" in hyp
    assert "4.3" in hyp
    assert "prefix" in low or "snippet" in low
    assert "bank-gold" in low or "bank gold" in low
    assert "bank-grounded short" not in low


def test_given_real_eval_when_read_then_live_battery_not_summary() -> None:
    assert AT0_REAL_EVAL_PROTOCOL["live_ask_battery"] is True
    assert AT0_REAL_EVAL_PROTOCOL["summary_only_forbidden"] is True
    assert AT0_REAL_EVAL_PROTOCOL["wall_ms_n_new_mandatory"] is True
    claim = str(AT0_REAL_EVAL_PROTOCOL["gen_claim_rule"]).lower()
    assert "nanogen4" in claim
    assert "5.0" in claim


def test_given_battery_when_scan_then_covers_four_modes() -> None:
    assert len(AT0_ASK_BATTERY) >= 4
    modes = {p["expect_mode"] for p in AT0_ASK_BATTERY}
    assert modes == AT0_MODES
    ids = [p["id"] for p in AT0_ASK_BATTERY]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("AT-ASK-") for i in ids)


def test_given_notes_when_read_then_anti_fp_and_north_star() -> None:
    assert "≠" in AT0_SAFE_NOTE
    assert "LOOKUP" in AT0_ANTI_FP
    assert "≤5M" in AT0_NORTH_STAR
    assert "NANOGEN4" in AT0_NORTH_STAR
    assert "PRODREG" in AT0_THESIS or "AT1" in AT0_THESIS


def test_given_ready_when_decide_then_promote() -> None:
    out = decide_at0_session(trials_dir_ready=True, anti_fp_signed=True)
    assert out.startswith("PROMOTE")
    assert AT0_ID in out


def test_given_no_trials_when_decide_then_kill() -> None:
    out = decide_at0_session(trials_dir_ready=False, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "trials" in out


def test_given_unsigned_anti_fp_when_decide_then_kill() -> None:
    out = decide_at0_session(trials_dir_ready=True, anti_fp_signed=False)
    assert out.startswith("KILL")
    assert "anti-FP" in out


def test_given_incomplete_battery_when_decide_then_kill() -> None:
    bad = [dict(p) for p in AT0_ASK_BATTERY if p["expect_mode"] != "PEAK"]
    out = decide_at0_session(
        trials_dir_ready=True, anti_fp_signed=True, battery=bad
    )
    assert out.startswith("KILL")
    assert "battery" in out.lower() or "modes" in out.lower()
