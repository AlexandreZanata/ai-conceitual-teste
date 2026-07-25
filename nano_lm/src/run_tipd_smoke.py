"""Smoke H-TIPD: binary tip decision RETIP→STAG′ xor util."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from data_tiny import load_tokenizer
from load_model import resolve_device
from matrix_common import REPO, matrix_cfg, write_json
from stag_ops import STAG_SEQ_LO
from tipd_pair import load_texts, run_tipd_seeds, tune_cpu_threads
from top_ops import DEFAULT_TOP_K
from top_pair import TIP_STAGES


def main() -> int:
    threads = tune_cpu_threads()
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("ERROR: H-TIPD requires CUDA", file=sys.stderr)
        return 2
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    gene_dir = Path(c.get("gene_dir", out))
    early_dir = Path(c.get("early_dir", gene_dir))
    pool_dir = Path(c.get("pool_dir", gene_dir))
    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    steps = int(c.get("steps_cur", c["steps_kd"]))
    prompts = load_texts(c["prompts"])
    max_new = int(c.get("max_new_fit", 16))
    t0 = time.perf_counter()
    payload = run_tipd_seeds(
        c,
        out=out,
        device=device,
        vocab=len(tok),
        steps=steps,
        prompts=prompts,
        max_new=max_new,
        early_dir=early_dir,
        pool_dir=pool_dir,
        label_prefix="HTIPD",
        claim_base=7100,
        pool_eval_fallback=True,
    )
    payload.update(
        {
            "wall_s": time.perf_counter() - t0,
            "seq_lo": STAG_SEQ_LO,
            "n_stages": TIP_STAGES,
            "steps": steps,
            "top_k": DEFAULT_TOP_K,
            "max_new": max_new,
            "n_prompts": len(prompts),
            "cpu_threads": threads,
            "mode": "TIPD: RETIP→STAG′ xor util (capacity + no serve regress)",
            "repo": str(REPO),
        }
    )
    write_json(out / "tipd_smoke.json", payload)
    print(
        json.dumps(
            {
                "decision": payload["decision"],
                "tip_outcome": payload["tip_outcome"],
                "out": str(out / "tipd_smoke.json"),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
