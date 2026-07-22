# Experimental Design — EvoGen

> How we prove the concept. Plan source: [plano-conceitual-evogen.md](plano-conceitual-evogen.md) §6.

## Bench tasks

| ID | Task | Purpose |
|----|------|---------|
| T1 | Function approximation (XOR / sine) | Cheapest full-loop validation (phase 04) |
| T2 | **Trait Forge Arena** (survival grid) | Visible selection pressure; species must develop under rules/variables (phase 06+) |
| T3 | Arena season / hazard drift | Dynamic stress; recovery lag under timed benches |

**First implementation:** T1 done. **T2 SurvivalArenaEnv** implemented (phase 06). Timed technique benches remain phase 08.

### T2 rules vs variables

| Rules (fixed) | Variables (config) |
|---------------|--------------------|
| Bounds (wall = no move); death at energy ≤ 0 | `grid_w`, `grid_h` (default **16×16**) |
| Per-tick `energy_drain`; food +0.35; hazard −0.4 | `food_density`, `energy_drain`, `hazard_rate`, `start_energy`, `episode_ticks` |
| Discrete **5-way** actions from scalar response bins (N/E/S/W/stay) | Season stub in stimulus (flip in T3 / TB-DRIFT) |

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

| Bench | Budget (example) | Goal |
|-------|------------------|------|
| TB-30 | 30 s or 40 gens | Mild τ |
| TB-60 | 60 s or 80 gens | Medium τ |
| TB-120 | 120 s or 150 gens | Harsh τ |
| TB-DRIFT | 90 s or 100 gens | Recovery after mid-run flip |

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
2. Repeat each condition ≥ R times (R chosen in phase 08; default proposal R=10).  
3. Same population size, episode length, and weight dimension across A/B/C for a given task.  
4. Store raw JSON/CSV under `results/` (gitignored); summarize in docs for phase 09.

## Hypotheses (short)

- **H1:** Condition C reaches target fitness in fewer generations than A on T1.  
- **H2:** Condition C adapts faster than A under T3 drift.  
- **H3:** Under Darwinian mode on a static T1, mean `learning_rate` decreases as genomes improve (Baldwin-compatible pattern).
