# Formal H-TIPD — RETIP → STAG′ xor util

Source: `results/nano-lm/formal-htipd/formal.json`
Wall clock: 236.5s

Binary tip decision (Wave V): promote RETIP/PRE3 ckpt to official train tip **STAG′** iff tip lp > live STAG **and** frozen EARLY/POOL serve do not regress (lp ≥ tip−ε). Else keep parked **H-STAG**; RETIP stays util.
Mode: `TIPD: RETIP→STAG′ xor util (capacity + no serve regress)`; seq_lo=`6` n_stages=`4` steps=`120` top_k=`64` max_new=`48` n_prompts=`8` cpu_threads=`12`.

## AR tip (capacity gate)

| family | mean teacher_lp | Δ lp |
|--------|-----------------|------|
| H-STAG (live) | -13.2775 | — |
| STAG′ (RETIP/PRE3) | -12.4946 | +0.7828 |

## Frozen EARLY serve (no-regress gate)

| ckpt | mean teacher_lp | Δ lp | mean wall_ms | Δ wall |
|------|-----------------|------|--------------|--------|
| live | -10.7067 | — | 62 | — |
| STAG′ | -10.6231 | +0.0837 | 62 | -0 |

## Frozen POOL serve (no-regress gate)

| ckpt | mean teacher_lp | Δ lp | mean wall_ms | Δ wall |
|------|-----------------|------|--------------|--------|
| live | -10.9978 | — | 70 | — |
| STAG′ | -10.9854 | +0.0124 | 71 | +0 |

**Decision: PROMOTE (STAG′ replaces H-STAG tip; capacity + serve holds)**
**Tip outcome: `STAG_PRIME`**

Decode tip genes (EARLY/POOL) unchanged. Wave V tip decision.

Commands: `npm run nano:formal:htipd` → `npm run nano:formal:htipd:report`.
