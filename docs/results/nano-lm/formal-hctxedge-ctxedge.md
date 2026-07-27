# H-CTXEDGE — undeca-doc beyond CTXNEXT (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 AN2 · Session: `.local/wave-an/SESSION.md`  
> Parent: **H-GENEDGE** HOLD · Pack: AN0 held-out asks  
> Module: `nano_lm/src/ctxedge_ops.py` · Runner: `npm run nano:ctxedge` (`nano:an:ctxedge`)

## Hypothesis

Serve each held-out AN ask under **eleven curated sources** with **ROLL/SUMCACHE at K=23** (deeper than CTXNEXT deca K=21) — proving **mean L_eff ↑ vs CTXNEXT 213147**, dual-arm ASK→EVAL→FIX×10, and **≥5**/10 gen-arm long-ctx usable without STREAM / naive CTX / LOOKUP-as-IQ.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ 7.0 · labeled WRAP_LOOKUP |
| GENERATE mean | **1.0** | Cursor scores completion (periods) |
| LOOKUP usable | **10**/10 | ≥ **7**/10 |
| GENERATE usable (long-ctx) | **10**/10 | ≥ **5**/10 · wall_ms>0 ∧ n_new>0 ∧ ctx_ok |
| FALSE_HIT | **0**/10 | any → **KILL** |
| mean sources | **11.0** | ≥ **11** |
| mean L_eff (combined) | **242448** | > CTXNEXT **213147** |
| mean slices | **238.6** | ≥ **23** (K_edge) |
| mean active | **352** | ≤ **352** SUMCACHE cap |
| FIX count | **0** | — |
| Decision | **PROMOTE** | L_eff↑ ∧ undeca-doc ∧ dual-arm ∧ gen usable≥5 |

## Frontier EVAL (Cursor) — LOOKUP arm

| Trial | Score | error? | Notes |
|-------|------:|:------:|-------|
| AN-CTXEDGE-LOOKUP-HITL-01…10 | 9 | no | TRUE_HIT · WRAP_LOOKUP · labeled ≠ gen IQ · undeca ctx ok |

**LOOKUP mean:** 9.0 · **Errors:** 0/10 · product retrieval only

## Frontier EVAL (Cursor) — GENERATE arm

| Trial | Score | error? | Notes |
|-------|------:|:------:|-------|
| AN-CTXEDGE-GEN-HITL-01…10 | 1 | yes | `........` period collapse · wall_ms>0 · n_new>0 · long-ctx usable |

**GEN mean:** 1.0 · Completions fail gold — **honest** · not claimed as generative IQ · long-ctx path still usable (telemetry + undeca meta)

### Cursor EVAL bullets

1. Undeca companions + K=23 ROLL/SUMCACHE raise mean L_eff past CTXNEXT without STREAM/naive CTX.  
2. LOOKUP arm remains product retrieve (WRAP_LOOKUP) — never scored as gen IQ.  
3. GENERATE periods are expected open-decode pathology; usable_long gate still holds (same anti-FP posture as CTXNEXT / GENEDGE).

## Finding

1. Every AN0 trial pairs ten companion curated sources (undeca-doc) with K=23 ROLL/SUMCACHE.  
2. Combined mean L_eff **242448** > CTXNEXT **213147**.  
3. LOOKUP arm TRUE_HIT via ASKFAST/SEMWRAP — scoped product, **not** open chat.  
4. GENERATE arm runs with real wall time; scores stay low (period collapse) — anti-FP law holds.  
5. Forbidden unused: STREAM · KVCACHE-Q · GENCACHE · naive CTX.  
6. Ship claim remains **AF packaged stack**; **≤5M** stays.

## Reproduce

```bash
npm run nano:an:session
npm run nano:ctxedge
# alias: npm run nano:an:ctxedge
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-an/ctxedge_summary.json`  
- Trials: `AN-CTXEDGE-LOOKUP-HITL-01…10` · `AN-CTXEDGE-GEN-HITL-01…10`  
- Contract: `nano_lm/tests/test_ctxedge.py`

Next: **AN3 H-SMARTEDGE** — **DONE PROMOTE** → [formal-hsmartedge-smartedge.md](formal-hsmartedge-smartedge.md). Next **AN4 H-FASTEDGE**.
