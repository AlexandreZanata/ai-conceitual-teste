# H-TIE smoke — tied embed + shared block vs H-STAG

Train under STAG recipe (`seq_lo=6`, `n_stages=4`) with UT-lite shared depth.
Kill if quality < STAG−ε or no param/FLOP win (FLOPs use full-depth proxy).

| family | mean teacher_lp | Δ lp | mean params | Δ params | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|-------------|----------|-----------------|----------|---|
| H-STAG | -16.5349 | — | 3348928 | — | 6.751 | — | 3 |
| H-TIE | -16.6773 | -0.1425 | 3299136 | -49792 | 6.751 | +0.000 | 3 |

**Decision: KILL (quality drop vs H-STAG)**

Commands: `npm run nano:tie` → `npm run nano:tie:report`.
