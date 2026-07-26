"""Contract: Wave AA1 H-PARA — paraphrase Z1 asks; no wrap false-hit; pass or document brittleness."""

from __future__ import annotations

import json
from pathlib import Path

from para_ops import (
    PARA_ID,
    PARA_N,
    PARA_PACK,
    PASS_MAX_ERRORS,
    PASS_MEAN,
    classify_lookup,
    decide_para,
    para_stats,
    paraphrase_collides_bank,
    score_para_trial,
)
from z_wrap import lookup_gold, normalize_question


def test_given_pack_when_loaded_then_exactly_ten() -> None:
    # GIVEN/WHEN/THEN: pesquisa §8.1 AA1 — paraphrase Z1–Z4 asks ×10
    assert PARA_ID == "H-PARA"
    assert len(PARA_PACK) == PARA_N == 10
    paras = [p["paraphrase"] for p in PARA_PACK]
    assert len(set(paras)) == 10
    parents = [p["parent_question"] for p in PARA_PACK]
    assert len(set(parents)) == 10


def test_given_pack_when_normalize_then_no_parent_collision() -> None:
    for item in PARA_PACK:
        assert normalize_question(item["paraphrase"]) != normalize_question(
            item["parent_question"]
        )


def test_given_bank_parents_when_para_then_no_bank_key_collision() -> None:
    rows = [
        {"question": p["parent_question"], "gold": p["parent_gold"]} for p in PARA_PACK
    ]
    assert paraphrase_collides_bank(PARA_PACK, rows) == []


def test_given_exact_parent_when_classify_then_true_hit() -> None:
    rows = [{"question": "What is a BIP?", "gold": "A design doc."}]
    gold = lookup_gold("What is a BIP?", rows)
    kind = classify_lookup(gold, "A design doc.")
    assert kind == "TRUE_HIT"


def test_given_wrong_gold_when_classify_then_false_hit() -> None:
    kind = classify_lookup("wrong gold text", "A design doc.")
    assert kind == "FALSE_HIT"


def test_given_miss_when_classify_then_miss() -> None:
    assert classify_lookup(None, "A design doc.") == "MISS"


def test_given_false_hit_when_score_then_zero_error() -> None:
    score, err, notes = score_para_trial(
        mode="WRAP_LOOKUP",
        completion="other gold",
        parent_gold="correct gold",
        lookup_kind="FALSE_HIT",
    )
    assert score == 0.0
    assert err is True
    assert "false-hit" in notes[0].lower() or "FALSE" in notes[0]


def test_given_true_hit_when_score_then_nine() -> None:
    g = "def add(a, b):\n    return a + b"
    score, err, _ = score_para_trial(
        mode="WRAP_LOOKUP",
        completion=g,
        parent_gold=g,
        lookup_kind="TRUE_HIT",
    )
    assert score == 9.0
    assert err is False


def test_given_miss_period_when_score_then_error() -> None:
    score, err, _ = score_para_trial(
        mode="WRAP_DECODE",
        completion="........",
        parent_gold="let mut x = 5;",
        lookup_kind="MISS",
    )
    assert score < PASS_MEAN
    assert err is True


def test_given_high_mean_no_false_when_decide_then_promote() -> None:
    stats = para_stats(
        [9.0] * 10,
        [False] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_miss=0,
    )
    assert stats["pass_bar"] is True
    assert decide_para(stats) == "PROMOTE"


def test_given_misses_no_false_when_decide_then_hold_brittle() -> None:
    # Gate: mean≥7 OR document lookup brittleness
    stats = para_stats(
        [1.0] * 10,
        [True] * 10,
        n_true_hit=0,
        n_false_hit=0,
        n_miss=10,
    )
    assert stats["pass_bar"] is False
    assert decide_para(stats) == "HOLD"


def test_given_any_false_hit_when_decide_then_kill() -> None:
    stats = para_stats(
        [9.0] * 9 + [0.0],
        [False] * 9 + [True],
        n_true_hit=9,
        n_false_hit=1,
        n_miss=0,
    )
    assert decide_para(stats) == "KILL"


def test_given_constants_when_loaded_then_match_pesquisa() -> None:
    assert PASS_MEAN == 7.0
    assert PASS_MAX_ERRORS == 3


def test_given_tmp_bank_when_para_ask_then_miss_not_false(tmp_path: Path) -> None:
    """Integration-light: paraphrase must not WRAP_LOOKUP against parent bank."""
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
    item = PARA_PACK[0]
    bank = tmp_path / "bank.jsonl"
    bank.write_text(
        json.dumps(
            {
                "trial_id": "Z1-01",
                "question": item["parent_question"],
                "source_id": item["source_id"],
                "model_raw": "........",
                "gold": item["parent_gold"],
                "score": 1.0,
                "error": True,
                "recipe_id": recipe["recipe_id"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    # Pure miss path would need CUDA; assert lookup only.
    assert lookup_gold(item["paraphrase"], [{"question": item["parent_question"], "gold": item["parent_gold"]}]) is None
    assert classify_lookup(None, item["parent_gold"]) == "MISS"
