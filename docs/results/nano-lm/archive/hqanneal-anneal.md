# H-Q-ANNEAL smoke — cooling T(t)+conf(t) on EARLY (**KILL**)

> Smoke **KILL**. Do not claim dual-gate win from anneal schedule. Tooling purged.

Wave X QI sandbox: geometric `T(t): 0.8→1e-6` and `conf(t): 0.95→0.55` per generated token under EARLY. Parent = fixed H-EARLY (PACK tip, temp≈0) on prog@128. ≠ ABS-REV, ≠ INTERF, ≠ MIXD.

Frozen: ε=0.05; max_new=32; seeds=3; prog pack; schedule as above.

**Decision: KILL (story_lp -14.9766 < parent−ε -14.9354)**

## Arms

| arm | mean story_lp | mean code_lp | mean wall_ms | mean n_new | n |
|-----|---------------|--------------|--------------|------------|---|
| H-EARLY parent | -14.8854 | -16.2692 | 22 | 6.7 | 12 |
| H-Q-ANNEAL | -14.9766 | -10.5057 | 16 | 9.2 | 12 |

## Lesson

Cooling schedule **lifted** `code_teacher_lp` (Δ ≈ +5.8) and cut wall, but `story_lp` slipped just below parent−ε (Δ ≈ −0.09). Hot→cold sampling is not a free dual-gate promote vs greedy EARLY. Next E.1: **H-ABS-SPIRAL** (Hilbert/spiral position remap) — not another temp schedule / INTERF mix / reverse-prefill.

Commands (purged): were `npm run nano:anneal` / `nano:formal:hqanneal*`.
