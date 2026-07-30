#!/usr/bin/env python3
"""Enforce cyclomatic complexity <= 10 per function (line caps waived)."""

from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass
from pathlib import Path

MAX_CYCLOMATIC = 10

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    "data",
    "runs",
    "artifacts",
    "results",
    ".local",
    "build",
    "dist",
}

# Nodes that each add one independent path through a function.
_BRANCH_NODES = (
    ast.If,
    ast.For,
    ast.AsyncFor,
    ast.While,
    ast.ExceptHandler,
    ast.With,
    ast.AsyncWith,
    ast.Assert,
    ast.IfExp,
    ast.Match,
)


@dataclass(frozen=True)
class Finding:
    path: Path
    function: str
    line: int
    complexity: int


def cyclomatic(node: ast.AST) -> int:
    """McCabe complexity: 1 + decision points, not counting nested functions."""
    score = 1
    for child in ast.walk(node):
        if child is node:
            continue
        if isinstance(child, _BRANCH_NODES):
            score += 1
        elif isinstance(child, ast.BoolOp):
            score += len(child.values) - 1
        elif isinstance(child, ast.comprehension):
            score += 1 + len(child.ifs)
        elif isinstance(child, ast.match_case):
            score += 1
    return score


def analyze(path: Path) -> list[Finding]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        print(f"[size-complexity] SYNTAX ERROR {path}:{exc.lineno}: {exc.msg}")
        raise SystemExit(1) from exc

    findings = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        score = cyclomatic(node)
        if score > MAX_CYCLOMATIC:
            findings.append(Finding(path, node.name, node.lineno, score))
    return findings


def iter_sources(root: Path) -> list[Path]:
    return [
        p
        for p in root.rglob("*.py")
        if not any(part in SKIP_DIRS for part in p.relative_to(root).parts)
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.root.resolve()

    files = iter_sources(root)
    if not files:
        print("[size-complexity] OK - no Python sources yet")
        return 0

    findings = [f for path in files for f in analyze(path)]
    if findings:
        print(f"[size-complexity] FAILED - cyclomatic > {MAX_CYCLOMATIC}:")
        for f in findings:
            rel = f.path.relative_to(root)
            print(f"  - {rel}:{f.line} {f.function}() complexity={f.complexity}")
        print("\nExtract helper functions. Do not nest deeper to game the metric.")
        return 1

    print(
        f"[size-complexity] OK - {len(files)} file(s), cyclomatic <= {MAX_CYCLOMATIC}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
