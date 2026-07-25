# Formal H-SERVE vs H-EARLY (full serving stack)

Source: `results/nano-lm/formal-hserve/formal.json`
Wall clock: 18.8s

Fit≠eval. Control: serial EARLY alone. Candidate: best of GALL-speed / GRAPHF-quality (recipes: `speed`). Gate: |Δlp| ≤ ε **and** (wall < EARLY or tok/s > EARLY).
n_prompts=10 chunk_size=`256` budgets=`[16, 64]` target_tokens=`128`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms/prompt | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|------------|---------|---------------------|--------|-----------------|----------|---|
| H-EARLY | -13.9921 | — | 700.2 | — | 13 | — | 7.393 | — | 3 |
| H-SERVE | -13.9918 | +0.0003 | 2824.4 | +2124.2 | 3 | -10 | 7.393 | +0.000 | 3 |

**Decision:** PROMOTE (full serving stack vs EARLY)

Tip H-EARLY unchanged. Full-stack serving claim (Wave R).

Commands: `npm run nano:formal:hserve` → `npm run nano:formal:hserve:report`.
