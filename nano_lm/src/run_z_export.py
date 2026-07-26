"""Z0 EXPORT: freeze champion QPFB2 ckpt+gene → wave-z/models/champion/."""

from __future__ import annotations

import json
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Any

from matrix_common import REPO, write_json
from run_formal_hprog import formal_cfg
from tipd_pair import tune_cpu_threads
from z_recipe import champion_recipe, validate_recipe

_OUT = REPO / "results/nano-lm/wave-z/models/champion"


def export_champion(*, seed: int = 0, out: Path | None = None) -> dict[str, Any]:
    """
    GIVEN formal B2 + EARLY artifacts
    WHEN exporting Wave Z champion
    THEN copy ckpt+gene, write recipe.json + MANIFEST.json under out/.
    """
    dest = Path(out) if out is not None else _OUT
    cfg = formal_cfg()
    recipe = champion_recipe(seed=seed)
    errs = validate_recipe(recipe)
    if errs:
        raise ValueError("invalid recipe: " + "; ".join(errs))
    ckpt_src = Path(cfg["ckpt_dir"]) / recipe["ckpt"]
    gene_src = Path(cfg["early_dir"]) / f"HEARLY_seed{int(seed)}_train.json"
    if not ckpt_src.is_file():
        raise FileNotFoundError(f"missing ckpt: {ckpt_src}")
    if not gene_src.is_file():
        raise FileNotFoundError(f"missing early gene: {gene_src}")
    genes_dir = dest / "genes"
    genes_dir.mkdir(parents=True, exist_ok=True)
    ckpt_dst = dest / recipe["ckpt"]
    gene_dst = dest / recipe["early_gene"]
    shutil.copy2(ckpt_src, ckpt_dst)
    shutil.copy2(gene_src, gene_dst)
    write_json(dest / "recipe.json", recipe)
    manifest = {
        "recipe_id": recipe["recipe_id"],
        "seed": int(seed),
        "out": str(dest),
        "ckpt_src": str(ckpt_src),
        "gene_src": str(gene_src),
        "ckpt_bytes": int(ckpt_dst.stat().st_size),
        "exported_at_unix": time.time(),
        "stage": "Z0",
        "status": "EXPORT_OK",
    }
    write_json(dest / "MANIFEST.json", manifest)
    return manifest


def main() -> int:
    for key in (
        "http_proxy",
        "https_proxy",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "all_proxy",
    ):
        os.environ.pop(key, None)
    threads = tune_cpu_threads(max(4, int(os.cpu_count() or 4) - 2))
    seed = 0
    if "--seed" in sys.argv:
        i = sys.argv.index("--seed")
        seed = int(sys.argv[i + 1])
    try:
        manifest = export_champion(seed=seed)
    except (OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "ok": True,
                "out": manifest["out"],
                "recipe_id": manifest["recipe_id"],
                "cpu_threads": threads,
                "stage": "Z0",
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
