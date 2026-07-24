# H-SPEC smoke vs B3/B4

Speculative decode (student draft, teacher Leviathan-style accept/reject) on B2 checkpoints.

| family | mean teacher_lp | mean tok/s | mean wall_ms | n seeds |
|--------|-----------------|------------|--------------|---------|
| B3 (AR) | −17.09 | ~680 | ~71 | 3 |
| B4 (BoN) | −17.02 | ~586 | ~54 | 3 |
| H-SPEC | −1.34 | ~134 | ~240 | 3 |

**Decision: KILL** — no tokens/s speedup vs B3 (gate requires faster **and** quality ≥ B3 − 0.05).

Note: elevated teacher_lp under H-SPEC is expected when a weak student draft is rejected often and the residual samples from the teacher; it is not a speed win.

Commands: `npm run nano:spec` → `npm run nano:matrix:report`.  
Artifacts: `results/nano-lm/student-matrix/spec_smoke.json`, `*_eval.json`.
