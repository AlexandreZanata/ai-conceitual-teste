# H-Q-BELL smoke — distant-token Bell K/V couple (**KILL**)

> Smoke **KILL**. Do not claim dual-gate win from wall↓ with identical continuations. Tooling purged.

Wave X QI sandbox: patch GPT-Neo `_attn` so positions `(i,i+τ)` mix K/V toward a shared mean latent (classical Bell couple; mix=1). Parent = strict H-EARLY on prog@128. ≠ TUNNEL, ≠ GROVER, ≠ SPIRAL.

Frozen: τ=16; mix=1.0; max_new=32; seeds=3; prog pack; identity gate on story+code means; mem audit.

**Decision: KILL (identity vs parent; Bell had no effect)**

## Arms

| arm | mean story_lp | mean code_lp | mean wall_ms | mean n_pairs | mean peak_mem_mb | n |
|-----|---------------|--------------|--------------|--------------|------------------|---|
| H-EARLY parent | -14.8854 | -16.2692 | 22 | 0.0 | — | 12 |
| H-Q-BELL τ=16 mix=1.00 | -14.8854 | -16.2692 | 11 | 131.2 | 199.1 | 12 |

## Lesson

Bell pairing ran (≈131 peak pairs; ~199 MB peak) and moved logits slightly, but **greedy EARLY continuations matched parent** on all 12 rows — story/code LPs identity. Wall↓ is warm-cache / order artifact. Distant mean-couple of K/V is not a free EARLY upgrade. Next E.1: **H-ABS-ORACLE1** (1-bit hash side channel) — not another KV couple / TUNNEL / GROVER.

Commands (purged): were `npm run nano:bell` / `nano:formal:hbell*`.
