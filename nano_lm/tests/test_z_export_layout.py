"""Contract: Z0 export writes champion layout under wave-z/models/champion."""

from __future__ import annotations

import json
from pathlib import Path

from run_z_export import export_champion
from z_recipe import validate_recipe

OUT = Path("results/nano-lm/wave-z/models/champion")


def test_given_export_when_run_then_layout_ok(tmp_path: Path) -> None:
    dest = tmp_path / "champion"
    manifest = export_champion(seed=0, out=dest)
    assert manifest["status"] == "EXPORT_OK"
    assert (dest / "recipe.json").is_file()
    assert (dest / "MANIFEST.json").is_file()
    recipe = json.loads((dest / "recipe.json").read_text(encoding="utf-8"))
    assert validate_recipe(recipe) == []
    assert (dest / recipe["ckpt"]).is_file()
    assert (dest / recipe["early_gene"]).is_file()
    assert (dest / recipe["ckpt"]).stat().st_size > 1_000_000


def test_given_repo_champion_when_present_then_recipe_ok() -> None:
    """Live artifact after `npm run nano:z:export` (skip if not exported)."""
    path = OUT / "recipe.json"
    if not path.is_file():
        return
    recipe = json.loads(path.read_text(encoding="utf-8"))
    assert validate_recipe(recipe) == []
    assert (OUT / "MANIFEST.json").is_file()
    assert (OUT / recipe["ckpt"]).is_file()
