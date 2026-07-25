"""Formal H-MIXD: STAG curriculum + prog mix (fit≠eval story prompts)."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import torch

from load_model import resolve_device
from matrix_common import REPO, write_json
from mixd_data import assert_mixd_holdout
from mixd_ops import MIX_FRAC, decide_hmixd
from mixd_pair import means_from_rows, run_seed_pair
from run_formal_htpack import formal_cfg as htpack_formal_cfg
from tipd_pair import tune_cpu_threads


def formal_cfg() -> dict[str, Any]:
    base = htpack_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hmixd"
    return base


def run_formal() -> int:
    threads = tune_cpu_threads(max(4, int(os.cpu_count() or 4) - 2))
    assert_mixd_holdout()
    c = formal_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        raise RuntimeError("H-MIXD formal requires CUDA")
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    steps = int(c.get("steps_cur", c["steps_kd"]))
    rows: list = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        print(json.dumps({"phase": "train", "seed": seed}), flush=True)
        rows.extend(run_seed_pair(c, out, seed, device, steps))
        torch.cuda.empty_cache()
    means = means_from_rows(rows)
    decision = decide_hmixd(
        mix_story_lp=means["H-MIXD:story_lp"],
        ctrl_story_lp=means["H-STAG-CTRL:story_lp"],
        mix_prog_ppl=means["H-MIXD:prog_ppl"],
        ctrl_prog_ppl=means["H-STAG-CTRL:prog_ppl"],
    )
    write_json(
        out / "formal.json",
        {
            "rows": rows,
            "means": means,
            "decision": decision,
            "wall_s": time.perf_counter() - t0,
            "mix_frac": MIX_FRAC,
            "steps": steps,
            "cpu_threads": threads,
            "licenses": ["PSF", "CC-BY-SA / MIT Apache-2.0"],
            "mode": (
                "MIXD formal: live STAG curriculum + curated prog mix_frac "
                "vs story-only; TinyStories teacher; fit≠eval story prompts"
            ),
        },
    )
    print(json.dumps({"decision": decision, "out": str(out / "formal.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
