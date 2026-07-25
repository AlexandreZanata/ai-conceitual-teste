# H-ADAMF smoke — fused AdamW under HALF vs H-HALF

Same top-k soft cache, STAG curriculum, PRE prefetch, and fp16-wire H2D; only AdamW fused=True differs. Kill if |Δlp| > ε vs H-HALF or no ms/step win.
Recipe: `seq_lo=6`, `n_stages=4`, `steps=30`, `top_k=64`, mode `HALF (fp16-wire PRE) + AdamW fused=True vs eager`.

| family | mean teacher_lp | Δ lp | mean ms/step | Δ ms/step | mean train_wall_s | n |
|--------|-----------------|------|--------------|-----------|------------------|---|
| H-HALF | -16.6988 | — | 7.2 | — | 0.22 | 3 |
| H-ADAMF | -16.6988 | +0.0000 | 5.9 | -1.2 | 0.18 | 3 |

**Decision: PROMOTE (fused AdamW under HALF)**

Tip H-HALF / H-PRE util unchanged unless PROMOTE. Train I/O deepen.

Commands: `npm run nano:adamf` → `npm run nano:adamf:report`.
