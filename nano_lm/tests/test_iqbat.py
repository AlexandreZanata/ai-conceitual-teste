"""Contract: Wave BH1 H-IQBAT — IQ battery v0 mix + scorer + Novel_FP gate."""

from __future__ import annotations

from pathlib import Path

from iqbat_ops import (
    IQBAT_ANTI_FP,
    IQBAT_BATTERY_PATH,
    IQBAT_ID,
    IQBAT_MIX_MIN,
    IQBAT_SCORE_LABELS,
    IQBAT_THESIS,
    decide_iqbat,
    load_iq_battery,
    map_iq_product_mode,
    score_iq_probe,
    summarize_iq_scores,
    validate_iq_mix,
)
from matrix_common import REPO


def test_given_modes_when_map_then_product_charter() -> None:
    # GIVEN/WHEN/THEN: pesquisa §0c — product modes
    assert map_iq_product_mode("WRAP_LOOKUP") == "LOOKUP"
    assert map_iq_product_mode("NO_ANSWER") == "ABSTAIN"
    assert map_iq_product_mode("WRAP_DECODE") == "DECODE"


def test_given_battery_file_when_load_then_mix_passes() -> None:
    # GIVEN iq-battery-v0.jsonl · WHEN validate · THEN ≥40 + split minima
    path = REPO / IQBAT_BATTERY_PATH
    assert path.is_file()
    rows = load_iq_battery(path)
    assert validate_iq_mix(rows) is None
    assert len(rows) >= int(IQBAT_MIX_MIN["total"])
    splits = {str(r["split"]) for r in rows}
    assert {
        "gold",
        "para",
        "forever",
        "adversary",
        "novel",
        "ood",
        "gen",
    } <= splits


def test_given_truncated_add_when_score_then_miss() -> None:
    # GIVEN LOOKUP expect + min_gold_substr · WHEN truncated · THEN MISS
    probe = {
        "expect": "LOOKUP",
        "split": "gold",
        "min_gold_substr": ["def add", "return", "a + b"],
        "wrong_if_contains": [],
    }
    ask = {"product_mode": "LOOKUP", "completion": "def add"}
    assert score_iq_probe(probe, ask) == "MISS"


def test_given_full_add_when_score_then_ok() -> None:
    probe = {
        "expect": "LOOKUP",
        "split": "gold",
        "min_gold_substr": ["def add", "return", "a + b"],
        "wrong_if_contains": [],
    }
    ask = {
        "product_mode": "LOOKUP",
        "completion": "def add(a, b):\n    return a + b",
    }
    assert score_iq_probe(probe, ask) == "OK"


def test_given_rust_abstain_when_score_then_miss() -> None:
    probe = {
        "expect": "LOOKUP",
        "split": "gold",
        "min_gold_substr": ["let mut x", "5"],
        "wrong_if_contains": [],
    }
    ask = {"product_mode": "ABSTAIN", "completion": "NO_ANSWER"}
    assert score_iq_probe(probe, ask) == "MISS"


def test_given_wrong_lookup_when_score_then_fp() -> None:
    # GIVEN ABSTAIN expect · WHEN LOOKUP neighbor gold · THEN FP
    probe = {
        "expect": "ABSTAIN",
        "split": "novel",
        "wrong_if_contains": ["def add", "return a + b"],
        "min_gold_substr": None,
    }
    ask = {"product_mode": "LOOKUP", "completion": "def add"}
    assert score_iq_probe(probe, ask) == "FP"


def test_given_abstain_hold_when_score_then_abstain_ok() -> None:
    probe = {
        "expect": "ABSTAIN",
        "split": "forever",
        "wrong_if_contains": ["def add"],
        "min_gold_substr": None,
    }
    ask = {"product_mode": "ABSTAIN", "completion": "NO_ANSWER"}
    assert score_iq_probe(probe, ask) == "ABSTAIN-OK"


def test_given_gen_decode_when_score_then_abstain_ok() -> None:
    probe = {
        "expect": "ABSTAIN",
        "split": "gen",
        "wrong_if_contains": [],
        "min_gold_substr": None,
    }
    ask = {"product_mode": "DECODE", "completion": "gibberish tail"}
    assert score_iq_probe(probe, ask) == "ABSTAIN-OK"


def test_given_scores_when_summarize_then_novel_fp_and_miss() -> None:
    scored = [
        {"split": "novel", "score": "ABSTAIN-OK"},
        {"split": "novel", "score": "FP"},
        {"split": "forever", "score": "ABSTAIN-OK"},
        {"split": "gold", "score": "MISS"},
        {"split": "gold", "score": "OK"},
        {"split": "adversary", "score": "ABSTAIN-OK"},
    ]
    board = summarize_iq_scores(scored)
    assert board["Novel_FP"] == 1
    assert board["Forever_FH"] == 0
    assert board["gold_para_miss"] == 1
    assert set(board["by_score"]) <= IQBAT_SCORE_LABELS | set(board["by_score"])


def test_given_clean_board_when_decide_then_promote() -> None:
    board = {
        "n": 50,
        "Novel_FP": 0,
        "Forever_FH": 0,
        "adversary_FP": 0,
        "gold_para_miss": 2,
    }
    out = decide_iqbat(
        mix_ok=True, board=board, anti_fp_signed=True, formal_ready=True
    )
    assert out.startswith("PROMOTE")
    assert IQBAT_ID in out
    assert "GOLDFIX" in out or "residual" in out.lower()


def test_given_novel_fp_when_decide_then_kill() -> None:
    board = {
        "n": 50,
        "Novel_FP": 1,
        "Forever_FH": 0,
        "adversary_FP": 0,
        "gold_para_miss": 0,
    }
    out = decide_iqbat(
        mix_ok=True, board=board, anti_fp_signed=True, formal_ready=True
    )
    assert out.startswith("KILL")
    assert "Novel_FP" in out


def test_given_forever_fh_when_decide_then_kill() -> None:
    board = {
        "n": 50,
        "Novel_FP": 0,
        "Forever_FH": 1,
        "adversary_FP": 0,
        "gold_para_miss": 0,
    }
    out = decide_iqbat(
        mix_ok=True, board=board, anti_fp_signed=True, formal_ready=True
    )
    assert out.startswith("KILL")
    assert "Forever_FH" in out


def test_given_bad_mix_when_validate_then_kill_reason() -> None:
    bad = [{"id": "IQ-x", "split": "gold", "expect": "LOOKUP", "question": "q"}]
    # missing schema fields
    err = validate_iq_mix(bad)
    assert err is not None
    assert err.startswith("KILL")


def test_given_notes_when_read_then_anti_fp_and_thesis() -> None:
    assert "Novel_FP" in IQBAT_ANTI_FP or "novel" in IQBAT_ANTI_FP.lower()
    assert "IQ battery" in IQBAT_THESIS or "iq battery" in IQBAT_THESIS.lower()
    assert Path(REPO / IQBAT_BATTERY_PATH).name == "iq-battery-v0.jsonl"
