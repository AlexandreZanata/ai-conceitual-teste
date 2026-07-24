# Formal H-FIT vs B2 (equal-budget follow-up)

Source: `results/nano-lm/formal-hfit-b2/formal.json`
Wall clock: 240.1s

Fit prompts: `nano_lm/prompts/fit_prompts.yaml` (f01–f02).
Eval prompts: `nano_lm/prompts/eval_prompts.yaml` (8). Seeds: 0,1,2.
B2: KD 120 steps. H-FIT: pop=8, gens=12, max_new_fit=24.
Teacher judge: TinyStories-33M. Integrity: fit ∩ eval ids = ∅.

| family | mean teacher_lp | Δ vs B2 | mean wall_ms | overfit | n |
|--------|-----------------|---------|--------------|---------|---|
| B2 | -14.6480 | — | 86 | — | 3 |
| H-FIT | -16.4839 | -1.8359 | 110 | yes | 3 |

**Decision:** KILL (overfit; H-FIT)

Smoke promote was tentative; this run is the claim-facing check.
