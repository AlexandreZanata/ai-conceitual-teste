#!/usr/bin/env bash
# Full quality gate. Used by Lefthook (pre-commit, pre-push) and `npm run verify`.
# Caps: cyclomatic <=10 per function, lint 0/0, hygiene clean, tests pass.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

SCOPE="${1:---all}"

echo "=== N32 quality gate ==="

echo ""
echo "1/4 Repository hygiene (no binaries, no secrets, no bloat)"
python3 scripts/check_repo_hygiene.py "$SCOPE"

echo ""
echo "2/4 Complexity (cyclomatic <= 10 per function)"
python3 scripts/check_size_complexity.py --root "$ROOT"

echo ""
echo "3/4 Lint (0 errors, 0 warnings)"
bash scripts/check-lint.sh

echo ""
echo "4/4 Tests"
bash scripts/check-tests.sh

echo ""
echo "=== All quality gates passed ==="
