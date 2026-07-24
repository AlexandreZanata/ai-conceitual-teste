"""Formal-budget H-TMN vs tip TYP+MINP; shared B2 ckpts."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch

from hold_ops import assert_disjoint, load_prompt_ids
from hyp_tmn import run_h_tmn
from load_model import resolve_device
from matrix_common import REPO, write_json
from run_formal_hdeck import formal_cfg as hdeck_formal_cfg


def formal_cfg() -> dict[str, Any]:
    base = hdeck_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-htmn"
    base["ckpt_dir"] = REPO / "results/nano-lm/formal-hdeck-b4"
    base["typ_dir"] = REPO / "results/nano-lm/formal-htyp"
    base["minp_dir"] = REPO / "results/nano-lm/formal-hminp"
    return base


def _tip_rows(path: Path, family: str) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [r for r in data["rows"] if r.get("family") == family]


def run_formal() -> int:
    c = formal_cfg()
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    device = resolve_device(True)
    c["out"].mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    rows.extend(_tip_rows(c["typ_dir"] / "formal.json", "H-TYP"))
    rows.extend(_tip_rows(c["minp_dir"] / "formal.json", "H-MINP"))
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        b2 = c["ckpt_dir"] / f"B2_seed{seed}.pt"
        typ_train = c["typ_dir"] / f"HTYP_seed{seed}_train.json"
        minp_train = c["minp_dir"] / f"HMINP_seed{seed}_train.json"
        for p in (b2, typ_train, minp_train):
            if not p.is_file():
                raise FileNotFoundError(f"missing formal tip artifact: {p}")
        meta = run_h_tmn(
            student_ckpt=b2,
            teacher_id=c["teacher_id"],
            tokenizer_id=c["tokenizer_id"],
            prompts_path=c["fit_prompts"],
            eval_prompts_path=c["prompts"],
            cache_dir=c["cache"],
            max_new=c["max_new_fit"],
            eval_max_new=c["max_new_eval"],
            seed=seed,
            typ_train=typ_train,
            minp_train=minp_train,
            out_meta=c["out"] / f"HTMN_seed{seed}_train.json",
        )
        rows.append(
            {
                "family": "H-TMN",
                "label": f"HTMN_seed{seed}",
                "teacher_mean_logprob": float(meta["eval_fit"]),
                "mean_wall_ms": float(meta["eval_wall_ms"]),
                "typ_mass": float(meta["typ_mass"]),
                "min_p": float(meta["min_p"]),
                "seed": seed,
            }
        )
        if device.type == "cuda":
            torch.cuda.empty_cache()
    payload = {
        "rows": rows,
        "wall_s": time.perf_counter() - t0,
        "config": {k: str(v) if isinstance(v, Path) else v for k, v in c.items()},
    }
    write_json(c["out"] / "formal.json", payload)
    print(json.dumps({"n_rows": len(rows), "out": str(c["out"] / "formal.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
