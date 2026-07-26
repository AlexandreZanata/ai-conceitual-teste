"""Contract: Wave AA4 H-DEPL-DOC — one-pagers match DEPL-Y (no new hyps)."""

from __future__ import annotations

from depl_doc_ops import (
    AA_OUTCOME_MARKERS,
    CORE_MARKERS,
    DEPL_DOC_ID,
    ONE_PAGERS,
    decide_depl_doc,
    missing_markers,
    page_sync_report,
)
from depl_y_ops import DEPL_Y_ROUTES


def test_given_id_when_loaded_then_hdepldoc() -> None:
    # GIVEN/WHEN/THEN: pesquisa §8.1 AA4 — public one-pager sync
    assert DEPL_DOC_ID == "H-DEPL-DOC"
    assert len(ONE_PAGERS) >= 3
    assert "RECIPES.md" in ONE_PAGERS[0] or any("RECIPES" in p for p in ONE_PAGERS)


def test_given_full_text_when_missing_then_empty() -> None:
    body = " ".join(CORE_MARKERS) + " " + " ".join(
        f"{a} {b}" for a, b in AA_OUTCOME_MARKERS
    )
    assert missing_markers(body, CORE_MARKERS) == []


def test_given_gap_when_missing_then_lists() -> None:
    miss = missing_markers("H-ZWRAP only", CORE_MARKERS)
    assert "H-PACK" in miss or len(miss) >= 1


def test_given_page_ok_when_report_then_ok() -> None:
    body = (
        "DEPL-Y H-PACK QPFB2 ROLL H-ZWRAP H-ZERR STREAM KILL "
        "H-WRAPBANK PROMOTE H-PARA HOLD H-ZPREF KILL"
    )
    rep = page_sync_report("docs/results/nano-lm/RECIPES.md", body)
    assert rep["ok"] is True
    assert rep["missing"] == []


def test_given_page_gap_when_report_then_not_ok() -> None:
    rep = page_sync_report("docs/results/nano-lm/RECIPES.md", "hello")
    assert rep["ok"] is False
    assert len(rep["missing"]) > 0


def test_given_all_ok_when_decide_then_promote() -> None:
    reps = [
        {"path": p, "ok": True, "missing": []} for p in ONE_PAGERS
    ]
    assert decide_depl_doc(reps) == "PROMOTE"


def test_given_one_gap_when_decide_then_kill() -> None:
    reps = [{"path": p, "ok": True, "missing": []} for p in ONE_PAGERS]
    reps[0] = {"path": ONE_PAGERS[0], "ok": False, "missing": ["H-PACK"]}
    out = decide_depl_doc(reps)
    assert out.startswith("KILL")
    assert "H-PACK" in out or ONE_PAGERS[0] in out


def test_given_depl_y_hitl_when_route_then_includes_wrapbank() -> None:
    # Sync: DEPL-Y hitl route must mention WRAPBANK after AA0
    assert "H-WRAPBANK" in DEPL_Y_ROUTES["hitl_known"]
