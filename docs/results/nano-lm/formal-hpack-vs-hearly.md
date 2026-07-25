# Formal H-PACK — SERVE + SROUTE packs vs H-EARLY

Source: `results/nano-lm/formal-hpack/formal.json`
Wall clock: 19.0s

Fit≠eval. Freeze SERVE=min-wall (|Δlp|≤ε) and SROUTE=Pareto (lp≥EARLY−ε); both need wall↓ or tok/s↑.
n_prompts=10 chunk_size=`256` budgets=`[16, 64]` target_tokens=`128`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms | Δ wall | mean est GFLOPs | n |
|--------|-----------------|------|------------|---------|--------------|--------|-----------------|---|
| H-EARLY | -13.9921 | — | 671.9 | — | 13 | — | 7.393 | 3 |
| H-SERVE | -13.9918 | +0.0003 | 2685.0 | +2013.1 | 3 | -10 | 7.393 | 3 |
| H-SROUTE | -12.3959 | +1.5963 | 5398.4 | +4726.4 | 6 | -7 | 41.016 | 3 |

**Decision:** PROMOTE (SERVE=min-wall + SROUTE=Pareto packs vs EARLY)

Card hygiene (Wave S). Serving defaults frozen vs tip EARLY.

Commands: `npm run nano:formal:hpack` → `npm run nano:formal:hpack:report`.
