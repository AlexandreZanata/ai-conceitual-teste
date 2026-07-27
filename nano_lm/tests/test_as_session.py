"""Contract: Wave AS0 SESSION — freeze product-trust packs (pesquisa §5)."""

from __future__ import annotations

from aq_session_ops import ADV_KINDS, unique_ids
from ar_session_ops import AR0_ADVREG_PACK
from as_session_ops import (
    AS0_ADVSAFE_N,
    AS0_ADVSAFE_PACK,
    AS0_ANTI_FP,
    AS0_ASKABSTAIN_CHARTER,
    AS0_ID,
    AS0_LATENCY_PATHS,
    AS0_METRICS_PROTOCOL,
    AS0_MODES,
    AS0_NANOGEN3_HYPOTHESIS,
    AS0_NORTH_STAR,
    AS0_PARA_N,
    AS0_PARAEXT2_PACK,
    AS0_REQUIRED_ADV_PARENTS,
    AS0_SAFE_NOTE,
    AS0_SEMFIX_HYPOTHESIS,
    AS0_THESIS,
    advsafe_kind_counts,
    advsafe_missing_required_parents,
    decide_as0_session,
    map_as_product_mode,
    paraext2_collides_parent_norm,
    paraext2_overlaps_ap_hitl,
    paraext2_overlaps_aq_para,
    paraext2_overlaps_ar_ext,
)


def test_given_packs_when_count_then_twenty_each() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AS0 — PARAEXT2-20 · ADVSAFE-20
    assert len(AS0_PARAEXT2_PACK) == AS0_PARA_N == 20
    assert len(AS0_ADVSAFE_PACK) == AS0_ADVSAFE_N == 20


def test_given_packs_when_ids_then_unique_with_prefix() -> None:
    assert unique_ids(AS0_PARAEXT2_PACK, n=AS0_PARA_N, prefix="AS-EXT2-")
    assert unique_ids(
        AS0_ADVSAFE_PACK, n=AS0_ADVSAFE_N, prefix="AS-ADVSAFE-"
    )


def test_given_advsafe_when_kinds_then_all_three_present() -> None:
    counts = advsafe_kind_counts(AS0_ADVSAFE_PACK)
    assert set(counts) == ADV_KINDS
    assert all(counts[k] >= 1 for k in ADV_KINDS)


def test_given_advsafe_when_parents_then_cites_ar_advreg_01_05() -> None:
    # GIVEN ADVREG KILL ids · WHEN freeze ADVSAFE · THEN cite 01/05
    assert advsafe_missing_required_parents(AS0_ADVSAFE_PACK) == []
    assert AS0_REQUIRED_ADV_PARENTS <= {
        str(p.get("parent_id", "")) for p in AS0_ADVSAFE_PACK
    }
    ar_asks = {r["id"]: r["ask"] for r in AR0_ADVREG_PACK}
    by_parent = {
        str(p["parent_id"]): p
        for p in AS0_ADVSAFE_PACK
        if p.get("parent_id") in AS0_REQUIRED_ADV_PARENTS
    }
    assert by_parent["AR-ADVREG-01"]["ask"] == ar_asks["AR-ADVREG-01"]
    assert by_parent["AR-ADVREG-05"]["ask"] == ar_asks["AR-ADVREG-05"]


def test_given_paraext2_when_compare_aq_then_no_exact_overlap() -> None:
    assert paraext2_overlaps_aq_para(AS0_PARAEXT2_PACK) == []


def test_given_paraext2_when_compare_ar_then_no_exact_overlap() -> None:
    assert paraext2_overlaps_ar_ext(AS0_PARAEXT2_PACK) == []


def test_given_copied_ar_ext_when_overlap_then_listed() -> None:
    from ar_session_ops import AR0_EXT_PARA_PACK

    bad = [dict(p) for p in AS0_PARAEXT2_PACK]
    bad[0]["paraphrase"] = AR0_EXT_PARA_PACK[0]["paraphrase"]
    assert paraext2_overlaps_ar_ext(bad) == ["AS-EXT2-01"]


def test_given_paraext2_when_compare_ap_then_no_verbatim_overlap() -> None:
    assert paraext2_overlaps_ap_hitl(AS0_PARAEXT2_PACK) == []


def test_given_paraext2_when_normalize_then_not_equal_parent() -> None:
    assert paraext2_collides_parent_norm(AS0_PARAEXT2_PACK) == []


def test_given_modes_when_map_then_lookup_peak_decode_abstain() -> None:
    assert map_as_product_mode("WRAP_LOOKUP") == "LOOKUP"
    assert map_as_product_mode("SEMWRAP_LOOKUP") == "LOOKUP"
    assert map_as_product_mode("WRAP_DECODE") == "DECODE"
    assert map_as_product_mode("NO_ANSWER") == "ABSTAIN"
    assert map_as_product_mode("ABSTAIN") == "ABSTAIN"
    assert set(AS0_LATENCY_PATHS) == AS0_MODES
    assert "ABSTAIN" in AS0_MODES


def test_given_charters_when_read_then_askabstain_semfix_nanogen3() -> None:
    assert AS0_ASKABSTAIN_CHARTER["action"] == "NO_ANSWER"
    assert AS0_ASKABSTAIN_CHARTER["product_mode"] == "ABSTAIN"
    assert "nano:z:ask" in AS0_ASKABSTAIN_CHARTER["paths"]
    assert "negation" in AS0_SEMFIX_HYPOTHESIS.lower()
    assert "margin" in AS0_SEMFIX_HYPOTHESIS.lower()
    assert "ablated" in AS0_NANOGEN3_HYPOTHESIS.lower()
    assert "5.0" in AS0_NANOGEN3_HYPOTHESIS
    assert "4.3" in AS0_NANOGEN3_HYPOTHESIS
    assert "p50_wall_ms" in AS0_METRICS_PROTOCOL["metrics"]
    assert "≠" in AS0_SAFE_NOTE
    assert "LOOKUP" in AS0_ANTI_FP
    assert "≤5M" in AS0_NORTH_STAR


def test_given_ready_when_decide_then_promote() -> None:
    out = decide_as0_session(trials_dir_ready=True, anti_fp_signed=True)
    assert out.startswith("PROMOTE")
    assert AS0_ID in out
    assert "ASKABSTAIN" in AS0_THESIS or "AS1" in AS0_THESIS


def test_given_no_trials_when_decide_then_kill() -> None:
    out = decide_as0_session(trials_dir_ready=False, anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "trials" in out


def test_given_unsigned_anti_fp_when_decide_then_kill() -> None:
    out = decide_as0_session(trials_dir_ready=True, anti_fp_signed=False)
    assert out.startswith("KILL")
    assert "anti-FP" in out


def test_given_missing_parent_when_decide_then_kill() -> None:
    bad = [dict(p) for p in AS0_ADVSAFE_PACK]
    for row in bad:
        if row.get("parent_id") == "AR-ADVREG-01":
            row.pop("parent_id")
    out = decide_as0_session(
        trials_dir_ready=True, anti_fp_signed=True, adv=bad
    )
    assert out.startswith("KILL")
    assert "AR-ADVREG-01" in out


def test_given_para_when_fields_then_gold_and_source() -> None:
    for item in AS0_PARAEXT2_PACK:
        assert item["source_id"]
        assert item["parent_question"].strip()
        assert item["paraphrase"].strip()
        assert item["gold"].strip()
        assert item["id"].startswith("AS-EXT2-")
