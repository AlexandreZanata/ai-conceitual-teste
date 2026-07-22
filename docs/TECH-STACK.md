# Tech Stack — EvoGen

## Core

| Piece | Choice | Why |
|-------|--------|-----|
| Language | C++17 (prefer C++20 where available) | Performance, single binary, auditability |
| Build | CMake | One file, reproducible research builds |
| JSON | **nlohmann/json v3.11** (FetchContent) | Config load + metrics JSONL |
| HTTP | **cpp-httplib v0.50.1** (FetchContent) | Embedded REST + static files |
| WebSocket | **cpp-httplib** built-in WS (`/ws/metrics`) | Live metrics stream (same pin) |
| Frontend | Static `web/` HTML/JS + Chart.js **4.4.1** CDN | No SPA build; MIT Chart.js |
| Tests | **Catch2 v3** (FetchContent) | Contract-first unit tests on Domain |
| Quality | Lefthook + size/complexity scanner (+ clang-tidy when compile_commands present) | Harness caps |

## Explicitly out of scope

PyTorch, TensorFlow, microservices, mandatory external databases.

## Optional persistence

JSON files under `results/` (gitignored). SQLite only if phase 08 needs queryable runs.

## Toolchain assumptions

- CMake ≥ 3.16  
- Compiler: GCC or Clang with C++17  
- Network on first configure (FetchContent for Catch2 + nlohmann/json + cpp-httplib)  
- Node only for Lefthook / repo hooks (not for the EvoGen binary)

## Build / test / run (phase 03+)

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
ctest --test-dir build --output-on-failure
./build/evogen --config experiments/config_A_only_genetic.json --generations 1
./build/evogen --serve --port 8080
```

Or via npm scripts: `npm run build`, `npm run test`, `npm run verify`.
