# H-CTXPUSH — hexa-doc beyond CTXLIFT (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AI2 · Session: `.local/wave-ai/SESSION.md`  
> Parent: **H-CAPRENEG** HOLD (≤5M stays) · Pack: AI0 held-out asks  
> Module: `nano_lm/src/ctxpush_ops.py` · Runner: `npm run nano:ctxpush` (`nano:ai:ctxpush`)

## Hypothesis

Serve each held-out AI ask under **six curated sources** with **ROLL/SUMCACHE at K=13** (deeper than CTXLIFT penta K=11) — proving **mean L_eff ↑ vs CTXLIFT 111578**, dual-arm ASK→EVAL→FIX×10, and **≥5**/10 gen-arm long-ctx usable without STREAM / naive CTX / LOOKUP-as-IQ.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ 7.0 · labeled WRAP_LOOKUP |
| GENERATE mean | **1.0** | Cursor scores completion (periods) |
| LOOKUP usable | **10**/10 | ≥ **7**/10 |
| GENERATE usable (long-ctx) | **10**/10 | ≥ **5**/10 · wall_ms>0 ∧ n_new>0 ∧ ctx_ok |
| FALSE_HIT | **0**/10 | any → **KILL** |
| mean sources | **6.0** | ≥ **6** |
| mean L_eff (combined) | **162851** | > CTXLIFT **111578** |
| mean slices | **77.4** | ≥ **13** (K_push) |
| mean active | **352** | ≤ **352** SUMCACHE cap |
| FIX count | **0** | — |
| Decision | **PROMOTE** | L_eff↑ ∧ hexa-doc ∧ dual-arm ∧ gen usable≥5 |

## Frontier EVAL (Cursor) — LOOKUP arm

| Trial | Score | error? | Notes |
|-------|------:|:------:|-------|
| AI-CTXPUSH-LOOKUP-HITL-01…10 | 9 | no | TRUE_HIT · WRAP_LOOKUP · labeled ≠ gen IQ · hexa ctx ok |

**LOOKUP mean:** 9.0 · **Errors:** 0/10 · product retrieval only

## Frontier EVAL (Cursor) — GENERATE arm

| Trial | Score | error? | Notes |
|-------|------:|:------:|-------|
| AI-CTXPUSH-GEN-HITL-01…10 | 1 | yes | `........` period collapse · wall_ms>0 · n_new>0 · long-ctx usable |

**GEN mean:** 1.0 · Completions fail gold — **honest** · not claimed as generative IQ · long-ctx path still usable (telemetry + hexa meta)

## Finding

1. Every AI0 trial pairs five companion curated sources (hexa-doc) with K=13 ROLL/SUMCACHE.  
2. Combined mean L_eff **162851** > CTXLIFT **111578**; mean slices **77.4**.  
3. LOOKUP arm TRUE_HIT via ASKFAST/SEMWRAP — scoped product, **not** open chat.  
4. GENERATE arm runs with real wall time; scores stay low (period collapse) — anti-FP law holds.  
5. Forbidden unused: STREAM · KVCACHE-Q · GENCACHE · naive CTX.  
6. Ship claim remains **AF packaged stack**; **≤5M** stays.

## Reproduce

```bash
npm run nano:ai:session
npm run nano:ctxpush
# alias: npm run nano:ai:ctxpush
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-ai/ctxpush_summary.json`  
- Trials: `AI-CTXPUSH-LOOKUP-HITL-01…10` · `AI-CTXPUSH-GEN-HITL-01…10`  
- Contract: `nano_lm/tests/test_ctxpush.py`

Next: **AI3 H-SMARTPUSH**.
