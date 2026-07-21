# Tech Stack — EvoGen

## Core

| Piece | Choice | Why |
|-------|--------|-----|
| Language | C++17 (prefer C++20 where available) | Performance, single binary, auditability |
| Build | CMake | One file, reproducible research builds |
| JSON | **nlohmann/json v3.11** (FetchContent) | Config load + metrics JSONL |
| HTTP | `cpp-httplib` (or Crow if needed) | Embedded REST, no heavy framework |
| WebSocket | Lightweight (`websocketpp` / `uWebSockets` — pick one in phase 05) | Live metrics stream |
| Frontend | Static HTML/JS + Chart.js or D3 | No heavy SPA build required |
| Tests | **Catch2 v3** (FetchContent) | Contract-first unit tests on Domain |
| Quality | Lefthook + size/complexity scanner (+ clang-tidy when compile_commands present) | Harness caps |

## Explicitly out of scope

PyTorch, TensorFlow, microservices, mandatory external databases.

## Optional persistence

JSON files under `results/` (gitignored). SQLite only if phase 08 needs queryable runs.

## Toolchain assumptions

- CMake ≥ 3.16  
- Compiler: GCC or Clang with C++17  
- Network on first configure (FetchContent for Catch2 + nlohmann/json)  
- Node only for Lefthook / repo hooks (not for the EvoGen binary)

## Build / test / run (phase 03+)

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
ctest --test-dir build --output-on-failure
./build/evogen --config experiments/config_A_only_genetic.json --generations 1
```

Or via npm scripts: `npm run build`, `npm run test`, `npm run verify`.
