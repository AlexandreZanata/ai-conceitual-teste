# H-ABS-SPIRAL smoke — Hilbert-curve position remap (**KILL**)

> Smoke **KILL**. Do not claim locality wins from Hilbert position_ids. Tooling purged.

Wave X ABS sandbox: remap absolute `position_ids` via Hilbert curve (row-major → Hilbert d); token order stays causal. Parent = linear-pos H-EARLY on prog@128. ≠ ANNEAL, ≠ ABS-REV, ≠ MIXD.

Frozen: ε=0.05; max_new=32; seeds=3; prog pack.

**Decision: KILL (story_lp -15.2268 < parent−ε -14.9354)**

## Arms

| arm | mean story_lp | mean code_lp | mean wall_ms | mean pos_alias | n |
|-----|---------------|--------------|--------------|----------------|---|
| H-EARLY linear-pos | -14.8854 | -16.2692 | 22 | 0.0000 | 12 |
| H-ABS-SPIRAL Hilbert-pos | -15.2268 | -14.6702 | 9 | 79.8221 | 12 |

## Lesson

Hilbert remapping cut wall and nudged `code_lp` up, but **broke** story dual gate (Δ ≈ −0.34 vs parent−ε) with large position-alias error (≈80). Space-filling absolute positions are not a free RoPE substitute on this student. Next E.1: **H-Q-GROVER** (attn reweight amplification) — not another pos remap / ANNEAL / reverse-prefill.

Commands (purged): were `npm run nano:spiral` / `nano:formal:hspiral*`.
