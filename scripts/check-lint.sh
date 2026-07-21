#!/usr/bin/env bash
# Lint gate: 0 errors and 0 warnings. Fails closed when tooling exists.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

has_js_sources=false
if find . \
  \( -path './.git' -o -path './.local' -o -path './node_modules' \
     -o -path './dist' -o -path './coverage' -o -path './agent-rules' \
     -o -path './agent-harness' -o -path './scripts' -o -path './build' \) -prune -o \
  -type f \( -name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.jsx' \
             -o -name '*.mjs' -o -name '*.cjs' \) -print \
  | grep -q .; then
  has_js_sources=true
fi

has_cxx_sources=false
if find . \
  \( -path './.git' -o -path './.local' -o -path './node_modules' \
     -o -path './build' -o -path './agent-rules' -o -path './agent-harness' \
     -o -path './scripts' \) -prune -o \
  -type f \( -name '*.cpp' -o -name '*.cc' -o -name '*.cxx' -o -name '*.hpp' \
             -o -name '*.h' -o -name '*.hh' \) -print \
  | grep -q .; then
  has_cxx_sources=true
fi

ran_any=false

if [[ -f "package.json" ]] && $has_js_sources; then
  if node -e "const p=require('./package.json'); process.exit(p.scripts && p.scripts.lint ? 0 : 1)"; then
    ran_any=true
    echo "[lint] Running npm run lint (0 warnings)..."
    npm run lint
  else
    echo "[lint] FAIL: JS/TS sources exist but package.json has no lint script."
    exit 1
  fi
fi

if $has_cxx_sources; then
  ran_any=true
  echo "[lint] Checking C++ sources with size/complexity gate (harness caps)..."
  python3 "$ROOT/scripts/check_size_complexity.py" --root "$ROOT"
  if command -v clang-tidy >/dev/null 2>&1 && [[ -f "compile_commands.json" || -f "build/compile_commands.json" ]]; then
    echo "[lint] clang-tidy available — optional deeper pass skipped in v1 (size gate is mandatory)."
  fi
fi

if ! $ran_any; then
  echo "[lint] No language lint tooling applicable yet — OK (docs/harness only)."
fi

echo "[lint] OK — 0 errors, 0 warnings"
