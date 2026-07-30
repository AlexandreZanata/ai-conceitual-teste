#!/usr/bin/env bash
# Lint: 0 errors, 0 warnings. Degrades gracefully until tooling is installed.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if ! compgen -G "n32/**/*.py" > /dev/null && ! compgen -G "bench/*.py" > /dev/null; then
  echo "[lint] OK - no sources yet"
  exit 0
fi

if command -v ruff > /dev/null 2>&1; then
  ruff check n32 bench scripts
  ruff format --check n32 bench scripts
  echo "[lint] OK - ruff clean"
else
  echo "[lint] SKIP - ruff not installed (pip install ruff)"
  python3 -m compileall -q n32 bench scripts > /dev/null
  echo "[lint] OK - syntax check passed (install ruff for the real gate)"
fi
