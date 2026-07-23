# Formal H-SYM vs B2 (equal-budget follow-up)

Source: `results/nano-lm/formal-hsym-b2/formal.json`
Wall clock: 181.7s

Prompts: `nano_lm/prompts/eval_prompts.yaml` (8). Seeds: 0,1,2.
B2: KD 120 steps. H-SYM: pop=8, gens=12, obligate pair + mutate.
Teacher judge: TinyStories-33M. Fitness: probe CE (no teacher_lp leak).

| family | mean teacher_lp | Δ vs B2 | mean wall_ms | mean sterile_gens | n |
|--------|-----------------|---------|--------------|-------------------|---|
| B2 | -14.6480 | — | 96 | — | 3 |
| H-SYM | -16.3116 | -1.6636 | 88 | 0.0 | 3 |

**Decision:** KILL / reverse smoke (H-SYM ≤ B2)

Smoke promote was tentative; this run is the claim-facing check.
