#!/usr/bin/env python3
"""CLI: enforce cyclomatic ≤10 (file/function line caps waived)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from quality.limits import MAX_CYCLOMATIC, MAX_FILE_LINES, MAX_FUNCTION_LINES
from quality.scan import analyze_file, iter_source_files


def _caps_msg() -> str:
    file_c = "waived" if MAX_FILE_LINES is None else f"≤{MAX_FILE_LINES}"
    fn_c = "waived" if MAX_FUNCTION_LINES is None else f"≤{MAX_FUNCTION_LINES}"
    return f"file {file_c}, function {fn_c}, cyclomatic≤{MAX_CYCLOMATIC}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.root.resolve()
    files = iter_source_files(root, args.paths or None)

    if not files:
        print("[size-complexity] No source files to check — OK")
        return 0

    findings = []
    for path in files:
        findings.extend(analyze_file(path))

    if findings:
        print("[size-complexity] FAILED — harness caps exceeded:")
        for item in findings:
            rel = (
                item.path.relative_to(root)
                if item.path.is_relative_to(root)
                else item.path
            )
            print(f"  - [{item.kind}] {rel}: {item.detail}")
        print(f"\nCaps: {_caps_msg()}")
        return 1

    print(f"[size-complexity] OK — {len(files)} file(s); caps: {_caps_msg()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
