"""Smoke H-SHORTB: SHORT under FUSEB dual-budget batch vs tip FUSEB."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import yaml

from chunk_fit import long_prompts
from chunk_ops import LONG_TARGET_TOKENS
from eval_decode import load_pair
from load_model import resolve_device
from matrix_common import matrix_cfg, write_json
from short_ops import clamp_short_gene
from shortb_ops import SHORTB_CHUNK
from shortb_score import SMOKE_BUDGETS, score_batch_fuseb, score_batch_shortb, tip_row


def _early_gene(out: Path, seed: int) -> dict[str, Any]:
    path = out / f"HEARLY_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing EARLY tip: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"EARLY missing best_gene: {path}")
    return gene


def _short_gene(out: Path, seed: int, tip: dict[str, Any]) -> dict[str, Any]:
    path = out / f"HSHORT_seed{seed}_eval.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing SHORT util: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene") or {}
    if "draft_max" not in gene or "stop_conf" not in gene:
        raise ValueError(f"SHORT missing draft_max/stop_conf: {path}")
    return clamp_short_gene(gene, tip)


def _kv_threshold(out: Path, seed: int) -> int:
    path = out / f"HKVSEL_seed{seed}_eval.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing KVSEL util: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene") or {}
    if "kv_threshold" not in gene:
        raise ValueError(f"KVSEL missing kv_threshold: {path}")
    return int(gene["kv_threshold"])


def _load_texts(*paths: Path) -> list[str]:
    texts: list[str] = []
    for path in paths:
        with path.open(encoding="utf-8") as f:
            texts.extend(p["text"] for p in yaml.safe_load(f)["prompts"])
    return texts


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("WARN: CUDA unavailable; smoke will be slow/CPU", file=sys.stderr)
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    from data_tiny import load_tokenizer

    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    raw = _load_texts(c["prompts"], c["fit_prompts"])
    prompts = long_prompts(raw, tok, target_tokens=LONG_TARGET_TOKENS)
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        early = _early_gene(out, seed)
        gene = {**early, "n": 1, "temperature": 1e-6}
        short = _short_gene(out, seed, gene)
        thr = _kv_threshold(out, seed)
        teacher, student = load_pair(
            out / f"B2_seed{seed}.pt",
            c["teacher_id"],
            c["tokenizer_id"],
            c["cache"],
        )
        claim = seed + 6868
        fuseb = score_batch_fuseb(
            teacher=teacher,
            student=student,
            prompts=prompts,
            gene=gene,
            seed=claim,
            kv_threshold=thr,
            chunk_size=SHORTB_CHUNK,
        )
        g_tip = {
            **gene,
            "kv_threshold": thr,
            "chunk_size": SHORTB_CHUNK,
            "backend": "sdpa+kvsel+chbat",
        }
        rows.append(tip_row("H-FUSEB", f"HFUSEB_shortb_seed{seed}", fuseb, seed, g_tip))
        shortb = score_batch_shortb(
            teacher=teacher,
            student=student,
            prompts=prompts,
            gene=gene,
            short=short,
            seed=claim,
            kv_threshold=thr,
            chunk_size=SHORTB_CHUNK,
        )
        g = {
            **gene,
            "draft_max": short["draft_max"],
            "stop_conf": short["stop_conf"],
            "kv_threshold": thr,
            "chunk_size": SHORTB_CHUNK,
            "backend": "sdpa+kvsel+short+chbat",
        }
        row = tip_row("H-SHORTB", f"HSHORTB_seed{seed}", shortb, seed, g)
        write_json(out / f"HSHORTB_seed{seed}_eval.json", row)
        rows.append(row)
    write_json(
        out / "shortb_smoke.json",
        {
            "rows": rows,
            "wall_s": time.perf_counter() - t0,
            "n_prompts": len(prompts),
            "chunk_size": SHORTB_CHUNK,
            "budgets": list(SMOKE_BUDGETS),
            "target_tokens": LONG_TARGET_TOKENS,
            "mode": "dual-budget SHORT under FUSEB; n=1 near-greedy; long prompts",
        },
    )
    print(json.dumps({"n_rows": len(rows), "out": str(out / "shortb_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
