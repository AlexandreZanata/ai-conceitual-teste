# H-CTXPLUS — multi-slice curated long ctx (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8.5 AC1 · §12.1 · Session: `.local/wave-ac/SESSION.md`  
> Parent: **H-LONGAPP** · **H-ROLL** · **H-SUMCACHE** · **H-SEMWRAP** / **H-ASKFAST** · Pack: AC0 held-out asks  
> Module: `nano_lm/src/ctxplus_ops.py` · Runner: `npm run nano:ctxplus`

## Hypothesis

Serve held-out curated documents under **SUMCACHE + top-K ROLL slices** (K=3, active ≤ 352) and answer AC0 asks via ASKFAST/SEMWRAP — proving **deeper** usable context than AB LONGAPP (mean L_eff ↑) **without** STREAM / naive flat CTX.

## Gate (Cursor ASK→EVAL→FIX×10)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| mean score | **9.0** | ≥ 7.0 |
| usable | **10**/10 | ≥ **7**/10 |
| FALSE_HIT | **0**/10 | any → **KILL** |
| mean L_eff | **20523** | > AB LONGAPP **10544.9** |
| mean active | **352** | ≤ 352 (SUMCACHE cap) |
| mean L_eff/W | **160.3** | ≥ 3 |
| mean slices | **3.0** | ≥ 1 |
| FIX count | **0** | — |
| Decision | **PROMOTE** | usable ∧ L_eff↑ ∧ ratio ∧ active ∧ slices ∧ quality |

## Finding

1. Held-out AC pack mean L_eff **20523** vs AB LONGAPP **10545** (pass L_eff↑).  
2. Top-3 ROLL slices + SUMCACHE keep active=352; 9/10 trials multi-deeper than single window.  
3. All 10 asks TRUE_HIT via wrap/SEMWRAP (scoped assist — **not** open chat).  
4. Forbidden paths unused: STREAM · KVCACHE-Q · GENCACHE · naive CTX.

## Reproduce

```bash
npm run nano:ac:session
npm run nano:ctxplus
```

## Artifacts

- Summary: `results/nano-lm/wave-ac/ctxplus_summary.json`  
- Trials: `results/nano-lm/wave-ac/trials/AC-CTXPLUS-HITL-01.json` … `10.json`  
- Contract: `nano_lm/tests/test_ctxplus.py`

Next: **AC2 H-SMARTPLUS**.
