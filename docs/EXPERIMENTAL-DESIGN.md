# Experimental Design — EvoGen

> How we prove the concept. Plan source: [plano-conceitual-evogen.md](plano-conceitual-evogen.md) §6.

## Bench tasks

| ID | Task | Purpose |
|----|------|---------|
| T1 | Function approximation (XOR / sine) | Cheapest full-loop validation (phase 04) |
| T2 | **Trait Forge Arena** (survival grid) | Visible selection pressure; species must develop under rules/variables (phase 06+) |
| T3 | Arena season / hazard drift | Dynamic stress; recovery lag under timed benches |

**First implementation:** T1 done. **Next product focus:** T2 survival game + timed technique benchmarks (see `.local/SURVIVAL-GAME-PLAN.md`).

### T2 rules vs variables (sketch)

| Rules (fixed) | Variables (config) |
|---------------|--------------------|
| Bounds, collision, death at energy ≤ 0 | `grid_*`, `food_density`, `energy_drain`, `hazard_rate`, `start_energy`, `episode_ticks` |
| Food raises energy; drain per tick | Season length / flip point (T3 / TB-DRIFT) |

### Techniques (phase 07+)

| ID | Genetic | Direct | Notes |
|----|---------|--------|-------|
| R0 | No | No | Random floor |
| A | Yes | No | Genetic only |
| B | No | Yes | Direct only |
| C | Yes | Yes | Full system (Darwinian) |
| C-L | Yes | Yes | Lamarckian inheritance |
| A+ | Yes | No | Stronger elitism |

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
