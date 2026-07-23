# Formal H-LAM vs H-BAL (equal-budget follow-up)

Source: `results/nano-lm/formal-hlam-b2/formal.json`
Wall clock: 299.6s

Prompts: `nano_lm/prompts/eval_prompts.yaml` (8). Seeds: 0,1,2.
B2: KD 120 steps. H-BAL/H-LAM: pop=8, gens=12, lifetime_steps=2.
Teacher judge: TinyStories-33M. Primary gate: H-LAM vs H-BAL.

| family | mean teacher_lp | Δ vs H-BAL | Δ vs B2 | mean wall_ms | unstable | n |
|--------|-----------------|------------|---------|--------------|----------|---|
| B2 | -14.6480 | — | — | 124 | — | 3 |
| H-BAL | -16.2170 | — | -1.5689 | 116 | — | 3 |
| H-LAM | -16.3382 | -0.1213 | -1.6902 | 95 | no | 3 |

**Decision (vs H-BAL):** KILL / reverse smoke (H-LAM ≤ H-BAL)
**vs B2:** KILL / reverse smoke (H-LAM ≤ B2)

Smoke promote was tentative; this run is the claim-facing check.
