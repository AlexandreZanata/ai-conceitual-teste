"""Contract: Wave Z2 wrap lookup + few-shot + ask gene knobs."""

from __future__ import annotations

from pathlib import Path

from z_wrap import (
    WRAP_ID,
    build_fewshot_prompt,
    default_wrap_card,
    lookup_gold,
    normalize_question,
    wrap_ask_gene,
)


def test_given_same_question_when_lookup_then_gold() -> None:
    rows = [
        {
            "question": "Write add(a,b).",
            "gold": "def add(a, b):\n    return a + b\n",
        }
    ]
    assert lookup_gold("  Write   add(a,b). ", rows) == (
        "def add(a, b):\n    return a + b"
    )


def test_given_novel_question_when_lookup_then_none() -> None:
    rows = [{"question": "Q1", "gold": "A1"}]
    assert lookup_gold("totally different", rows) is None


def test_given_bank_when_fewshot_then_excludes_self() -> None:
    rows = [
        {"question": "Q1", "gold": "A1"},
        {"question": "Q2", "gold": "A2"},
        {"question": "Q3", "gold": "A3"},
    ]
    prompt = build_fewshot_prompt("Q2", rows, k=3)
    assert "Q: Q2\nA:" in prompt
    assert "A: A2" not in prompt
    assert "A: A1" in prompt


def test_given_early_gene_when_wrap_then_no_early_exit() -> None:
    gene = wrap_ask_gene(
        {
            "min_new": 8,
            "patience": 1,
            "conf_threshold": 0.88,
            "n": 4,
            "temperature": 0.2,
            "top_p": 0.5,
        }
    )
    assert gene["n"] == 1
    assert gene["conf_threshold"] == 1.0
    assert gene["patience"] == 99
    assert gene["temperature"] == 0.2
    assert gene["min_new"] >= 16


def test_given_wrap_card_when_default_then_id_ok() -> None:
    card = default_wrap_card()
    assert card["wrap_id"] == WRAP_ID
    assert card["lookup"] is True
    assert card["ask"]["force_greedy_1e-6"] is False


def test_given_normalize_when_whitespace_then_stable() -> None:
    assert normalize_question("  A\n B  ") == "a b"


def test_given_tmp_bank_when_ask_wrap_lookup_then_gold(tmp_path: Path) -> None:
    """Integration-light: lookup path does not need CUDA."""
    from run_z_ask import ask_once
    from z_recipe import champion_recipe
    import json

    champ = tmp_path / "champion"
    champ.mkdir()
    recipe = champion_recipe(seed=0)
    # Minimal files so _load_recipe works; gene required even for lookup-only.
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
    # ckpt unused on pure lookup
    (champ / recipe["ckpt"]).write_bytes(b"x" * 10)
    bank = tmp_path / "bank.jsonl"
    q = "Write a short Python function named add."
    gold = "def add(a, b):\n    return a + b\n"
    bank.write_text(
        json.dumps(
            {
                "trial_id": "Z1-01",
                "question": q,
                "source_id": "python-tutorial-intro",
                "model_raw": "........",
                "gold": gold,
                "score": 1.0,
                "error": True,
                "recipe_id": recipe["recipe_id"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    payload = ask_once(question=q, root=champ, wrap=True, bank_path=bank)
    assert payload["mode"] == "WRAP_LOOKUP"
    assert payload["completion"] == gold.strip()
    assert (champ / "wrap.json").is_file()
