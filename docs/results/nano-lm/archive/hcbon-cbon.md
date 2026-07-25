# H-ABS-CBON — code-teacher BoN commit (**KILL**)

> Smoke **KILL**. Do not claim code↑ as a dual-gate win when story regresses. Tooling purged.

Wave X absurd sandbox: EARLY K-beam decode → commit by frozen `code_teacher_lp` (≠ story BoN; ≠ INTERF α-mix; ≠ POOL student-lp). Parent = bare H-EARLY n=1 greedy on prog@128.

Frozen: K=4; CBON_TEMP=0.8; ε_lp=0.05; max_new=32; seeds=3; unique@K gate ≥1.5.

## Smoke

| arm | mean story_lp | mean code_lp | mean wall_ms | mean unique | n |
|-----|---------------|--------------|--------------|-------------|---|
| H-EARLY n=1 | -14.8854 | -16.2692 | 21 | 1.000 | 12 |
| H-ABS-CBON k=4 | -16.5844 | -7.8866 | 72 | 4.000 | 12 |

**Decision: KILL (story_lp -16.5844 < parent−ε -14.9354)**

Code↑ Δ≈+8.38 with unique@K=4 (diversity real), but story_lp fell past ε and wall↑ ~3.4×.

## Lesson

Selecting the beam that maximizes frozen code-teacher LP **does** lift `code_teacher_lp` and yields distinct beams, but it is not dual-gate safe: story teacher LP regresses and latency rises. Code-only BoN commit ≠ free IQ without story HOLD — same dual-gate lesson as INTERF (code↑ story↓). Next: **HOLD** or propose a new H-ID (do not revive INTERF/CBON selection variants without a story-safe commit rule).

Commands (purged): were `npm run nano:cbon` / `nano:cbon:report`.
