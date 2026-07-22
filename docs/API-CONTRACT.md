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
  "technique": "C",
  "environment": "survival_arena",
  "population_size": 20,
  "max_generations": 20,
  "max_wall_ms": 30000,
  "fitness_threshold": -0.4,
  "enable_drift": false,
  "seed": 42,
  "genome_size": 8,
  "grid_w": 16,
  "grid_h": 16,
  "food_density": 0.08,
  "energy_drain": 0.05,
  "hazard_rate": 0.02,
  "start_energy": 1.0,
  "episode_ticks": 32,
  "generation_delay_ms": 40
}
```

- `technique` (optional): `R0` | `A` | `B` | `C` | `C-L` | `A+` — applies flag matrix (see EXPERIMENTAL-DESIGN). Unknown ID → 400.
- `environment`: `function_approx` (T1) or `survival_arena` (T2 Trait Forge Arena).
- `condition` **A|B|C** still accepted; when `technique` is set it overrides enable_* / inheritance / elite.
- `max_wall_ms` (optional, default `0` = off): stop when elapsed wall time reaches this budget.
- `fitness_threshold` (optional τ): stop when generation `fitness_mean` ≥ τ; recorded in `meta.json`.
- `enable_drift` / `drift_at_fraction` (optional): mid-budget season/hazard flip (TB-DRIFT / TB-120).
- `generation_delay_ms` (optional, default `0`): sleep after each generation so UI/WS clients can observe pause/resume.
- Arena knobs validated when `environment` is `survival_arena`.

### `POST /experiments/{id}/pause` / `.../resume` / `.../stop`

Lifecycle control. Idempotent where possible (repeat pause/resume/stop on terminal states).

### `GET /experiments/{id}`

Snapshot: status, current generation, latest metrics, condition, seed.

### `GET /experiments/{id}/population` / `.../lineage`

Optional / phase 07+ dashboard — not required for phase 06 arena.

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
  "learning_rate_mean": 0.009,
  "alive_mean": 0.45,
  "technique": "C",
  "wall_ms_elapsed": 1280
}
```

`alive_mean` is the fraction of agents still alive at episode end (1.0 for non-interactive T1).  
`technique` is the learning-technique ID when set (phase 07).  
`wall_ms_elapsed` is milliseconds since run start (phase 08 budgets).

**Update budget (UC-003):** a `generation` event MUST arrive within **1s** after the generation completes (local process; typically immediate).

## Static files

`web/` is mounted at `/` (Chart.js via jsDelivr CDN — MIT; see [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md)).

## CLI

```bash
./build/evogen --serve [--port 8080] [--bind 127.0.0.1] [--web-root web] [--results DIR]
./build/evogen --technique C --generations 5
./build/evogen --config experiments/survival/benches/TB-30.json --technique C
python3 scripts/run_survival_bench.py --bench TB-30 --technique R0 --technique C --seeds 2
python3 scripts/aggregate_survival_bench.py
```

## Non-goals (v1)

Auth/multi-tenant API, GraphQL, external message bus, binding all interfaces by default.
