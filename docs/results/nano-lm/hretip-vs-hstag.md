# H-RETIP smoke — PRE3 train vs live STAG; frozen EARLY/POOL serve

Capacity question: does TPACK/PRE3 train I/O yield tip capacity (AR lp↑ vs live STAG) **or** a serve win under frozen EARLY/POOL genes? Kill iff tip lp ≤ STAG control **and** no serve win.
Mode: `PRE3 retip vs live STAG; frozen EARLY/POOL serve`; seq_lo=`6` n_stages=`4` steps=`30` top_k=`64` max_new=`16` n_prompts=`2`.

## AR tip (capacity)

| family | mean teacher_lp | Δ lp |
|--------|-----------------|------|
| H-STAG (live) | -17.0327 | — |
| H-RETIP (PRE3) | -16.6988 | +0.3340 |

## Frozen EARLY serve

| ckpt | mean teacher_lp | Δ lp | mean wall_ms | Δ wall |
|------|-----------------|------|--------------|--------|
| live | -16.3871 | — | 23 | — |
| PRE3 | -15.4930 | +0.8941 | 22 | -1 |

## Frozen POOL serve

| ckpt | mean teacher_lp | Δ lp | mean wall_ms | Δ wall |
|------|-----------------|------|--------------|--------|
| live | -16.9990 | — | 26 | — |
| PRE3 | -15.6416 | +1.3574 | 23 | -2 |

**Decision: PROMOTE (capacity+EARLY-serve+POOL-serve win)**

Official tip genes unchanged (not re-searched). Wave U capacity probe.

Commands: `npm run nano:retip` → `npm run nano:retip:report`.
