#!/usr/bin/env bash
# Full quality gate used by Lefthook pre-commit and `npm run verify`.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "=== ai-conceitual-teste quality gate ==="

echo ""
echo "1/4 Size + complexity (file≤200, function≤80, cyclomatic≤10)"
python3 "$ROOT/scripts/check_size_complexity.py" --root "$ROOT" "$@"

echo ""
echo "2/4 Lint (0 errors, 0 warnings)"
bash "$ROOT/scripts/check-lint.sh"

echo ""
echo "3/3 System / compile (0 errors)"
bash "$ROOT/scripts/check-system.sh"

echo ""
echo "4/4 Benchmark report contract (phase 09)"
python3 "$ROOT/scripts/validate_benchmark_report.py"

echo ""
echo "=== All quality gates passed ==="
