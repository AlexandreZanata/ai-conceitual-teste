# Formal H-DECK vs B4 (equal-budget follow-up)

Source: `results/nano-lm/formal-hdeck-b4/formal.json`
Wall clock: 164.3s

Fit prompts: `nano_lm/prompts/fit_prompts.yaml` (f01–f02).
Eval prompts: `nano_lm/prompts/eval_prompts.yaml` (8). Seeds: 0,1,2.
Shared: B2 KD 120 ckpt. B4: fixed BoN. H-DECK: pop=8 gens=12 top_k=2.
Teacher judge: TinyStories-33M. Integrity: fit ∩ eval ids = ∅.

| family | mean teacher_lp | Δ vs B4 | mean wall_ms | overfit | n |
|--------|-----------------|---------|--------------|---------|---|
| B4 | -14.4943 | — | 81 | — | 3 |
| H-DECK | -11.9635 | +2.5308 | 248 | no | 3 |

**Decision:** PROMOTE confirmed (H-DECK > B4)

Smoke promote was tentative; this run is the claim-facing check.
