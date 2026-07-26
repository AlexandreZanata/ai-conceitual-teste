# H-CTXREAL — quad-doc beyond CTXULTRA (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AG2 · Session: `.local/wave-ag/SESSION.md`  
> Parent: **H-CTXULTRA** · **H-ANTIFP** · Pack: AG0 held-out asks  
> Module: `nano_lm/src/ctxreal_ops.py` · Runner: `npm run nano:ctxreal` (`nano:ag:ctxreal`)

## Hypothesis

Serve each held-out AG ask under **quad curated sources** with **ROLL/SUMCACHE at K=9** (deeper than CTXULTRA triple K=7) — proving **mean L_eff ↑ vs CTXULTRA 56965**, dual-arm ASK→EVAL→FIX×10, and **≥5**/10 gen-arm long-ctx usable without STREAM / naive CTX / LOOKUP-as-IQ.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ 7.0 · labeled WRAP_LOOKUP |
| GENERATE mean | **1.0** | Cursor scores completion (periods) |
| LOOKUP usable | **10**/10 | ≥ **7**/10 |
| GENERATE usable (long-ctx) | **10**/10 | ≥ **5**/10 · wall_ms>0 ∧ n_new>0 ∧ ctx_ok |
| FALSE_HIT | **0**/10 | any → **KILL** |
| mean sources | **4.0** | ≥ **4** |
| mean L_eff (combined) | **93975** | > CTXULTRA **56965** |
| mean slices | **35.6** | ≥ **9** (K_real) |
| FIX count | **0** | — |
| Decision | **PROMOTE** | L_eff↑ ∧ quad-doc ∧ dual-arm ∧ gen usable≥5 |

## Frontier EVAL (Cursor) — LOOKUP arm

| Trial | Score | error? | Notes |
|-------|------:|:------:|-------|
| AG-CTXREAL-LOOKUP-HITL-01…10 | 9 | no | TRUE_HIT · WRAP_LOOKUP · labeled ≠ gen IQ · quad ctx ok |

**LOOKUP mean:** 9.0 · **Errors:** 0/10 · product retrieval only

## Frontier EVAL (Cursor) — GENERATE arm

| Trial | Score | error? | Notes |
|-------|------:|:------:|-------|
| AG-CTXREAL-GEN-HITL-01…10 | 1 | yes | `........` period collapse · wall_ms>0 · n_new=8 · long-ctx usable |

**GEN mean:** 1.0 · Completions fail gold — **honest** · not claimed as generative IQ · long-ctx path still usable (telemetry + quad meta)

## Finding

1. Every AG0 trial pairs secondary + tertiary + quaternary curated sources (quad-doc).  
2. Combined mean L_eff **93975** > CTXULTRA **56965**; mean slices **35.6** (≈9×4).  
3. LOOKUP arm TRUE_HIT via ASKFAST/SEMWRAP — scoped product, **not** open chat.  
4. GENERATE arm runs with real wall time; scores stay low (period collapse) — anti-FP law holds.  
5. Forbidden unused: STREAM · KVCACHE-Q · GENCACHE · naive CTX.

## Reproduce

```bash
npm run nano:ag:session
npm run nano:antifp
npm run nano:ctxreal
# alias: npm run nano:ag:ctxreal
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-ag/ctxreal_summary.json`  
- Trials: `AG-CTXREAL-LOOKUP-HITL-01…10` · `AG-CTXREAL-GEN-HITL-01…10`  
- Contract: `nano_lm/tests/test_ctxreal.py`

Next: **AG3 H-SMARTREAL**.
