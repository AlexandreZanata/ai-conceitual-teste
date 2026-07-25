"""Render formal H-BTC bitcoin domain capacity report."""

from __future__ import annotations

import argparse
from pathlib import Path

from write_hbtc_report import render


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--formal",
        type=Path,
        default=Path("results/nano-lm/formal-hbtc/formal.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/formal-hbtc-bitcoin.md"),
    )
    args = p.parse_args()
    text = render(args.formal, formal=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
