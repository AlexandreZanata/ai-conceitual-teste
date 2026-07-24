# H-DEPTH smoke — 1-layer STAG + PRUN recover vs tip

Train STAG recipe (`seq_lo=6`, `n_stages=4`) with `n_layers=1` (tip `2`), then magnitude prune + short KD recover. Claim with frozen EARLY genes.
Arch cut ≠ H-THIN (width). Kill if lp < STAG−ε or no wall win.

| family | mean teacher_lp | Δ lp | mean wall_ms | Δ wall | mean est GFLOPs | Δ GFLOPs | params | n |
|--------|-----------------|------|--------------|--------|-----------------|----------|--------|---|
| H-STAG | -16.6551 | — | 120 | — | 8.930 | — | 3348928 | 3 |
| H-DEPTH | -15.8425 | +0.8127 | 62 | -58 | 6.158 | -2.772 | 3299136 | 3 |

**Decision: PROMOTE (shallow STAG+PRUN vs tip)**

Commands: `npm run nano:depth` → `npm run nano:depth:report`.
