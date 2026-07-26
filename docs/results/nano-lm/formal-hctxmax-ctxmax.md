# H-CTXMAX — multi-doc beyond CTXPLUS (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AE1 · Session: `.local/wave-ae/SESSION.md`  
> Parent: **H-CTXPLUS** · **H-COMPOSE** · **H-SEMWRAP** / **H-ASKFAST** · Pack: AE0 held-out asks  
> Module: `nano_lm/src/ctxmax_ops.py` · Runner: `npm run nano:ctxmax`

## Hypothesis

Serve each held-out AE ask under **dual curated sources** with **CTXPLUS ROLL/SUMCACHE at K=5** (deeper than CTXPLUS K=3) — proving **mean L_eff ↑ vs CTXPLUS 20522.6** and ≥ **7**/10 long usable without STREAM / naive flat CTX.

## Gate (Cursor ASK→EVAL→FIX×10)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| mean score | **9.0** | ≥ 7.0 |
| usable | **10**/10 | ≥ **7**/10 |
| FALSE_HIT | **0**/10 | any → **KILL** |
| mean sources | **2.0** | ≥ **2** |
| mean L_eff (combined) | **31043** | > CTXPLUS **20522.6** |
| mean slices | **10.0** | ≥ **5** (K_max) |
| mean active | **352** | ≤ 352 |
| FIX count | **0** | — |
| Decision | **PROMOTE** | usable ∧ L_eff↑ ∧ multi-doc ∧ quality |

## Finding

1. Every AE0 trial pairs a secondary curated source with the primary (multi-doc).  
2. Combined mean L_eff **31043** > CTXPLUS **20523**; mean slices **10** (5+5) vs CTXPLUS **3**.  
3. All 10 asks TRUE_HIT via wrap/SEMWRAP (scoped assist — **not** open chat).  
4. Forbidden unused: STREAM · KVCACHE-Q · GENCACHE · naive CTX.

## Reproduce

```bash
npm run nano:ae:session
npm run nano:ctxmax
```

## Artifacts

- Summary: `results/nano-lm/wave-ae/ctxmax_summary.json`  
- Trials: `results/nano-lm/wave-ae/trials/AE-CTXMAX-HITL-01.json` … `10.json`  
- Contract: `nano_lm/tests/test_ctxmax.py`

Next: **AE2 H-SMARTMAX**.
