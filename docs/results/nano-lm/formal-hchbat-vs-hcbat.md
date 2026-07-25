# Formal H-CHBAT vs H-CBAT (CHB B under CBAT)

Source: `results/nano-lm/formal-hchbat/formal.json`
Wall clock: 8.5s

Shared formal B2 + formal EARLY exit knobs. Fit≠eval (`eval_prompts`).
Long prompts; CBAT tip B vs CHB tip B under FLASH SDPA.
Mode: `tip-exit knobs; n=1 near-greedy; long eval; CHB B vs CBAT`. Kill if |Δlp| > ε or no tok/s win.
n_prompts=8 tip_chunk=`32` chunk_size=`256` target_tokens=`128`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms/prompt | n |
|--------|-----------------|------|------------|---------|---------------------|---|
| H-CBAT | -13.9854 | — | 2430.1 | — | 10 | 3 |
| H-CHBAT | -13.9854 | +0.0000 | 4256.2 | +1826.1 | 2 | 3 |

**Decision:** PROMOTE (CHB B under CBAT)

Throughput util on CBAT axis — does not replace H-EARLY / H-CBAT tips.

Commands: `npm run nano:formal:hchbat` → `npm run nano:formal:hchbat:report`.
