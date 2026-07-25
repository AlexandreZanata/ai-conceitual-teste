# H-Q-GROVER smoke — next-token mass amplify (**KILL**)

> Smoke **KILL**. Do not claim dual-gate win from p∝p² amplify. Tooling purged.

Wave X QI sandbox: after softmax, apply **R=2** rounds of `p ← normalize(p²)` (classical amplitude amplification on next-token mass), then sample. Parent = fixed H-EARLY on prog@128. ≠ SPIRAL, ≠ ANNEAL, ≠ MIXD.

Frozen: ε=0.05; R=2; max_new=32; seeds=3; prog pack.

**Decision: KILL (story_lp -15.1955 < parent−ε -14.9354)**

## Arms

| arm | mean story_lp | mean code_lp | mean wall_ms | R | n |
|-----|---------------|--------------|--------------|---|---|
| H-EARLY parent | -14.8854 | -16.2692 | 22 | 0 | 12 |
| H-Q-GROVER R=2 | -15.1955 | -7.8783 | 45 | 2 | 12 |

## Lesson

Mass amplify **lifted** `code_teacher_lp` a lot (Δ ≈ +8.4) but **broke** story dual gate and **increased** wall (mean n_new → 32; early-exit starved). Grover-style p∝p² is not a free POOL/EARLY upgrade. Next E.1: **H-Q-TUNNEL** (tiny attn leak under causal mask) — not another mass amplify / SPIRAL / ANNEAL.

Commands (purged): were `npm run nano:grover` / `nano:formal:hgrover*`.
