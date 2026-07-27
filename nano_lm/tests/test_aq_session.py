"""Contract: Wave AQ0 SESSION — freeze product-science packs (pesquisa §5)."""

from __future__ import annotations

from aq_session_ops import (
    ADV_KINDS,
    AQ0_ADV_N,
    AQ0_ADV_PACK,
    AQ0_ID,
    AQ0_LATENCY_PATHS,
    AQ0_MODES,
    AQ0_PARA_N,
    AQ0_PARA_PACK,
    AQ0_PRODUCT_HOLES,
    AQ0_THESIS,
    adv_kind_counts,
    decide_aq0_session,
    kb_coverage_snapshot,
    map_product_mode,
    para_collides_parent_norm,
    para_overlaps_ap_hitl,
    unique_ids,
)


def _kb_ok() -> dict:
    return kb_coverage_snapshot(
        curated_ids={"bip-0039", "rfc791"},
        bank_source_ids={"bip-0039"},
    )


def test_given_packs_when_count_then_twenty_each() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AQ0 — paraphrase-20 · adversary-20
    assert len(AQ0_PARA_PACK) == AQ0_PARA_N == 20
    assert len(AQ0_ADV_PACK) == AQ0_ADV_N == 20


def test_given_packs_when_ids_then_unique_with_prefix() -> None:
    assert unique_ids(AQ0_PARA_PACK, n=AQ0_PARA_N, prefix="AQ-PARA-") is True
    assert unique_ids(AQ0_ADV_PACK, n=AQ0_ADV_N, prefix="AQ-ADV-") is True


def test_given_adv_when_kinds_then_all_three_present() -> None:
    counts = adv_kind_counts(AQ0_ADV_PACK)
    assert set(counts) == ADV_KINDS
    assert all(counts[k] >= 1 for k in ADV_KINDS)


def test_given_para_when_compare_ap_then_no_verbatim_overlap() -> None:
    assert para_overlaps_ap_hitl(AQ0_PARA_PACK) == []


def test_given_copied_ap_q_when_overlap_then_listed() -> None:
    from ap_session_ops import AP0_PACK

    bad = [dict(p) for p in AQ0_PARA_PACK]
    bad[0]["paraphrase"] = AP0_PACK[0]["question"]
    assert para_overlaps_ap_hitl(bad) == ["AQ-PARA-01"]


def test_given_para_when_normalize_then_not_equal_parent() -> None:
    assert para_collides_parent_norm(AQ0_PARA_PACK) == []


def test_given_modes_when_map_then_lookup_peak_decode() -> None:
    assert map_product_mode("WRAP_LOOKUP") == "LOOKUP"
    assert map_product_mode("SEMWRAP_LOOKUP") == "LOOKUP"
    assert map_product_mode("WRAP_DECODE") == "DECODE"
    assert (
        map_product_mode("QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+PEAK") == "PEAK"
    )
    assert (
        map_product_mode("QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+ABLATED")
        == "DECODE"
    )
    assert set(AQ0_LATENCY_PATHS) == AQ0_MODES


def test_given_kb_when_holes_then_not_fake_complete() -> None:
    snap = _kb_ok()
    assert snap["coverage_pct"] == 50.0
    assert "rfc791" in snap["missing_curated_in_bank"]
    assert snap["complete_claim_forbidden"] is True
    assert len(snap["holes"]) >= 1
    assert len(AQ0_PRODUCT_HOLES) >= 1


def test_given_ready_when_decide_then_promote() -> None:
    out = decide_aq0_session(trials_dir_ready=True, kb=_kb_ok())
    assert out.startswith("PROMOTE")
    assert AQ0_ID in out
    assert "PARAHIT" in AQ0_THESIS or "AQ1" in AQ0_THESIS


def test_given_no_trials_when_decide_then_kill() -> None:
    out = decide_aq0_session(trials_dir_ready=False, kb=_kb_ok())
    assert out.startswith("KILL")
    assert "trials" in out


def test_given_empty_holes_when_decide_then_kill() -> None:
    kb = dict(_kb_ok())
    kb["holes"] = []
    out = decide_aq0_session(trials_dir_ready=True, kb=kb)
    assert out.startswith("KILL")
    assert "holes" in out


def test_given_para_when_fields_then_gold_and_source() -> None:
    for item in AQ0_PARA_PACK:
        assert item["source_id"]
        assert item["parent_question"].strip()
        assert item["paraphrase"].strip()
        assert item["gold"].strip()
        assert item["id"].startswith("AQ-PARA-")
