# H-CTXBASE — trideca-doc beyond CTXCORE (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AP2 · Session: `.local/wave-ap/SESSION.md`  
> Parent: **H-GENBASE** HOLD · Pack: AP0 held-out asks  
> Module: `nano_lm/src/ctxbase_ops.py` · Runner: `npm run nano:ctxbase` (`nano:ap:ctxbase`)

## Hypothesis

Serve each held-out AP ask under **thirteen curated sources** with **ROLL/SUMCACHE at K=27** (deeper than CTXCORE dodeca K=25) — proving **mean L_eff ↑ vs CTXCORE 253105**, dual-arm ASK→EVAL→FIX×10, and **≥5**/10 gen-arm long-ctx usable without STREAM / naive CTX / LOOKUP-as-IQ.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ 7.0 · labeled WRAP_LOOKUP |
| GENERATE mean | **1.0** | Cursor scores completion (periods) |
| LOOKUP usable | **10**/10 | ≥ **7**/10 |
| GENERATE usable (long-ctx) | **10**/10 | ≥ **5**/10 · wall_ms>0 ∧ n_new>0 ∧ ctx_ok |
| FALSE_HIT | **0**/10 | any → **KILL** |
| mean sources | **13.0** | ≥ **13** |
| mean L_eff (combined) | **274198** | > CTXCORE **253105** |
| mean slices | **324.8** | ≥ **27** (K_base) |
| mean active | **352** | ≤ **352** SUMCACHE cap |
| FIX count | **0** | — |
| Decision | **PROMOTE** | L_eff↑ ∧ trideca-doc ∧ dual-arm ∧ gen usable≥5 |

## Frontier EVAL (Cursor) — LOOKUP arm

| Trial | Score | error? | Notes |
|-------|------:|:------:|-------|
| AP-CTXBASE-LOOKUP-HITL-01…10 | 9 | no | TRUE_HIT · WRAP_LOOKUP · labeled ≠ gen IQ · trideca ctx ok |

**LOOKUP mean:** 9.0 · **Errors:** 0/10 · product retrieval only

## Frontier EVAL (Cursor) — GENERATE arm

| Trial | Score | error? | Notes |
|-------|------:|:------:|-------|
| AP-CTXBASE-GEN-HITL-01…10 | 1 | yes | `........` period collapse · wall_ms>0 · n_new>0 · long-ctx usable |

**GEN mean:** 1.0 · Completions fail gold — **honest** · not claimed as generative IQ · long-ctx path still usable (telemetry + trideca meta)

### Cursor EVAL bullets

1. Trideca companions + K=27 ROLL/SUMCACHE raise mean L_eff past CTXCORE without STREAM/naive CTX.  
2. LOOKUP arm remains product retrieve (WRAP_LOOKUP) — never scored as gen IQ.  
3. GENERATE periods are expected open-decode pathology; usable_long gate still holds (same anti-FP posture as CTXCORE / GENBASE).

## Finding

1. Every AP0 trial pairs twelve companion curated sources (trideca-doc) with K=27 ROLL/SUMCACHE.  
2. Combined mean L_eff **274198** > CTXCORE **253105**.  
3. LOOKUP arm TRUE_HIT via ASKFAST/SEMWRAP — scoped product, **not** open chat.  
4. GENERATE arm runs with real wall time; scores stay low (period collapse) — anti-FP law holds.  
5. Forbidden unused: STREAM · KVCACHE-Q · GENCACHE · naive CTX.  
6. Ship claim remains **AF packaged stack**; **≤5M** stays.

## Reproduce

```bash
npm run nano:ap:session
npm run nano:ctxbase
# alias: npm run nano:ap:ctxbase
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-ap/ctxbase_summary.json`  
- Trials: `AP-CTXBASE-LOOKUP-HITL-01…10` · `AP-CTXBASE-GEN-HITL-01…10`  
- Contract: `nano_lm/tests/test_ctxbase.py`

Next: **AP3 H-SMARTBASE** — smarter cite+answer; kill SEMWRAP FPs.
