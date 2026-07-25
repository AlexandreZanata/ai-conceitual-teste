# Formal H-CPOOLB vs H-POOLB (chunked prefill under batch POOL)

Source: `results/nano-lm/formal-hcpoolb/formal.json`
Wall clock: 15.8s

Shared formal B2 + formal POOL tip knobs. Fit≠eval (`eval_prompts`).
Long prompts + chunked KV prefill under FLASH SDPA vs flat POOLB.
Mode: `POOL tip top_p; n=1 near-greedy; long eval`. Kill if |Δlp| > ε or no tok/s win.
n_prompts=8 chunk_size=`256` target_tokens=`128`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms/prompt | n |
|--------|-----------------|------|------------|---------|---------------------|---|
| H-POOLB | -11.7094 | — | 1496.7 | — | 34 | 3 |
| H-CPOOLB | -11.7094 | +0.0000 | 5091.3 | +3594.7 | 10 | 3 |

**Decision:** PROMOTE (chunked prefill under POOLB)

Throughput util on POOLB axis — does not replace H-POOL / H-POOLB tips.

Commands: `npm run nano:formal:hcpoolb` → `npm run nano:formal:hcpoolb:report`.
