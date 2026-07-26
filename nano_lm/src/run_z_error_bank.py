"""Summarize Wave Z error_bank.jsonl counts (nano:z:error-bank)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from matrix_common import REPO

_DEFAULT = REPO / "results/nano-lm/wave-z/error_bank.jsonl"


def summarize(path: Path) -> dict[str, object]:
    if not path.is_file():
        return {"ok": True, "n": 0, "n_error": 0, "path": str(path), "exists": False}
    n = 0
    n_err = 0
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            n += 1
            row = json.loads(line)
            if bool(row.get("error")) or float(row.get("score", 10)) < 8.0:
                n_err += 1
    return {
        "ok": True,
        "n": n,
        "n_error": n_err,
        "path": str(path),
        "exists": True,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", type=Path, default=_DEFAULT)
    args = ap.parse_args()
    print(json.dumps(summarize(args.path)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
