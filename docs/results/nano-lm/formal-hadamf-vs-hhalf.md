# Formal H-ADAMF vs H-HALF (fused AdamW under HALF)

Source: `results/nano-lm/formal-hadamf/formal.json`
Wall clock: 157.5s

Same top-k soft cache and HALF I/O path; only AdamW fused differs.
Fit≠eval. Gate: |Δlp| ≤ ε **and** train ms/step < HALF.
Recipe: `seq_lo=6`, `n_stages=4`, `steps=120`, `top_k=64`, mode `HALF (fp16-wire PRE) + AdamW fused=True vs eager`.

| family | mean teacher_lp | Δ lp | mean ms/step | Δ ms/step | mean train_wall_s | n |
|--------|-----------------|------|--------------|-----------|------------------|---|
| H-HALF | -12.4946 | — | 14.7 | — | 1.76 | 3 |
| H-ADAMF | -12.4946 | +0.0000 | 14.1 | -0.5 | 1.69 | 3 |

**Decision:** PROMOTE (fused AdamW under HALF)

Tip H-HALF / H-PRE util unchanged. Train I/O deepen.

Commands: `npm run nano:formal:hadamf` → `npm run nano:formal:hadamf:report`.
