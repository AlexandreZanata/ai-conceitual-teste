# Formal H-RETIP — PRE3 train vs live STAG; frozen EARLY/POOL serve

Source: `results/nano-lm/formal-hretip/formal.json`
Wall clock: 227.3s

Capacity question: does TPACK/PRE3 train I/O yield tip capacity (AR lp↑ vs live STAG) **or** a serve win under frozen EARLY/POOL genes? Kill iff tip lp ≤ STAG control **and** no serve win.
Mode: `PRE3 retip vs live STAG; frozen EARLY/POOL serve`; seq_lo=`6` n_stages=`4` steps=`120` top_k=`64` max_new=`48` n_prompts=`8`.

## AR tip (capacity)

| family | mean teacher_lp | Δ lp |
|--------|-----------------|------|
| H-STAG (live) | -13.2775 | — |
| H-RETIP (PRE3) | -12.4946 | +0.7828 |

## Frozen EARLY serve

| ckpt | mean teacher_lp | Δ lp | mean wall_ms | Δ wall |
|------|-----------------|------|--------------|--------|
| live | -10.9680 | — | 66 | — |
| PRE3 | -10.8772 | +0.0908 | 66 | -0 |

## Frozen POOL serve

| ckpt | mean teacher_lp | Δ lp | mean wall_ms | Δ wall |
|------|-----------------|------|--------------|--------|
| live | -11.0527 | — | 73 | — |
| PRE3 | -10.8681 | +0.1846 | 73 | +0 |

**Decision: PROMOTE (capacity+EARLY-serve+POOL-serve win)**

Official tip genes unchanged (not re-searched). Wave U capacity probe.

Commands: `npm run nano:formal:hretip` → `npm run nano:formal:hretip:report`.
