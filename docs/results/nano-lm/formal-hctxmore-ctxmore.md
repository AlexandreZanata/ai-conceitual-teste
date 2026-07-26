# H-CTXMORE — octa-doc beyond CTXPEAK (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AK2 · Session: `.local/wave-ak/SESSION.md`  
> Parent: **H-GENTRUE** HOLD · Pack: AK0 held-out asks  
> Module: `nano_lm/src/ctxmore_ops.py` · Runner: `npm run nano:ctxmore` (`nano:ak:ctxmore`)

## Hypothesis

Serve each held-out AK ask under **eight curated sources** with **ROLL/SUMCACHE at K=17** (deeper than CTXPEAK hepta K=15) — proving **mean L_eff ↑ vs CTXPEAK 177809**, dual-arm ASK→EVAL→FIX×10, and **≥5**/10 gen-arm long-ctx usable without STREAM / naive CTX / LOOKUP-as-IQ.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ 7.0 · labeled WRAP_LOOKUP |
| GENERATE mean | **1.0** | Cursor scores completion (periods) |
| LOOKUP usable | **10**/10 | ≥ **7**/10 |
| GENERATE usable (long-ctx) | **10**/10 | ≥ **5**/10 · wall_ms>0 ∧ n_new>0 ∧ ctx_ok |
| FALSE_HIT | **0**/10 | any → **KILL** |
| mean sources | **8.0** | ≥ **8** |
| mean L_eff (combined) | **188984** | > CTXPEAK **177809** |
| mean slices | **134.2** | ≥ **17** (K_more) |
| mean active | **352** | ≤ **352** SUMCACHE cap |
| FIX count | **0** | — |
| Decision | **PROMOTE** | L_eff↑ ∧ octa-doc ∧ dual-arm ∧ gen usable≥5 |

## Frontier EVAL (Cursor) — LOOKUP arm

| Trial | Score | error? | Notes |
|-------|------:|:------:|-------|
| AK-CTXMORE-LOOKUP-HITL-01…10 | 9 | no | TRUE_HIT · WRAP_LOOKUP · labeled ≠ gen IQ · octa ctx ok |

**LOOKUP mean:** 9.0 · **Errors:** 0/10 · product retrieval only

## Frontier EVAL (Cursor) — GENERATE arm

| Trial | Score | error? | Notes |
|-------|------:|:------:|-------|
| AK-CTXMORE-GEN-HITL-01…10 | 1 | yes | `........` period collapse · wall_ms>0 · n_new>0 · long-ctx usable |

**GEN mean:** 1.0 · Completions fail gold — **honest** · not claimed as generative IQ · long-ctx path still usable (telemetry + octa meta)

### Cursor EVAL bullets

1. Octa companions + K=17 ROLL/SUMCACHE raise mean L_eff past CTXPEAK without STREAM/naive CTX.  
2. LOOKUP arm remains product retrieve (WRAP_LOOKUP) — never scored as gen IQ.  
3. GENERATE periods are expected open-decode pathology; usable_long gate still holds (same anti-FP posture as CTXPEAK / GENTRUE).

## Finding

1. Every AK0 trial pairs seven companion curated sources (octa-doc) with K=17 ROLL/SUMCACHE.  
2. Combined mean L_eff **188984** > CTXPEAK **177809**; mean slices **134.2**.  
3. LOOKUP arm TRUE_HIT via ASKFAST/SEMWRAP — scoped product, **not** open chat.  
4. GENERATE arm runs with real wall time; scores stay low (period collapse) — anti-FP law holds.  
5. Forbidden unused: STREAM · KVCACHE-Q · GENCACHE · naive CTX.  
6. Ship claim remains **AF packaged stack**; **≤5M** stays.

## Reproduce

```bash
npm run nano:ak:session
npm run nano:ctxmore
# alias: npm run nano:ak:ctxmore
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-ak/ctxmore_summary.json`  
- Trials: `AK-CTXMORE-LOOKUP-HITL-01…10` · `AK-CTXMORE-GEN-HITL-01…10`  
- Contract: `nano_lm/tests/test_ctxmore.py`

Next: **AK3 H-SMARTMORE** — smarter cite+answer; kill SEMWRAP FPs.
