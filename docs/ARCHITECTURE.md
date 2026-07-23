# EvoGen — Architecture

> Normative for agents. Product intent (PT): [plano-conceitual-evogen.md](plano-conceitual-evogen.md).

## Product

**EvoGen** is a lightweight research PoC that combines:

1. Genetic / population learning  
2. Direct response learning (intra-lifetime / online)  
3. Natural selection via an `Environment` fitness pressure  

Core language: **C++17/20**. One process: evolutionary engine + embedded HTTP/WebSocket server. Web UI is an observation tool, not a commercial product.

## Layers

| Layer | Responsibility | Location |
|-------|----------------|----------|
| **Interfaces** | REST/WebSocket JSON, static `web/` assets | `src/server/`, `web/` |
| **Application** | Experiment control (start/pause/config), recording, A/B/C modes | `src/server/` (`ExperimentController`, `MetricsHub`) |
| **Domain** | `Genome`, `Agent`, `Population`, selection, mutation, `DirectLearner`, `Environment` contracts | `src/core/`, `src/environments/` |
| **Infrastructure** | RNG, JSON I/O, optional SQLite/JSON persistence, threading | thin adapters next to core |

Dependency rule: Domain has **zero** knowledge of HTTP, HTML, or chart libraries. Server calls Domain directly in-process.

## Aggregates and entities

| Term | Kind | Root / notes |
|------|------|--------------|
| `Genome` | Value Object | `weights`, evolvable `mutation_rate`, `learning_rate` |
| `Agent` | Entity | owns a `Genome` + lifetime state (`fitness`, short history) |
| `Population` | Aggregate | collection of `Agent` + genetic operators |
| `Environment` | Port (interface) | supplies stimuli + `evaluate(response, stimulus)` |
| `Generation` | Value / record | generation index + metrics snapshot |
| `Experiment` | Application aggregate | config, seed, condition A/B/C, run state |

## Ports

```text
Environment          ← Domain depends on this port
Recorder             ← Application writes GenerationMetrics
ExperimentController ← Application starts/pauses loop
```

## Main loop (domain)

```text
for each generation:
  for each agent:
    begin_lifetime() unless condition B continuing online
    if env.interactive():          # T2 SurvivalArenaEnv
      reset_episode(seed)
      while not done:
        stimulus = observe()
        response = agent.respond(stimulus)
        reward   = step(response)   # move/eat/hazard; may end episode
        if direct learning: phenotype += lr * (target - response) * stimulus
        agent.fitness += reward
    else:                          # T1 function approx
      for each stimulus in environment.episode():
        response = agent.respond(stimulus)
        target   = environment.target_of(stimulus)
        reward   = environment.evaluate(response, stimulus)
        if direct learning:
          phenotype += lr * (target - response) * stimulus
        agent.fitness += reward
  recorder.log_generation(... includes alive_mean, wall_ms_elapsed)
  if budgets hit (τ / max_wall_ms / max_generations): stop; write meta.json
  if drift due: flip season/hazard on Environment
  if genetic reproduction enabled:
    parents from genotype (Darwinian) or phenotype→genotype (Lamarckian)
    population = crossover_and_mutate(parents)
```

## Size and complexity (mandatory)

Every `.cpp` / `.hpp` must obey harness caps: **≤80 lines/function**, **≤200 lines/file**, **cyclomatic ≤10**. Prefer more files over larger files. Quality scanner must include C++ suffixes before the first C++ commit lands.

## Non-goals (C++ EvoGen product)

- Generic ML framework  
- Heavy ML libraries (PyTorch, TensorFlow, etc.) inside the evolutionary binary  
- Microservices or mandatory external DB  

## Side track — nano-LM (phase 10)

[`nano_lm/`](../nano_lm/) is an **isolated** Python/PyTorch experiment: frozen TinyStories-1M + decode-method comparison (AR / Best-of-N / Lookahead MAE). It is **not** part of Domain aggregates (`Genome`, `Population`, …). Protocol: [NANO-LM-TRACK.md](NANO-LM-TRACK.md). 
