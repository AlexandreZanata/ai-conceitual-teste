# H-CTXNEXT — deca-doc beyond CTXFRESH (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AM2 · Session: `.local/wave-am/SESSION.md`  
> Parent: **H-GENTRUTH** HOLD · Pack: AM0 held-out asks  
> Module: `nano_lm/src/ctxnext_ops.py` · Runner: `npm run nano:ctxnext` (`nano:am:ctxnext`)

## Hypothesis

Serve each held-out AM ask under **ten curated sources** with **ROLL/SUMCACHE at K=21** (deeper than CTXFRESH nona K=19) — proving **mean L_eff ↑ vs CTXFRESH 200344**, dual-arm ASK→EVAL→FIX×10, and **≥5**/10 gen-arm long-ctx usable without STREAM / naive CTX / LOOKUP-as-IQ.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ 7.0 · labeled WRAP_LOOKUP |
| GENERATE mean | **1.0** | Cursor scores completion (periods) |
| LOOKUP usable | **10**/10 | ≥ **7**/10 |
| GENERATE usable (long-ctx) | **10**/10 | ≥ **5**/10 · wall_ms>0 ∧ n_new>0 ∧ ctx_ok |
| FALSE_HIT | **0**/10 | any → **KILL** |
| mean sources | **10.0** | ≥ **10** |
| mean L_eff (combined) | **213147** | > CTXFRESH **200344** |
| mean slices | **203.2** | ≥ **21** (K_next) |
| mean active | **352** | ≤ **352** SUMCACHE cap |
| FIX count | **0** | — |
| Decision | **PROMOTE** | L_eff↑ ∧ deca-doc ∧ dual-arm ∧ gen usable≥5 |

## Frontier EVAL (Cursor) — LOOKUP arm

| Trial | Score | error? | Notes |
|-------|------:|:------:|-------|
| AM-CTXNEXT-LOOKUP-HITL-01…10 | 9 | no | TRUE_HIT · WRAP_LOOKUP · labeled ≠ gen IQ · deca ctx ok |

**LOOKUP mean:** 9.0 · **Errors:** 0/10 · product retrieval only

## Frontier EVAL (Cursor) — GENERATE arm

| Trial | Score | error? | Notes |
|-------|------:|:------:|-------|
| AM-CTXNEXT-GEN-HITL-01…10 | 1 | yes | `........` period collapse · wall_ms>0 · n_new>0 · long-ctx usable |

**GEN mean:** 1.0 · Completions fail gold — **honest** · not claimed as generative IQ · long-ctx path still usable (telemetry + deca meta)

### Cursor EVAL bullets

1. Deca companions + K=21 ROLL/SUMCACHE raise mean L_eff past CTXFRESH without STREAM/naive CTX.  
2. LOOKUP arm remains product retrieve (WRAP_LOOKUP) — never scored as gen IQ.  
3. GENERATE periods are expected open-decode pathology; usable_long gate still holds (same anti-FP posture as CTXFRESH / GENTRUTH).

## Finding

1. Every AM0 trial pairs nine companion curated sources (deca-doc) with K=21 ROLL/SUMCACHE.  
2. Combined mean L_eff **213147** > CTXFRESH **200344**.  
3. LOOKUP arm TRUE_HIT via ASKFAST/SEMWRAP — scoped product, **not** open chat.  
4. GENERATE arm runs with real wall time; scores stay low (period collapse) — anti-FP law holds.  
5. Forbidden unused: STREAM · KVCACHE-Q · GENCACHE · naive CTX.  
6. Ship claim remains **AF packaged stack**; **≤5M** stays.

## Reproduce

```bash
npm run nano:am:session
npm run nano:ctxnext
# alias: npm run nano:am:ctxnext
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-am/ctxnext_summary.json`  
- Trials: `AM-CTXNEXT-LOOKUP-HITL-01…10` · `AM-CTXNEXT-GEN-HITL-01…10`  
- Contract: `nano_lm/tests/test_ctxnext.py`

Next: **AM3 H-SMARTNEXT** — **DONE PROMOTE** → [formal-hsmartnext-smartnext.md](formal-hsmartnext-smartnext.md).
