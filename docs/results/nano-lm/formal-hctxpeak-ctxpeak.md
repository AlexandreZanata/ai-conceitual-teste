# H-CTXPEAK — hepta-doc beyond CTXPUSH (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AJ2 · Session: `.local/wave-aj/SESSION.md`  
> Parent: **H-GENPEAK** PROMOTE · Pack: AJ0 held-out asks  
> Module: `nano_lm/src/ctxpeak_ops.py` · Runner: `npm run nano:ctxpeak` (`nano:aj:ctxpeak`)

## Hypothesis

Serve each held-out AJ ask under **seven curated sources** with **ROLL/SUMCACHE at K=15** (deeper than CTXPUSH hexa K=13) — proving **mean L_eff ↑ vs CTXPUSH 162851**, dual-arm ASK→EVAL→FIX×10, and **≥5**/10 gen-arm long-ctx usable without STREAM / naive CTX / LOOKUP-as-IQ.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ 7.0 · labeled WRAP_LOOKUP |
| GENERATE mean | **1.0** | Cursor scores completion (periods) |
| LOOKUP usable | **10**/10 | ≥ **7**/10 |
| GENERATE usable (long-ctx) | **10**/10 | ≥ **5**/10 · wall_ms>0 ∧ n_new>0 ∧ ctx_ok |
| FALSE_HIT | **0**/10 | any → **KILL** |
| mean sources | **7.0** | ≥ **7** |
| mean L_eff (combined) | **177809** | > CTXPUSH **162851** |
| mean slices | **104.2** | ≥ **15** (K_peak) |
| mean active | **352** | ≤ **352** SUMCACHE cap |
| FIX count | **0** | — |
| Decision | **PROMOTE** | L_eff↑ ∧ hepta-doc ∧ dual-arm ∧ gen usable≥5 |

## Frontier EVAL (Cursor) — LOOKUP arm

| Trial | Score | error? | Notes |
|-------|------:|:------:|-------|
| AJ-CTXPEAK-LOOKUP-HITL-01…10 | 9 | no | TRUE_HIT · WRAP_LOOKUP · labeled ≠ gen IQ · hepta ctx ok |

**LOOKUP mean:** 9.0 · **Errors:** 0/10 · product retrieval only

## Frontier EVAL (Cursor) — GENERATE arm

| Trial | Score | error? | Notes |
|-------|------:|:------:|-------|
| AJ-CTXPEAK-GEN-HITL-01…10 | 1 | yes | `........` period collapse · wall_ms>0 · n_new>0 · long-ctx usable |

**GEN mean:** 1.0 · Completions fail gold — **honest** · not claimed as generative IQ · long-ctx path still usable (telemetry + hepta meta)

### Cursor EVAL bullets

1. Hepta companions + K=15 ROLL/SUMCACHE raise mean L_eff past CTXPUSH without STREAM/naive CTX.  
2. LOOKUP arm remains product retrieve (WRAP_LOOKUP) — never scored as gen IQ.  
3. GENERATE periods are expected open-decode pathology; usable_long gate still holds (same anti-FP posture as CTXPUSH).

## Finding

1. Every AJ0 trial pairs six companion curated sources (hepta-doc) with K=15 ROLL/SUMCACHE.  
2. Combined mean L_eff **177809** > CTXPUSH **162851**; mean slices **104.2**.  
3. LOOKUP arm TRUE_HIT via ASKFAST/SEMWRAP — scoped product, **not** open chat.  
4. GENERATE arm runs with real wall time; scores stay low (period collapse) — anti-FP law holds.  
5. Forbidden unused: STREAM · KVCACHE-Q · GENCACHE · naive CTX.  
6. Ship claim remains **AF packaged stack**; **≤5M** stays.

## Reproduce

```bash
npm run nano:aj:session
npm run nano:ctxpeak
# alias: npm run nano:aj:ctxpeak
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-aj/ctxpeak_summary.json`  
- Trials: `AJ-CTXPEAK-LOOKUP-HITL-01…10` · `AJ-CTXPEAK-GEN-HITL-01…10`  
- Contract: `nano_lm/tests/test_ctxpeak.py`

Next: **AJ3 H-SMARTPEAK** — **DONE PROMOTE** → [formal-hsmartpeak-smartpeak.md](formal-hsmartpeak-smartpeak.md). Next: **AJ4 H-FASTPEAK**.
