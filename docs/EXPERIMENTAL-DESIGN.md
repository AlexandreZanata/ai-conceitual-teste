# Experimental Design — EvoGen

> How we prove the concept. Plan source: [plano-conceitual-evogen.md](plano-conceitual-evogen.md) §6.

## Bench tasks

| ID | Task | Purpose |
|----|------|---------|
| T1 | Function approximation (XOR / sine) | Cheapest full-loop validation |
| T2 | 2D grid navigation to a target | Selection + online adaptation inside episode |
| T3 | Incremental classifier with concept drift | Dynamic environment stress test |

**First implementation:** T1 only (phases 03–04).

## Conditions

| Condition | Genetic evolution | Direct learning | Role |
|-----------|-------------------|-----------------|------|
| **A** | Yes | No (genome fixed in lifetime) | Control |
| **B** | No (no reproduction between gens) | Yes | Control |
| **C** | Yes | Yes | Full system |

Configs (to be added under `experiments/`):

- `config_A_only_genetic.json`
- `config_B_only_direct.json`
- `config_C_full_system.json`

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
