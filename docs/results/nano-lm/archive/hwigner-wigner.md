# H-Q-WIGNER smoke — signed top-k logit quasi-prob (**KILL**)

> Smoke **KILL**. Do not claim signed top-k quasi-prob dual-gate win from wall↓ with identity continuations. Tooling purged.

Wave X QI sandbox: Wigner-like signed mix on top-k softmax — q=p−λ·flip(p) (λ=0.5), relu+renorm, closed top-k support (k=8). Negative mass audited; ≠ Born-rule attn; ≠ TELE inject. Parent = bare H-EARLY on prog@128.

Frozen: ε=0.05; k=8; λ=0.5; max_new=32; seeds=3.

**Decision: KILL (identity vs parent; WIGNER had no effect)**

## Arms

| arm | mean story_lp | mean code_lp | mean wall_ms | mean neg_mass | mean entropy | n |
|-----|---------------|--------------|--------------|---------------|--------------|---|
| H-EARLY bare | -14.8854 | -16.2692 | 22 | 0.000 | 0.000 | 12 |
| H-Q-WIGNER k=8 λ=0.5 | -14.8854 | -16.2692 | 12 | 0.333 | 0.000 | 12 |

## Lesson

Signed mix **ran** (neg_mass≈0.33) and wall↓, but relu+renorm collapsed to a one-hot on the parent mode (entropy≈0) — **all 12** greedy continuations matched EARLY exactly. Classical Wigner quasi-prob on top-k logits is not a free code-IQ lift under greedy EARLY. Next E.1: **H-ABS-CHRONO** (acausal KD soft-label shuffle) — not another logit-space signed mix.

Commands (purged): were `npm run nano:wigner` / `nano:wigner:report`.
