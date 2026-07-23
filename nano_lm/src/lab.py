"""Terminal laboratory: one-line progress bar + end summary."""

from __future__ import annotations

import json
import sys
import threading
import time
from pathlib import Path
from typing import Any

import torch

from aggregate import summarize, to_markdown
from lab_display import end_status, render_summary, status_line, write_status
from load_model import load_causal_lm
from run_bench import (
    ROOT,
    load_config,
    load_prompts,
    record_row,
    resolve_config,
    run_method,
)
from telemetry import Telemetry


def _jobs(cfg: dict[str, Any], prompts: list[dict[str, str]]):
    for method in cfg["methods"]:
        for prompt in prompts:
            for seed in cfg["seeds"]:
                yield method, prompt, seed


def _out_dir(cfg: dict[str, Any]) -> Path:
    out_dir = Path(cfg["out_dir"])
    if not out_dir.is_absolute():
        out_dir = ROOT.parent / out_dir
    return out_dir.parent / f"{out_dir.name}-lab"


def _start_ui(state: dict[str, Any], total: int, t0: float, tel: Telemetry):
    stop = threading.Event()

    def loop() -> None:
        while not stop.wait(0.2):
            gpu, _, _ = tel.snapshot()
            write_status(
                status_line(
                    done=state["done"],
                    total=total,
                    elapsed_s=time.perf_counter() - t0,
                    current=state["current"],
                    gpu=gpu,
                )
            )

    thread = threading.Thread(target=loop, daemon=True)
    thread.start()
    return stop


def _run_jobs(jobs, loaded, cfg, out_file, state) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with out_file.open("w", encoding="utf-8") as f:
        for i, (method, prompt, seed) in enumerate(jobs):
            state["done"] = i
            state["current"] = f"{method}/{prompt['id']}/s{seed}"
            result = run_method(method, loaded, prompt["text"], cfg, seed)
            row = record_row(method, prompt, seed, result)
            rows.append(row)
            f.write(json.dumps(row) + "\n")
            f.flush()
            if loaded.device.type == "cuda":
                torch.cuda.empty_cache()
    return rows


def run_lab(cfg_path: Path) -> int:
    if not torch.cuda.is_available():
        print("ERROR: nano:lab requires CUDA.", file=sys.stderr)
        return 2
    cfg = load_config(cfg_path)
    prompts = load_prompts(ROOT / cfg["prompts_path"])
    jobs = list(_jobs(cfg, prompts))
    cache = ROOT / ".cache"
    cache.mkdir(parents=True, exist_ok=True)
    print(f"Nano-LM Lab | {cfg['model_id']} | loading CUDA fp16…", flush=True)
    loaded = load_causal_lm(
        cfg["model_id"], cfg["tokenizer_id"], cache_dir=cache,
        prefer_cuda=True, use_fp16=True,
    )
    out_dir = _out_dir(cfg)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "runs.jsonl"
    state = {"done": 0, "current": "starting"}
    t0 = time.perf_counter()
    device = f"{loaded.device} | dtype={loaded.dtype}"
    tel = Telemetry()
    tel.start(0.25)
    stop_ui = _start_ui(state, len(jobs), t0, tel)
    try:
        rows = _run_jobs(jobs, loaded, cfg, out_file, state)
        state["done"] = len(jobs)
        state["current"] = "DONE"
        time.sleep(0.3)
    finally:
        stop_ui.set()
        tel.stop()
        end_status()
    gpu, hist, cores = tel.snapshot()
    print(render_summary(
        model_id=cfg["model_id"], device=device, gpu=gpu,
        hist=hist, cpu_cores=cores, rows=rows,
    ))
    md = out_dir / "lab-summary.md"
    md.write_text(to_markdown(summarize(rows), str(out_file)), encoding="utf-8")
    print(f"Wrote {out_file}\nWrote {md}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    cfg_arg = "configs/lab_gpu.json"
    if args and args[0] in {"--config", "-c"} and len(args) >= 2:
        cfg_arg = args[1]
    elif args:
        cfg_arg = args[0]
    return run_lab(resolve_config(cfg_arg))


if __name__ == "__main__":
    raise SystemExit(main())
