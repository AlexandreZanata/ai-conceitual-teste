# H-ABS-DEBATE smoke — dual early-exit halves then BoN commit (**KILL**)

> Smoke **KILL**. Do not claim dual-half debate dual-gate win from wall↓ with identical text. Tooling purged.

Wave X absurd sandbox: two shared-weight EARLY halves (A=parent gene; B=conf×0.9 / patience+1) debate, commit by student self mean_lp. Still ≤5M params. Parent = bare H-EARLY on prog@128. Wall = A+B cost.

Frozen: ε=0.05; conf_scale_b=0.90; patience_delta_b=1; max_new=32; seeds=3; identity gate.

**Decision: KILL (identity vs parent; debate had no effect)**

## Arms

| arm | mean story_lp | mean code_lp | mean wall_ms | mean tok/s | mean disagree | n |
|-----|---------------|--------------|--------------|------------|---------------|---|
| H-EARLY bare | -14.8854 | -16.2692 | 22 | 662.1 | 0.000 | 12 |
| H-ABS-DEBATE | -14.8854 | -16.2692 | 20 | 334.8 | 0.000 | 12 |

## Lesson

Dual early-exit schedules **never disagreed** (disagree=0; winner always A) and matched parent story/code LPs exactly — identity under greedy EARLY. Softening conf/patience is not a free multi-agent upgrade when both halves collapse to the same continuation. Next E.1: **H-ABS-HOLO** (holographic KV checksum) — not another BoN/INTERF/DNA compress.

Commands (purged): were `npm run nano:debate` / `nano:formal:hdebate*`.
