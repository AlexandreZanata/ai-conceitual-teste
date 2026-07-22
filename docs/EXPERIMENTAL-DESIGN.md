# Experimental Design — EvoGen

> How we prove the concept. Plan source: [plano-conceitual-evogen.md](plano-conceitual-evogen.md) §6.

## Bench tasks

| ID | Task | Purpose |
|----|------|---------|
| T1 | Function approximation (XOR / sine) | Cheapest full-loop validation (phase 04) |
| T2 | **Trait Forge Arena** (survival grid) | Visible selection pressure; species must develop under rules/variables (phase 06+) |
| T3 | Arena season / hazard drift | Dynamic stress; recovery lag under timed benches |

**First implementation:** T1 done. **T2 SurvivalArenaEnv** implemented (phase 06). **Timed technique benches** implemented (phase 08).

### T2 rules vs variables

| Rules (fixed) | Variables (config) |
|---------------|--------------------|
| Bounds (wall = no move); death at energy ≤ 0 | `grid_w`, `grid_h` (default **16×16**) |
| Per-tick `energy_drain`; food +0.35; hazard −0.4 | `food_density`, `energy_drain`, `hazard_rate`, `start_energy`, `episode_ticks` |
| Discrete **5-way** actions from scalar response bins (N/E/S/W/stay) | Season in stimulus (`set_season`); flip in T3 / TB-DRIFT / TB-120 |

Reward: Δenergy this tick + 0.01 alive bonus while alive.  
Factory: `environment: "survival_arena"`. Smoke config: `experiments/config_survival_C_smoke.json`.  
Metric: `alive_mean` = fraction of agents still alive at episode end.

### Techniques (phase 07)

| ID | Genetic | Direct | Inheritance | Elite | Condition field |
|----|---------|--------|-------------|-------|-----------------|
| R0 | No | No | Darwinian | 1 | A |
| A | Yes | No | Darwinian | 1 | A |
| B | No | Yes | Darwinian | 1 | B |
| C | Yes | Yes | Darwinian | 1 | C |
| C-L | Yes | Yes | Lamarckian | 1 | C |
| A+ | Yes | No | Darwinian | **5** | A |

Runtime: JSON/`--technique` → `apply_technique_defaults` (overrides enable_* / inheritance / elite / rates).  
Configs: `experiments/survival/{R0,A,B,C,C-L,A+}.json` (shared arena knobs).  
A+ strong elitism trades diversity for exploitation (fewer unique lineages).

### Timed budgets (phase 08)

| Bench | Wall / gens | Arena | τ | Drift |
|-------|-------------|-------|---|-------|
| TB-30 | 30 s / 40 gens | mild (`food=0.12`, `hazard=0.01`) | **τ_mild = −0.40** | no |
| TB-60 | 60 s / 80 gens | medium | **τ_med = −0.60** | no |
| TB-120 | 120 s / 150 gens | harsh | **τ_harsh = −0.68** | yes @ 50% |
| TB-DRIFT | 90 s / 100 gens | mid scarcity → harsher | −0.55 | yes @ 50% |

**τ calibration (seed 42, pop 20, technique C, 40 gens smoke):** mild best mean ≈ −0.095; med ≈ −0.629; harsh ≈ −0.711. Thresholds set below those peaks so techniques can hit τ without requiring the absolute smoke maximum.

Stop when **first** of: `fitness_mean ≥ τ`, `wall_ms ≥ max_wall_ms`, or `generation ≥ max_generations`. Record `stop_reason` in `meta.json`. Per-gen log includes `wall_ms_elapsed`.

Configs: `experiments/survival/benches/{TB-30,TB-60,TB-120,TB-DRIFT}.json`.  
Runner: `python3 scripts/run_survival_bench.py` → `results/survival/<bench>/<technique>/seed_<n>/{meta.json,metrics.jsonl}`.  
Aggregate: `python3 scripts/aggregate_survival_bench.py` → `docs/results/survival-benchmark-summary.md` (+ optional CSV).

Progress metrics: time-to-threshold, fitness@budget, learning-curve AUC, survival rate, recovery lag.

## Conditions

| Condition | Genetic evolution | Direct learning | Role |
|-----------|-------------------|-----------------|------|
| **A** | Yes | No (genome fixed in lifetime) | Control |
| **B** | No (no reproduction between gens) | Yes | Control |
| **C** | Yes | Yes | Full system |

Configs under `experiments/`:

- `config_A_only_genetic.json` — genetic only (`enable_direct_learning: false`)
- `config_B_only_direct.json` — direct only (`enable_genetic_reproduction: false`)
- `config_C_full_system.json` — full system
- `config_survival_C_smoke.json` — Trait Forge Arena (T2) condition C smoke
- `experiments/survival/{R0,A,B,C,C-L,A+}.json` — technique matrix presets

T1 knobs: `function_task` (`xor`|`sine`), `episode_length`, `inheritance_mode` (`Darwinian`|`Lamarckian`).

Reward: `-(response - target)^2`.

## Success metrics

| Metric | Definition |
|--------|------------|
| Convergence speed | Generations until target fitness |
| Max fitness @ N | Best fitness within N generations |
| Genetic diversity | Mean pairwise genome distance per generation |
| Baldwin signal | Evolved mean `learning_rate` trend vs genome performance |

## Protocol (minimum)

1. Fixed seed logged in every run.  
2. Repeat each condition ≥ R times. **Default proposal:** R=10 full report / **R=2 CI smoke** (`scripts/run_survival_bench.py --seeds`).  
3. Same population size, episode length, and weight dimension across techniques for a given bench.  
4. Store raw JSON under `results/survival/` (gitignored); summarize in `docs/results/` for phase 08–09.

## Hypotheses (short)

Arena-restated (T2/T3). Claims are **comparative under equal budget**, not absolute proof of Baldwin or optimality.

- **H1:** On static TB-30/TB-60, technique **C** reaches τ in fewer generations / less wall time than **A** (genetic-only) more often than chance across seeds.  
- **H2:** Under TB-DRIFT / TB-120 mid-run flip, **C** shows shorter recovery lag than **A** (and usually than **R0**).  
- **H3:** On a static mild arena under Darwinian **C**, mean `learning_rate` tends to fall as genomes improve (Baldwin-compatible *pattern* only — not a causal claim).

T1 XOR/sine remains the regression suite; do not overclaim from smoke R=2 alone.
