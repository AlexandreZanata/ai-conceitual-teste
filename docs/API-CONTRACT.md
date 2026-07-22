# API Contract — EvoGen

> Embedded C++ server (cpp-httplib v0.50.1). JSON over REST + WebSocket.
> Terms: [GLOSSARY.md](GLOSSARY.md).

## Base

- Process binds **`127.0.0.1`** by default (override with `--bind`).
- Default port **`8080`** (`--port`).
- Content-Type: `application/json`.
- Errors: `{ "error": { "code": "string", "message": "string" } }`.
- PoC paths are unversioned (single binary); not a public multi-tenant API.

## REST

### `GET /health`

Returns `{ "status": "ok", "version": "semver" }`.

### `POST /experiments`

Start a run. Response **201**: `{ "experiment_id": "hex-id", "status": "running" }`.
Conflict if another experiment is active → **409**.

```json
{
  "condition": "C",
  "environment": "function_approx",
  "function_task": "xor",
  "episode_length": 4,
  "population_size": 50,
  "max_generations": 100,
  "seed": 42,
  "inheritance_mode": "Darwinian",
  "initial_mutation_rate": 0.05,
  "initial_learning_rate": 0.01,
  "generation_delay_ms": 40
}
```

- `condition` **A|B|C** applies enable-flag defaults (overridable by explicit `enable_*` fields).
- `generation_delay_ms` (optional, default `0`): sleep after each generation so UI/WS clients can observe pause/resume.

### `POST /experiments/{id}/pause` / `.../resume` / `.../stop`

Lifecycle control. Idempotent where possible (repeat pause/resume/stop on terminal states).

### `GET /experiments/{id}`

Snapshot: status, current generation, latest metrics, condition, seed.

### `GET /experiments/{id}/population` / `.../lineage`

Optional / phase 06 — not required for phase 05.

## WebSocket `GET /ws/metrics`

Server pushes per-generation events (text JSON):

```json
{
  "type": "generation",
  "experiment_id": "hex-id",
  "generation": 12,
  "fitness_mean": 0.41,
  "fitness_max": 0.88,
  "diversity_mean": 0.17,
  "learning_rate_mean": 0.009
}
```

**Update budget (UC-003):** a `generation` event MUST arrive within **1s** after the generation completes (local process; typically immediate).

## Static files

`web/` is mounted at `/` (Chart.js via jsDelivr CDN — MIT; see [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md)).

## CLI

```bash
./build/evogen --serve [--port 8080] [--bind 127.0.0.1] [--web-root web] [--results DIR]
```

## Non-goals (v1)

Auth/multi-tenant API, GraphQL, external message bus, binding all interfaces by default.
