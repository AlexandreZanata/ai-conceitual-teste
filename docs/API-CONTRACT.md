# API Contract — EvoGen (sketch)

> Embedded C++ server. JSON over REST + WebSocket. Refine before phase 05 implementation.
> Terms: [GLOSSARY.md](GLOSSARY.md).

## Base

- Process binds localhost (default port TBD in phase 05, e.g. `8080`).
- Content-Type: `application/json`.
- Errors: `{ "error": { "code": "string", "message": "string" } }`.

## REST

### `GET /health`

Returns `{ "status": "ok", "version": "semver" }`.

### `POST /experiments`

Start or configure a run.

```json
{
  "condition": "C",
  "environment": "function_approx",
  "population_size": 50,
  "max_generations": 100,
  "seed": 42,
  "inheritance_mode": "Darwinian",
  "initial_mutation_rate": 0.05,
  "initial_learning_rate": 0.01
}
```

Response: `{ "experiment_id": "uuid", "status": "running" }`.

### `POST /experiments/{id}/pause` / `.../resume` / `.../stop`

Lifecycle control. Idempotent where possible.

### `GET /experiments/{id}`

Snapshot: status, current generation, latest metrics, config.

### `GET /experiments/{id}/population`

Optional snapshot of genomes/fitness (may be truncated for large pops).

### `GET /experiments/{id}/lineage`

Parent links for lineage visualization (phase 06).

## WebSocket `GET /ws/metrics`

Server pushes per-generation events:

```json
{
  "type": "generation",
  "experiment_id": "uuid",
  "generation": 12,
  "fitness_mean": 0.41,
  "fitness_max": 0.88,
  "diversity_mean": 0.17,
  "learning_rate_mean": 0.009
}
```

## Non-goals (v1)

Auth/multi-tenant API, GraphQL, external message bus.
