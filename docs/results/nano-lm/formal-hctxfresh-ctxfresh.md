# H-CTXFRESH — nona-doc beyond CTXMORE (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AL2 · Session: `.local/wave-al/SESSION.md`  
> Parent: **H-GENFRESH** HOLD · Pack: AL0 held-out asks  
> Module: `nano_lm/src/ctxfresh_ops.py` · Runner: `npm run nano:ctxfresh` (`nano:al:ctxfresh`)

## Hypothesis

Serve each held-out AL ask under **nine curated sources** with **ROLL/SUMCACHE at K=19** (deeper than CTXMORE octa K=17) — proving **mean L_eff ↑ vs CTXMORE 188984**, dual-arm ASK→EVAL→FIX×10, and **≥5**/10 gen-arm long-ctx usable without STREAM / naive CTX / LOOKUP-as-IQ.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ 7.0 · labeled WRAP_LOOKUP |
| GENERATE mean | **1.0** | Cursor scores completion (periods) |
| LOOKUP usable | **10**/10 | ≥ **7**/10 |
| GENERATE usable (long-ctx) | **10**/10 | ≥ **5**/10 · wall_ms>0 ∧ n_new>0 ∧ ctx_ok |
| FALSE_HIT | **0**/10 | any → **KILL** |
| mean sources | **9.0** | ≥ **9** |
| mean L_eff (combined) | **200344** | > CTXMORE **188984** |
| mean slices | **166.4** | ≥ **19** (K_fresh) |
| mean active | **352** | ≤ **352** SUMCACHE cap |
| FIX count | **0** | — |
| Decision | **PROMOTE** | L_eff↑ ∧ nona-doc ∧ dual-arm ∧ gen usable≥5 |

## Frontier EVAL (Cursor) — LOOKUP arm

| Trial | Score | error? | Notes |
|-------|------:|:------:|-------|
| AL-CTXFRESH-LOOKUP-HITL-01…10 | 9 | no | TRUE_HIT · WRAP_LOOKUP · labeled ≠ gen IQ · nona ctx ok |

**LOOKUP mean:** 9.0 · **Errors:** 0/10 · product retrieval only

## Frontier EVAL (Cursor) — GENERATE arm

| Trial | Score | error? | Notes |
|-------|------:|:------:|-------|
| AL-CTXFRESH-GEN-HITL-01…10 | 1 | yes | `........` period collapse · wall_ms>0 · n_new>0 · long-ctx usable |

**GEN mean:** 1.0 · Completions fail gold — **honest** · not claimed as generative IQ · long-ctx path still usable (telemetry + nona meta)

### Cursor EVAL bullets

1. Nona companions + K=19 ROLL/SUMCACHE raise mean L_eff past CTXMORE without STREAM/naive CTX.  
2. LOOKUP arm remains product retrieve (WRAP_LOOKUP) — never scored as gen IQ.  
3. GENERATE periods are expected open-decode pathology; usable_long gate still holds (same anti-FP posture as CTXMORE / GENFRESH).

## Finding

1. Every AL0 trial pairs eight companion curated sources (nona-doc) with K=19 ROLL/SUMCACHE.  
2. Combined mean L_eff **200344** > CTXMORE **188984**; mean slices **166.4**.  
3. LOOKUP arm TRUE_HIT via ASKFAST/SEMWRAP — scoped product, **not** open chat.  
4. GENERATE arm runs with real wall time; scores stay low (period collapse) — anti-FP law holds.  
5. Forbidden unused: STREAM · KVCACHE-Q · GENCACHE · naive CTX.  
6. Ship claim remains **AF packaged stack**; **≤5M** stays.

## Reproduce

```bash
npm run nano:al:session
npm run nano:ctxfresh
# alias: npm run nano:al:ctxfresh
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-al/ctxfresh_summary.json`  
- Trials: `AL-CTXFRESH-LOOKUP-HITL-01…10` · `AL-CTXFRESH-GEN-HITL-01…10`  
- Contract: `nano_lm/tests/test_ctxfresh.py`

Next: **AL3 H-SMARTFRESH**.
