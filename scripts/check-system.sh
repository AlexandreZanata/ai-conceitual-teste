#!/usr/bin/env bash
# System / compile gate: 0 errors when a build system exists.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -f "CMakeLists.txt" ]]; then
  echo "[system] Configuring and building CMake project..."
  cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
  cmake --build build --parallel
  if [[ -f "build/CTestTestfile.cmake" ]] || compgen -G "build/**/CTestTestfile.cmake" >/dev/null 2>&1; then
    echo "[system] Running ctest..."
    ctest --test-dir build --output-on-failure
  fi
  echo "[system] OK — 0 errors"
  exit 0
fi

if [[ -f "package.json" ]]; then
  if node -e "const p=require('./package.json'); process.exit(p.scripts && p.scripts.typecheck ? 0 : 1)"; then
    echo "[system] Running npm run typecheck..."
    npm run typecheck
    echo "[system] OK — 0 errors"
    exit 0
  fi
  if node -e "const p=require('./package.json'); process.exit(p.scripts && p.scripts.build ? 0 : 1)"; then
    echo "[system] Running npm run build..."
    npm run build
    echo "[system] OK — 0 errors"
    exit 0
  fi
fi

if [[ -f "tsconfig.json" ]]; then
  if command -v npx >/dev/null 2>&1; then
    echo "[system] Running tsc --noEmit..."
    npx tsc --noEmit
    echo "[system] OK — 0 errors"
    exit 0
  fi
fi

echo "[system] No compile toolchain yet — OK (scaffold pending)"
