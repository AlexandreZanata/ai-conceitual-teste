# H-CHBAT smoke — CHB B=256 under CBAT vs tip CBAT

Left-pad multi-prompt EARLY batch; prefill with CHB tip chunk_size (B=256) under FLASH SDPA vs CBAT tip B (`32`).
Long prompts (same pack for both arms). Kill if |Δlp| > ε vs H-CBAT or no tok/s win.
Prompt pack: smoke+fit elongated (`n_prompts=4`); chunk_size=`256` target_tokens=`128`; mode `n=1 near-greedy; long prompts; CHB B vs CBAT tip`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms/prompt | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|------------|---------|---------------------|--------|-----------------|----------|---|
| H-CBAT | -12.5933 | — | 1200.5 | — | 21 | — | 9.734 | — | 3 |
| H-CHBAT | -12.5933 | +0.0000 | 2400.8 | +1200.3 | 3 | -18 | 6.111 | -3.624 | 3 |

**Decision: PROMOTE (CHB B under CBAT)**

Throughput util on CBAT axis — tip EARLY / util CBAT unchanged as tips.

Commands: `npm run nano:chbat` → `npm run nano:chbat:report`.
