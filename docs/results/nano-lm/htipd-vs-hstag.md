# H-TIPD smoke — RETIP → STAG′ xor util

Binary tip decision (Wave V): promote RETIP/PRE3 ckpt to official train tip **STAG′** iff tip lp > live STAG **and** frozen EARLY/POOL serve do not regress (lp ≥ tip−ε). Else keep parked **H-STAG**; RETIP stays util.
Mode: `TIPD: RETIP→STAG′ xor util (capacity + no serve regress)`; seq_lo=`6` n_stages=`4` steps=`30` top_k=`64` max_new=`16` n_prompts=`2` cpu_threads=`12`.

## AR tip (capacity gate)

| family | mean teacher_lp | Δ lp |
|--------|-----------------|------|
| H-STAG (live) | -17.0327 | — |
| STAG′ (RETIP/PRE3) | -16.6988 | +0.3340 |

## Frozen EARLY serve (no-regress gate)

| ckpt | mean teacher_lp | Δ lp | mean wall_ms | Δ wall |
|------|-----------------|------|--------------|--------|
| live | -17.3323 | — | 24 | — |
| STAG′ | -16.7144 | +0.6179 | 22 | -2 |

## Frozen POOL serve (no-regress gate)

| ckpt | mean teacher_lp | Δ lp | mean wall_ms | Δ wall |
|------|-----------------|------|--------------|--------|
| live | -17.0801 | — | 25 | — |
| STAG′ | -16.4536 | +0.6266 | 24 | -2 |

**Decision: PROMOTE (STAG′ replaces H-STAG tip; capacity + serve holds)**
**Tip outcome: `STAG_PRIME`**

Decode tip genes (EARLY/POOL) unchanged. Wave V tip decision.

Commands: `npm run nano:tipd` → `npm run nano:tipd:report`.
