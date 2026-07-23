# Formal H-XOV vs B2 (equal-budget follow-up)

Source: `results/nano-lm/formal-hxov-b2/formal.json`
Wall clock: 183.5s

Prompts: `nano_lm/prompts/eval_prompts.yaml` (8). Seeds: 0,1,2.
B2: KD 120 steps. H-XOV: pop=8, gens=12, uniform crossover + mutate.
Teacher judge: TinyStories-33M.

| family | mean teacher_lp | Δ vs B2 | mean wall_ms | collapse | n |
|--------|-----------------|---------|--------------|----------|---|
| B2 | -14.6480 | — | 96 | — | 3 |
| H-XOV | -16.2999 | -1.6519 | 88 | no | 3 |

**Decision:** KILL / reverse smoke (H-XOV ≤ B2)

Smoke promote was tentative; this run is the claim-facing check.
