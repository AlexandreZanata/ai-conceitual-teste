# H-QCOMP — classical-shadow KV sketch (**KILL**)

> Smoke tentatively **PROMOTE**; **formal KILL** (story teacher_lp regress). Do not claim shadow-KV long-L serve.

Archived evidence:
- Formal: [`formal-hqcomp-shadow-kv.md`](formal-hqcomp-shadow-kv.md)
- Smoke (superseded): [`hqcomp-shadow-kv-smoke.md`](hqcomp-shadow-kv-smoke.md)

Wave X compression (H-Q-SHADOW classical surrogate under **H-QCOMP**): prefill KV@256, Rademacher Phi → S=64 slots, decode on compressed past. Parent = EARLY@128. Inspiration: classical shadows / ±1 KV projections (no quantum hardware).

**Formal decision: KILL (story_lp −11.0989 < C0−ε −10.3733)**

## Formal arms

| Arm | mean story_lp | mean code_teacher_lp | mean wall_ms | kv_bytes | full_kv_bytes | recon_mse |
|-----|---------------|----------------------|--------------|----------|---------------|-----------|
| C0 EARLY@128 | −10.3233 | −14.1457 | 24 | — | — | — |
| H-QCOMP@256 | −11.0989 | −12.7268 | 11 | 65536 | 289792 | 0.2431 |

## Lesson

Shadow KV **won mem** (65536 < 289792) and **wall↓**, and formal **code_lp ↑** vs C0, but **story_lp** fell below C0−ε → dual-gate **KILL** (same failure mode as MIXD: domain/code win, story regress). Bare random ±1 sequence sketch is not enough; next try critical-token keep + sketch residual (**H-Q-QUBITKV**).

Smoke had tentatively PROMOTE (story held on smoke prompts); formal fit≠eval story gate failed. No ε soften.

Commands (purged): were `npm run nano:qcomp` / `nano:formal:hqcomp*`.
