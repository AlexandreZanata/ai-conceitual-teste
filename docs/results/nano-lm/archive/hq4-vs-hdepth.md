# H-Q4 smoke — CUDA int4 weight-only vs H-DEPTH

Same `HDEPTH_prun` ckpt + frozen EARLY genes; Linear layers use `aten::_weight_int4pack_mm` (gpt-fast affine group quant). `lm_head` stays fp (out_features % 8 ≠ 0).
Kill if lp < DEPTH−ε or no wall win. Memory bytes reported.
Backend: `aten_int4pack_cuda`; `groupsize=32`; `tiles=2`.

| family | mean teacher_lp | Δ lp | mean wall_ms | Δ wall | mean est GFLOPs | Δ GFLOPs | mean weight_bytes | Δ bytes | n |
|--------|-----------------|------|--------------|--------|-----------------|----------|-------------------|--------|---|
| H-DEPTH | -16.1813 | — | 61 | — | 8.798 | — | 13458692 | — | 3 |
| H-Q4 | -16.1813 | +0.0000 | 45 | -16 | 8.666 | -0.132 | 13292036 | -166656 | 3 |

**Decision: PROMOTE (int4 CUDA decode vs DEPTH)**

Note: systems util on DEPTH ckpt; tip STAG/EARLY genes unchanged.

Commands: `npm run nano:q4` → `npm run nano:q4:report`.
