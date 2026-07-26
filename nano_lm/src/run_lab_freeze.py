"""Lab freeze NO-REOPEN runner (nano:lab-freeze) — §8 #6."""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from lab_freeze_ops import (
    KILL_ARCHIVES,
    LAB_FREEZE_ID,
    WAVE_COMPLETE_DOCS,
    decide_lab_freeze,
    load_npm_script_names,
)
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/lab_freeze.json"


def _read_text(rel: str) -> str:
    path = REPO / rel
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _smoke_wrap() -> dict[str, object]:
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

    # Parallel filesystem reads (use CPU without thrashing GPU yet).
    archive_paths = list(KILL_ARCHIVES.values())
    with ThreadPoolExecutor(max_workers=min(12, len(archive_paths) + 4)) as pool:
        arch_flags = list(
            pool.map(lambda p: (p, (REPO / p).is_file()), archive_paths)
        )
        wave_bodies = list(
            pool.map(lambda p: (p, _read_text(p)), list(WAVE_COMPLETE_DOCS))
        )
    archive_exists = dict(arch_flags)
    wave_texts = dict(wave_bodies)
    package_json = _read_text("package.json")
    scripts = load_npm_script_names(package_json)
    recipes = _read_text("docs/results/nano-lm/RECIPES.md")
    decision = decide_lab_freeze(
        archive_exists=archive_exists,
        script_names=scripts,
        wave_texts=wave_texts,
        recipes_md=recipes,
    )
    ask: dict[str, object] | None = None
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
        "id": LAB_FREEZE_ID,
        "decision": decision,
        "cpu_threads": threads,
        "archives": {k: archive_exists[v] for k, v in KILL_ARCHIVES.items()},
        "n_scripts": len(scripts),
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/lab-freeze.md",
        "rule": "pesquisa §8 #6 NO-REOPEN",
    }
    write_json(Path(args.out), payload)
    ok = decision.startswith("PROMOTE")
    print(json.dumps({"ok": ok, "decision": decision[:64], "out": str(args.out)}))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
