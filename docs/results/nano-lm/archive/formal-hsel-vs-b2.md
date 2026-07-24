# Formal H-SEL vs B2 (equal-budget follow-up)

Source: `results/nano-lm/formal-hsel-b2/formal.json`
Wall clock: 137.0s

Prompts: `nano_lm/prompts/eval_prompts.yaml` (8). Seeds: 0,1,2.
B2: KD 120 steps. H-SEL: pop=8, gens=12. Teacher judge: TinyStories-33M.

| family | mean teacher_lp | Δ vs B2 | mean wall_ms | n |
|--------|-----------------|---------|--------------|---|
| B2 | -14.6480 | — | 115 | 3 |
| H-SEL | -16.2426 | -1.5946 | 75 | 3 |

**Decision:** KILL / reverse smoke (H-SEL ≤ B2)

Smoke promote was tentative; this run is the claim-facing check.
