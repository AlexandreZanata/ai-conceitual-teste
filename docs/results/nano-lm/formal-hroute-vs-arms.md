# Formal H-ROUTE vs H-GALL / H-GRAPHF (length-budget router)

Source: `results/nano-lm/formal-hroute/formal.json`
Wall clock: 17.3s

Fit≠eval. Short→GALL; long→GRAPHF/KV. Gate: not dominated by either single arm on (lp, wall).
n_prompts=10 chunk_size=`256` budgets=`[16, 64]` target_tokens=`128`.

| family | mean teacher_lp | Δ lp vs best | mean tok/s | mean wall_ms/prompt | Δ wall vs best | mean est GFLOPs | n |
|--------|-----------------|--------------|------------|---------------------|----------------|-----------------|---|
| H-GALL | -13.9918 | — | 1964.1 | 5 | — | 7.393 | 3 |
| H-GRAPHF | -12.3583 | — | 4555.8 | 8 | — | 43.593 | 3 |
| H-ROUTE | -12.3959 | -0.0375 | 5008.4 | 7 | +2 | 41.016 | 3 |

**Decision:** PROMOTE (length-budget router not dominated)

Tip H-EARLY / H-SERVE unchanged. Length-budget router (Wave R).

Commands: `npm run nano:formal:hroute` → `npm run nano:formal:hroute:report`.
