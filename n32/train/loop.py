"""Single training entry point for N32.

Law R6: one pipeline, one train command. Later stages (P05, P15) flesh this out.
Until then the module exists so the entry-point contract is enforceable today.
"""

from __future__ import annotations

import argparse
import sys


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="N32 training loop (built in P05)")
    parser.add_argument("--steps", type=int, default=None)
    parser.add_argument("--resume", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    parse_args(argv)
    print(
        "n32.train.loop: training harness lands in P05. "
        "This stub exists so P01 can enforce a single entry point.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
