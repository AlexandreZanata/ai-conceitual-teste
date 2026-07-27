"""Contract: Wave AR0 SESSION — freeze product deepen packs (pesquisa §5)."""

from __future__ import annotations

from aq_session_ops import ADV_KINDS, unique_ids
from ar_session_ops import (
    AR0_ABSTAIN_PROTOCOL,
    AR0_ADVREG_N,
    AR0_ADVREG_PACK,
    AR0_EXT_N,
    AR0_EXT_PARA_PACK,
    AR0_ID,
    AR0_LATENCY_PATHS,
    AR0_MODES,
    AR0_NANOGEN2_HYPOTHESIS,
    AR0_NORTH_STAR,
    AR0_SAFE_NOTE,
    AR0_SHIPDEMO_CHARTER,
    AR0_THESIS,
    advreg_kind_counts,
    advreg_overlaps_aq_adv,
    decide_ar0_session,
    ext_collides_parent_norm,
    ext_overlaps_ap_hitl,
    ext_overlaps_aq_para,
    map_ar_product_mode,
)


def test_given_packs_when_count_then_twenty_each() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AR0 — external-para-20 · advreg-20
    assert len(AR0_EXT_PARA_PACK) == AR0_EXT_N == 20
    assert len(AR0_ADVREG_PACK) == AR0_ADVREG_N == 20


def test_given_packs_when_ids_then_unique_with_prefix() -> None:
    assert unique_ids(AR0_EXT_PARA_PACK, n=AR0_EXT_N, prefix="AR-EXT-") is True
    assert (
        unique_ids(AR0_ADVREG_PACK, n=AR0_ADVREG_N, prefix="AR-ADVREG-")
        is True
    )


def test_given_advreg_when_kinds_then_all_three_present() -> None:
    counts = advreg_kind_counts(AR0_ADVREG_PACK)
    assert set(counts) == ADV_KINDS
    assert all(counts[k] >= 1 for k in ADV_KINDS)


def test_given_ext_when_compare_aq_then_no_exact_overlap() -> None:
    assert ext_overlaps_aq_para(AR0_EXT_PARA_PACK) == []


def test_given_copied_aq_para_when_overlap_then_listed() -> None:
    from aq_session_ops import AQ0_PARA_PACK

    bad = [dict(p) for p in AR0_EXT_PARA_PACK]
    bad[0]["paraphrase"] = AQ0_PARA_PACK[0]["paraphrase"]
    assert ext_overlaps_aq_para(bad) == ["AR-EXT-01"]


def test_given_ext_when_compare_ap_then_no_verbatim_overlap() -> None:
    assert ext_overlaps_ap_hitl(AR0_EXT_PARA_PACK) == []


def test_given_ext_when_normalize_then_not_equal_parent() -> None:
    assert ext_collides_parent_norm(AR0_EXT_PARA_PACK) == []


def test_given_advreg_when_compare_aq_then_no_exact_ask() -> None:
    assert advreg_overlaps_aq_adv(AR0_ADVREG_PACK) == []


def test_given_modes_when_map_then_lookup_peak_decode_abstain() -> None:
    assert map_ar_product_mode("WRAP_LOOKUP") == "LOOKUP"
    assert map_ar_product_mode("SEMWRAP_LOOKUP") == "LOOKUP"
    assert map_ar_product_mode("WRAP_DECODE") == "DECODE"
    assert (
        map_ar_product_mode("QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+PEAK") == "PEAK"
    )
    assert map_ar_product_mode("NO_ANSWER") == "ABSTAIN"
    assert map_ar_product_mode("REFUSE") == "ABSTAIN"
    assert map_ar_product_mode("ABSTAIN") == "ABSTAIN"
    assert set(AR0_LATENCY_PATHS) == AR0_MODES
    assert "ABSTAIN" in AR0_MODES


def test_given_charters_when_read_then_abstain_and_nanogen2() -> None:
    assert AR0_ABSTAIN_PROTOCOL["action"] == "NO_ANSWER"
    assert AR0_ABSTAIN_PROTOCOL["product_mode"] == "ABSTAIN"
    assert "ABSTAIN" in AR0_SHIPDEMO_CHARTER["required_ui_modes"]
    assert "ablated" in AR0_NANOGEN2_HYPOTHESIS.lower()
    assert "5.0" in AR0_NANOGEN2_HYPOTHESIS
    assert "≠" in AR0_SAFE_NOTE
    assert "≤5M" in AR0_NORTH_STAR


def test_given_ready_when_decide_then_promote() -> None:
    out = decide_ar0_session(trials_dir_ready=True, north_star_signed=True)
    assert out.startswith("PROMOTE")
    assert AR0_ID in out
    assert "ABSTAIN" in AR0_THESIS or "AR1" in AR0_THESIS


def test_given_no_trials_when_decide_then_kill() -> None:
    out = decide_ar0_session(trials_dir_ready=False, north_star_signed=True)
    assert out.startswith("KILL")
    assert "trials" in out


def test_given_unsigned_north_star_when_decide_then_kill() -> None:
    out = decide_ar0_session(trials_dir_ready=True, north_star_signed=False)
    assert out.startswith("KILL")
    assert "north-star" in out


def test_given_ext_when_fields_then_gold_and_source() -> None:
    for item in AR0_EXT_PARA_PACK:
        assert item["source_id"]
        assert item["parent_question"].strip()
        assert item["paraphrase"].strip()
        assert item["gold"].strip()
        assert item["id"].startswith("AR-EXT-")
