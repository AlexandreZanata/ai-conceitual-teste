# H-GENQ-ABS — amplitude/measurement genome (**KILL**)

> Smoke+formal **KILL**. Do not claim amplitude-slot genetics over GENC. Tooling purged.

Wave X genetics (QI): evolve `{K, τ, amp_temp, crit_frac}` (pop≤6, gens=2, fit≠eval) under BUD. Classical surrogate = overlapping prompt slots + Jaccard softmax amplitudes + measure-and-freeze decode blocks. Parent = frozen **H-GENC** genome path (not Born-rule attn / not KV sketch).

Frozen: ε=0.05; H_min=0.05; require K>1 or crit_frac>0 (identity K=1≠mechanism); seeds=3; max_new=32; prog pack.

**Decision: KILL (single-slot identity; no amplitude/crit mechanism)**

## Arms (formal eval)

| arm | mean story_lp | mean code_lp | mean wall_ms | mean ctx_chars | mean H(slots) | mean K | n |
|-----|---------------|--------------|--------------|----------------|---------------|--------|---|
| GENC parent (K=1) | -8.9141 | -13.9039 | 19 | 75 | 0.0 | 1.0 | 12 |
| H-GENQ-ABS best | -8.9141 | -13.9039 | 4 | 75 | 0.0 | 1.0 | 12 |

Smoke best genes were all `K=1` (parent identity); wall↓ vs parent was **not** an amplitude win (CUDA/seed artifact under identical quality). Tightened gate: PROMOTE requires K>1 or crit_frac>0.

## Lesson

Genetic search over amplitude schedules **collapsed to the GENC parent** (single slot). Evolving `{K,τ,amp_temp,crit_frac}` with story-latency fitness does not discover multi-slot mixes that beat GENC on code_lp×wall×mem. Next: stronger code distill (**H-DIST**) or a different E.1 operator — not another amplitude-schedule GA on the same surrogate.

Commands (purged): were `npm run nano:genq` / `nano:formal:hgenq*`.
