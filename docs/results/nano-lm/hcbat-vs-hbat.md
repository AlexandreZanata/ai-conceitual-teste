# H-CBAT smoke — chunked prefill under BAT vs flat BAT

Left-pad multi-prompt EARLY batch; prefill prompt in blocks of B with KV under FLASH SDPA (frozen EARLY tip, n=1 near-greedy).
Long prompts (same pack for both arms). Kill if |Δlp| > ε vs H-BAT or no tok/s win.
Prompt pack: smoke+fit elongated (`n_prompts=4`); chunk_size=`32` target_tokens=`128`; mode `n=1 near-greedy; long prompts`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms/prompt | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|------------|---------|---------------------|--------|-----------------|----------|---|
| H-BAT | -12.5933 | — | 846.6 | — | 20 | — | 6.111 | — | 3 |
| H-CBAT | -12.5933 | +0.0000 | 1820.5 | +973.9 | 4 | -16 | 9.734 | +3.624 | 3 |

**Decision: PROMOTE (chunked prefill under BAT)**

Throughput util on BAT axis — tip EARLY / util BAT unchanged as tips.

Commands: `npm run nano:cbat` → `npm run nano:cbat:report`.
