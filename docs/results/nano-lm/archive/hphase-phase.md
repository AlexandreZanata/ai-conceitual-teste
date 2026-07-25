# H-ABS-PHASE smoke — 2D rotary / complex phase on Q/K (**KILL**)

> Smoke **KILL**. Do not claim 2D-rotary dual-gate win from wall↓ with identical text. Tooling purged.

Wave X absurd sandbox: apply RoPE-like 2D rotary (e^{iθ(t)}, base=10000) on GPT-Neo Q/K — not Hilbert `position_ids` (SPIRAL). Parent = bare H-EARLY on prog@128. Gate: not identity, both lps ≥ parent−ε, (code↑ or wall↓); audit mean |θ|.

Frozen: ε=0.05; theta_base=10000; max_new=32; seeds=3; identity gate.

**Decision: KILL (identity vs parent; PHASE had no effect)**

## Arms

| arm | mean story_lp | mean code_lp | mean wall_ms | mean_abs_theta | n |
|-----|---------------|--------------|--------------|----------------|---|
| H-EARLY bare | -14.8854 | -16.2692 | 23 | 0.0000 | 12 |
| H-ABS-PHASE base=10000 | -14.8854 | -16.2692 | 15 | 13.1000 | 12 |

## Lesson

2D rotary **did** rotate Q/K (mean |θ|≈13) and cut wall, but **all 12** greedy continuations matched parent story/code LPs exactly — identity under EARLY. Injecting e^{iθ} atop absolute wpe is not a free RoPE upgrade when argmax paths collapse. Next E.1: **H-Q-ENTPOS** (entangled pos⊗tok bias) — not another rotary/Hilbert/SPIRAL remap.

Commands (purged): were `npm run nano:phase` / `nano:formal:hphase*`.
