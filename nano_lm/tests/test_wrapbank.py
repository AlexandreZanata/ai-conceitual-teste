"""Contract: Wave AA0 H-WRAPBANK — expand wrap golds; HITL pass bar; no weight update."""

from __future__ import annotations

import json
from pathlib import Path

from wrapbank_ops import (
    PASS_MAX_ERRORS,
    PASS_MEAN,
    WRAPBANK_ID,
    WRAPBANK_N,
    WRAPBANK_PACK,
    bank_row_from_item,
    decide_wrapbank,
    expand_bank_rows,
    missing_pack_source_ids,
    new_questions_not_in_bank,
    score_wrap_hit,
    wrapbank_stats,
)
from z_error_bank import validate_error_row
from z_wrap import lookup_gold


def test_given_pack_when_loaded_then_exactly_ten_scoped() -> None:
    # GIVEN/WHEN/THEN: pesquisa §8.1 AA0 — HITL×10 new scoped Qs
    assert WRAPBANK_ID == "H-WRAPBANK"
    assert len(WRAPBANK_PACK) == WRAPBANK_N == 10
    qs = [p["question"] for p in WRAPBANK_PACK]
    assert len(set(qs)) == 10
    for item in WRAPBANK_PACK:
        assert item["source_id"]
        assert item["gold"].strip()
        assert item["question"].strip()


def test_given_registry_when_pack_then_all_source_ids_known() -> None:
    from curated_sources import source_ids

    miss = missing_pack_source_ids(set(source_ids()))
    assert miss == []


def test_given_pack_item_when_bank_row_then_schema_ok() -> None:
    row = bank_row_from_item(WRAPBANK_PACK[0], trial_id="AA0-01")
    assert validate_error_row(row) == []
    assert row["error"] is False
    assert row["recipe_id"] == "champion-wrap-v0"
    assert "gold" in row and row["gold"].strip()


def test_given_empty_bank_when_expand_then_all_ten_appended() -> None:
    added, merged = expand_bank_rows([], WRAPBANK_PACK)
    assert len(added) == 10
    assert len(merged) == 10
    for item in WRAPBANK_PACK:
        assert lookup_gold(item["question"], merged) == item["gold"].strip()


def test_given_existing_pack_when_expand_then_idempotent() -> None:
    _, once = expand_bank_rows([], WRAPBANK_PACK)
    added, twice = expand_bank_rows(once, WRAPBANK_PACK)
    assert added == []
    assert len(twice) == 10


def test_given_partial_bank_when_new_questions_then_only_missing() -> None:
    seed = [bank_row_from_item(WRAPBANK_PACK[0], trial_id="AA0-01")]
    miss = new_questions_not_in_bank(seed, WRAPBANK_PACK)
    assert len(miss) == 9
    assert WRAPBANK_PACK[0]["question"] not in [m["question"] for m in miss]


def test_given_wrap_lookup_when_score_then_nine_no_error() -> None:
    # Same product contract as Z2/Z4 WRAP_LOOKUP
    score, err, notes = score_wrap_hit("def add(a,b): return a+b", "def add(a,b): return a+b")
    assert score == 9.0
    assert err is False
    assert len(notes) == 3


def test_given_miss_or_empty_when_score_then_error() -> None:
    score, err, _ = score_wrap_hit("........", "gold answer")
    assert score < PASS_MEAN
    assert err is True


def test_given_ten_hits_when_stats_then_promote() -> None:
    stats = wrapbank_stats([9.0] * 10, [False] * 10, n_lookup=10)
    assert stats["pass_bar"] is True
    assert decide_wrapbank(stats) == "PROMOTE"
    assert stats["n_lookup"] == 10
    assert stats["weight_update"] is False


def test_given_too_many_errors_when_decide_then_kill() -> None:
    stats = wrapbank_stats([9.0] * 6 + [1.0] * 4, [False] * 6 + [True] * 4, n_lookup=6)
    assert stats["pass_bar"] is False
    assert decide_wrapbank(stats) == "KILL"


def test_given_constants_when_loaded_then_match_pesquisa() -> None:
    assert PASS_MEAN == 7.0
    assert PASS_MAX_ERRORS == 3


def test_given_tmp_bank_when_ask_wrap_new_golds_then_lookup(tmp_path: Path) -> None:
    """Integration-light: expanded bank answers new asks without CUDA."""
    from run_z_ask import ask_once
    from z_recipe import champion_recipe

    champ = tmp_path / "champion"
    champ.mkdir()
    recipe = champion_recipe(seed=0)
    (champ / "recipe.json").write_text(json.dumps(recipe), encoding="utf-8")
    gene_path = champ / recipe["early_gene"]
    gene_path.parent.mkdir(parents=True, exist_ok=True)
    gene_path.write_text(
        json.dumps(
            {
                "best_gene": {
                    "min_new": 8,
                    "patience": 1,
                    "conf_threshold": 0.9,
                    "n": 1,
                    "temperature": 0.2,
                    "top_p": 0.5,
                }
            }
        ),
        encoding="utf-8",
    )
    (champ / recipe["ckpt"]).write_bytes(b"x" * 10)
    bank = tmp_path / "bank.jsonl"
    item = WRAPBANK_PACK[0]
    row = bank_row_from_item(item, trial_id="AA0-01")
    bank.write_text(json.dumps(row) + "\n", encoding="utf-8")
    payload = ask_once(
        question=item["question"], root=champ, wrap=True, bank_path=bank
    )
    assert payload["mode"] == "WRAP_LOOKUP"
    assert payload["completion"] == item["gold"].strip()
