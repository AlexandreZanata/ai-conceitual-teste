# Formal H-CBAT vs H-BAT (chunked prefill under batch)

Source: `results/nano-lm/formal-hcbat/formal.json`
Wall clock: 2.4s

Shared formal B2 + formal EARLY exit knobs. Fit≠eval (`eval_prompts`).
Long prompts + chunked KV prefill under FLASH SDPA vs flat BAT.
Mode: `tip-exit knobs; n=1 near-greedy; long eval`. Kill if |Δlp| > ε or no tok/s win.
n_prompts=8 chunk_size=`32` target_tokens=`128`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms/prompt | n |
|--------|-----------------|------|------------|---------|---------------------|---|
| H-BAT | -13.9854 | — | 1751.6 | — | 10 | 3 |
| H-CBAT | -13.9854 | +0.0000 | 3222.6 | +1471.0 | 2 | 3 |

**Decision:** PROMOTE (chunked prefill under BAT)

Throughput util on BAT axis — does not replace H-EARLY / H-BAT tips.

Commands: `npm run nano:formal:hcbat` → `npm run nano:formal:hcbat:report`.
