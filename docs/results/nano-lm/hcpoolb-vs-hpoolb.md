# H-CPOOLB smoke — chunked prefill under POOLB vs flat POOLB

Left-pad multi-prompt POOL/BoN batch; prefill prompt in blocks of B (CHB tip B) with KV under FLASH SDPA (n=1 near-greedy).
Long prompts (same pack for both arms). Kill if |Δlp| > ε vs H-POOLB or no tok/s win.
Prompt pack: smoke+fit elongated (`n_prompts=4`); chunk_size=`256` target_tokens=`128`; mode `POOL tip top_p; n=1 near-greedy; long prompts`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms/prompt | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|------------|---------|---------------------|--------|-----------------|----------|---|
| H-POOLB | -10.3848 | — | 1311.8 | — | 34 | — | 31.989 | — | 3 |
| H-CPOOLB | -10.3848 | +0.0000 | 2747.2 | +1435.5 | 12 | -21 | 32.878 | +0.889 | 3 |

**Decision: PROMOTE (chunked prefill under POOLB)**

Throughput util on POOLB axis — tip POOL / util POOLB unchanged as tips.

Commands: `npm run nano:cpoolb` → `npm run nano:cpoolb:report`.
