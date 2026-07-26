"""Wave AA-FREEZE runner (nano:aa:freeze) — lock AA; no Wave AB invent."""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from aa_freeze_ops import (
    AA_DECISIONS,
    AA_FREEZE_ID,
    AA_PRODUCT_DOCS,
    AA_PUBLIC,
    AA_THESIS,
    decide_aa_freeze,
)
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-aa/aa_freeze.json"


def _read_text(rel: str) -> str:
    path = REPO / rel
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _smoke_wrap() -> dict[str, Any]:
    from run_z_ask import ask_once

    q = (
        "Write a short Python function named add that returns "
        "the sum of two integers a and b."
    )
    payload = ask_once(question=q, wrap=True, seed=0)
    text = str(payload.get("completion", "")).strip()
    mode = str(payload.get("mode", ""))
    return {
        "ok": mode == "WRAP_LOOKUP" and "def add" in text,
        "mode": mode,
        "wall_ms": payload.get("wall_ms"),
    }


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
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()
    threads = tune_cpu_threads(max(4, int(os.cpu_count() or 4) - 2))

    formal_paths = [p for _, (p, _) in AA_DECISIONS.items()]
    read_paths = list(
        dict.fromkeys([*formal_paths, *AA_PUBLIC, *AA_PRODUCT_DOCS])
    )
    with ThreadPoolExecutor(max_workers=min(14, len(read_paths))) as pool:
        pairs = list(pool.map(lambda p: (p, _read_text(p)), read_paths))
    texts = dict(pairs)
    formal_texts = {p: texts.get(p, "") for p in formal_paths}
    public_texts = {p: texts.get(p, "") for p in AA_PUBLIC}
    product_texts = {p: texts.get(p, "") for p in AA_PRODUCT_DOCS}
    decision = decide_aa_freeze(
        formal_texts=formal_texts,
        public_texts=public_texts,
        product_texts=product_texts,
    )
    ask: dict[str, Any] | None = None
    if not args.skip_ask:
        try:
            ask = _smoke_wrap()
        except (OSError, RuntimeError, ValueError) as exc:
            print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
            return 2
        if not bool(ask.get("ok")):
            print(json.dumps({"ok": False, "error": "wrap smoke failed", "ask": ask}))
            return 2
    payload = {
        "id": AA_FREEZE_ID,
        "thesis": AA_THESIS,
        "decision": decision,
        "cpu_threads": threads,
        "formals": {
            hid: {
                "path": path,
                "want": want,
                "ok": want in formal_texts.get(path, ""),
            }
            for hid, (path, want) in AA_DECISIONS.items()
        },
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/aa-freeze.md",
        "wave_aa_summary": "docs/results/nano-lm/wave-aa-summary.md",
        "rule": "pesquisa §8.2 AA-FREEZE",
    }
    write_json(Path(args.out), payload)
    ok = str(decision).startswith("PROMOTE")
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": AA_FREEZE_ID,
                "decision": decision[:96],
                "cpu_threads": threads,
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
