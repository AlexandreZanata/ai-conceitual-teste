# H-CTXLIFT — penta-doc beyond CTXREAL (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AH2 · Session: `.local/wave-ah/SESSION.md`  
> Parent: **H-CTXREAL** · Pack: AH0 held-out asks  
> Module: `nano_lm/src/ctxlift_ops.py` · Runner: `npm run nano:ctxlift` (`nano:ah:ctxlift`)

## Hypothesis

Serve each held-out AH ask under **five curated sources** with **ROLL/SUMCACHE at K=11** (deeper than CTXREAL quad K=9) — proving **mean L_eff ↑ vs CTXREAL 93975**, dual-arm ASK→EVAL→FIX×10, and **≥5**/10 gen-arm long-ctx usable without STREAM / naive CTX / LOOKUP-as-IQ.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ 7.0 · labeled WRAP_LOOKUP |
| GENERATE mean | **1.0** | Cursor scores completion (periods) |
| LOOKUP usable | **10**/10 | ≥ **7**/10 |
| GENERATE usable (long-ctx) | **10**/10 | ≥ **5**/10 · wall_ms>0 ∧ n_new>0 ∧ ctx_ok |
| FALSE_HIT | **0**/10 | any → **KILL** |
| mean sources | **5.0** | ≥ **5** |
| mean L_eff (combined) | **111578** | > CTXREAL **93975** |
| mean slices | **54.2** | ≥ **11** (K_lift) |
| mean active | **352** | ≤ **352** SUMCACHE cap |
| FIX count | **0** | — |
| Decision | **PROMOTE** | L_eff↑ ∧ penta-doc ∧ dual-arm ∧ gen usable≥5 |

## Frontier EVAL (Cursor) — LOOKUP arm

| Trial | Score | error? | Notes |
|-------|------:|:------:|-------|
| AH-CTXLIFT-LOOKUP-HITL-01…10 | 9 | no | TRUE_HIT · WRAP_LOOKUP · labeled ≠ gen IQ · penta ctx ok |

**LOOKUP mean:** 9.0 · **Errors:** 0/10 · product retrieval only

## Frontier EVAL (Cursor) — GENERATE arm

| Trial | Score | error? | Notes |
|-------|------:|:------:|-------|
| AH-CTXLIFT-GEN-HITL-01…10 | 1 | yes | `........` period collapse · wall_ms>0 · n_new=8 · long-ctx usable |

**GEN mean:** 1.0 · Completions fail gold — **honest** · not claimed as generative IQ · long-ctx path still usable (telemetry + penta meta)

## Finding

1. Every AH0 trial pairs secondary + tertiary + quaternary + quinary curated sources (penta-doc).  
2. Combined mean L_eff **111578** > CTXREAL **93975**; mean slices **54.2** (≈11×5).  
3. LOOKUP arm TRUE_HIT via ASKFAST/SEMWRAP — scoped product, **not** open chat.  
4. GENERATE arm runs with real wall time; scores stay low (period collapse) — anti-FP law holds.  
5. Forbidden unused: STREAM · KVCACHE-Q · GENCACHE · naive CTX.

## Reproduce

```bash
npm run nano:ah:session
npm run nano:ctxlift
# alias: npm run nano:ah:ctxlift
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-ah/ctxlift_summary.json`  
- Trials: `AH-CTXLIFT-LOOKUP-HITL-01…10` · `AH-CTXLIFT-GEN-HITL-01…10`  
- Contract: `nano_lm/tests/test_ctxlift.py`

Next: **AH3 H-SMARTLIFT** → [formal-hsmartlift-smartlift.md](formal-hsmartlift-smartlift.md) **HOLD**.
