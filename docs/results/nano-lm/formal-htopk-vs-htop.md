# Formal H-TOPK vs tip H-TOP k=64

Source: `results/nano-lm/formal-htopk/formal.json`
Wall clock: 169.5s

Equal formal STAG steps; cache sliced from max challenger/tip width.
Fit≠eval. Gate: some k≠64 with lp ≥ tip−ε **and** ms/step < tip.
Recipe: `seq_lo=6`, `n_stages=4`, `steps=120`, ks=`[32, 64]` (challenger smoke-best k=32).

| top_k | mean teacher_lp | Δ lp vs tip | mean ms/step | Δ ms/step | mean train_wall_s | n |
|-------|-----------------|-------------|--------------|-----------|------------------|---|
| 32 | -12.3345 | +0.1601 | 14.8 | +0.4 | 1.77 | 3 |
| 64 (tip) | -12.4946 | — | 14.4 | — | 1.73 | 3 |

**Decision:** KILL (best ≤ tip k=64 on lp, ms/step)

Tip H-TOP k=64 util unchanged unless PROMOTE replaces default k.

Commands: `npm run nano:formal:htopk` → `npm run nano:formal:htopk:report`.
