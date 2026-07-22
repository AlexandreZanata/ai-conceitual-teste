#!/usr/bin/env python3
"""Validate phase 09 report structure and cited run paths (when present)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "results" / "BENCHMARK-REPORT.md"
SUMMARY = ROOT / "docs" / "results" / "survival-benchmark-summary.md"
CURVES = ROOT / "docs" / "results" / "curves"
RESULTS = ROOT / "results" / "survival"

REQUIRED_HEADINGS = [
    "## 1. Intro",
    "## 3. Methods",
    "## 4. Techniques",
    "## 5. Timed protocol",
    "## 6. Results",
    "## 7. Research questions",
    "## 8. Narrative",
    "## 9. Discussion",
    "## 10. Limits",
]

REQUIRED_CURVES = [
    "TB-30_fitness_vs_generation.svg",
    "TB-60_fitness_vs_generation.svg",
    "TB-30_R0_seed1.csv",
    "TB-60_C_seed1.csv",
]

PATH_RE = re.compile(
    r"results/survival/"
    r"(TB-[A-Z0-9-]+/[A-Za-z0-9+-]+/seed_\d+(?:/[A-Za-z0-9_.]+)?/?)"
)


def check_headings(text: str) -> list[str]:
    return [f"missing heading: {h}" for h in REQUIRED_HEADINGS if h not in text]


def check_rq_and_tb60(text: str) -> list[str]:
    errors = [f"missing RQ mapping mention: {rq}" for rq in ("RQ1", "RQ2", "RQ3", "RQ4")
              if rq not in text]
    if "TB-60" not in text or "beats" not in text.lower():
        errors.append("TB-60 comparative answer missing")
    return errors


def check_artifacts() -> list[str]:
    errors = []
    if not SUMMARY.is_file():
        errors.append("missing survival-benchmark-summary.md")
    for name in REQUIRED_CURVES:
        if not (CURVES / name).is_file():
            errors.append(f"missing curve artifact: {name}")
    return errors


def check_citations(text: str) -> list[str]:
    cited = sorted(set(PATH_RE.findall(text)))
    errors = []
    if len(cited) < 5:
        errors.append(f"expected ≥5 run-path citations, found {len(cited)}")
    if not RESULTS.is_dir():
        print("warn: results/survival absent — skipped live path checks")
        return errors
    for rel in cited:
        if not (RESULTS / rel.rstrip("/")).exists():
            errors.append(f"cited path missing on disk: results/survival/{rel}")
    return errors


def main() -> int:
    if not REPORT.is_file():
        print("error: missing BENCHMARK-REPORT.md", file=sys.stderr)
        return 1
    text = REPORT.read_text()
    errors = (
        check_headings(text)
        + check_rq_and_tb60(text)
        + check_artifacts()
        + check_citations(text)
    )
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        return 1
    cited_n = len(set(PATH_RE.findall(text)))
    print(f"ok: report validated ({cited_n} citations checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
