# Formal H-DEC vs B4 (equal-budget follow-up)

Source: `results/nano-lm/formal-hdec-b4/formal.json`
Wall clock: 352.4s

Fit prompts: `nano_lm/prompts/fit_prompts.yaml` (f01–f02).
Eval prompts: `nano_lm/prompts/eval_prompts.yaml` (8). Seeds: 0,1,2.
Shared: B2 KD 120 ckpt. B4: fixed BoN n=4, T=0.8, p=0.9, max_new=48.
H-DEC: pop=8, gens=12, search max_new=16 on fit; claim on eval.
Teacher judge: TinyStories-33M. Integrity: fit ∩ eval ids = ∅.

| family | mean teacher_lp | Δ vs B4 | mean wall_ms | overfit | n |
|--------|-----------------|---------|--------------|---------|---|
| B4 | -14.4943 | — | 534 | — | 3 |
| H-DEC | -12.0638 | +2.4305 | 1046 | no | 3 |

**Decision:** PROMOTE confirmed (H-DEC > B4)

Smoke promote was tentative; this run is the claim-facing check.
