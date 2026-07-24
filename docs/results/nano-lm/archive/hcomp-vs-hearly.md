# H-COMP smoke — torch.compile on EARLY tip genes

Same B2 ckpt + frozen EARLY genes; treatment uses
`torch.compile(..., mode=reduce-overhead)` after warmup.
Kill if quality < EARLY−ε or no wall win.

| family | mean teacher_lp | mean wall_ms | Δ lp vs EARLY | n |
|--------|-----------------|--------------|---------------|---|
| H-EARLY | -16.5322 | 77 | — | 3 |
| H-COMP | -16.5322 | 1480 | +0.0000 | 3 |

**Decision: KILL (no wall win vs H-EARLY)**

Commands: `npm run nano:comp` → `npm run nano:comp:report`.
