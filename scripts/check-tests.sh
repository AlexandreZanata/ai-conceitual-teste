#!/usr/bin/env bash
# Contract tests. Never weaken an assertion to make this pass.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if ! find n32 bench -name 'test_*.py' -print -quit 2>/dev/null | grep -q .; then
  echo "[tests] FAILED - no contract tests found under n32/ or bench/"
  exit 1
fi

if command -v pytest > /dev/null 2>&1 || python3 -c "import pytest" 2>/dev/null; then
  python3 -m pytest n32 bench -q
  echo "[tests] OK"
else
  echo "[tests] FAILED - tests exist but pytest is not installed"
  exit 1
fi
