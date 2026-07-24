# Formal H-SHO vs B2 (equal-budget follow-up)

Source: `results/nano-lm/formal-hsho-b2/formal.json`
Wall clock: 182.1s

Prompts: `nano_lm/prompts/eval_prompts.yaml` (8). Seeds: 0,1,2.
B2: KD 120 steps. H-SHO: pop=8, gens=12, mutate + layer shock.
Teacher judge: TinyStories-33M. Fitness: probe CE (no teacher_lp leak).

| family | mean teacher_lp | Δ vs B2 | mean wall_ms | n |
|--------|-----------------|---------|--------------|---|
| B2 | -14.6480 | — | 107 | 3 |
| H-SHO | -16.5129 | -1.8649 | 101 | 3 |

**Decision:** KILL / reverse smoke (H-SHO ≤ B2)

Smoke promote was tentative; this run is the claim-facing check.
