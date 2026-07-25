# H-ABS-CSAFE — story-constrained code BoN (**KILL**)

> Smoke **KILL**. Story floor alone does not save the dual gate when most beams miss eligibility. Tooling purged.

Wave X absurd sandbox: EARLY K-beam decode → keep beams with `story_lp ≥ parent_story − ε` → commit `argmax code_teacher_lp` among eligible; if none eligible, fallback to max story (≠ unconstrained CBON; ≠ INTERF α-mix). Parent = bare H-EARLY n=1 greedy on prog@128.

Frozen: K=4; CSAFE_TEMP=0.8; ε_lp=0.05; max_new=32; seeds=3; unique@K ≥1.5.

## Smoke

| arm | mean story_lp | mean code_lp | mean wall_ms | mean unique | mean n_elig | n |
|-----|---------------|--------------|--------------|-------------|-------------|---|
| H-EARLY n=1 | -14.8854 | -16.2692 | 22 | 1.000 | 1.00 | 12 |
| H-ABS-CSAFE k=4 | -15.8695 | -8.3700 | 72 | 4.000 | 0.75 | 12 |

**Decision: KILL (story_lp -15.8695 < parent−ε -14.9354)**

Code↑ Δ≈+7.90 with unique@K=4, but mean n_elig≈0.75 (7/12 rows had **zero** eligible beams). Max-story fallback on empty eligible sets still pulled mean story below parent−ε; wall↑ ~3.3×.

## Lesson

A per-beam story floor is not dual-gate safe if the beam bank rarely clears the floor: fallback to “best story among bad beams” ≠ parent HOLD. Next story-safe BoN (if any) must **fallback to the parent continuation** when n_elig=0 — or raise diversity/temp until elig≥1 — not max-story among ineligible. Do not revive unconstrained CBON/INTERF.

Commands (purged): were `npm run nano:csafe` / `nano:csafe:report`.
