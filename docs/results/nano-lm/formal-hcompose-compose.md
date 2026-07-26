# H-COMPOSE — multi-source CTXPLUS compose (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8.6 AD2 · §13.1 · Session: `.local/wave-ad/SESSION.md`  
> Parent: **H-CTXPLUS** · **H-SEMWRAP** / **H-ASKFAST** · Pack: AD0 held-out asks  
> Module: `nano_lm/src/compose_ops.py` · Runner: `npm run nano:compose`

## Hypothesis

Serve each held-out ask under **dual curated sources** (primary + secondary) with **CTXPLUS multi-slice ROLL/SUMCACHE** on both — proving multi-source usable long context ≥ **7**/10 without STREAM / naive flat CTX.

## Gate (Cursor ASK→EVAL→FIX×10)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| mean score | **9.0** | ≥ 7.0 |
| usable | **10**/10 | ≥ **7**/10 |
| FALSE_HIT | **0**/10 | any → **KILL** |
| mean sources | **2.0** | ≥ **2** |
| mean L_eff (combined) | **40928** | ≥ 512 |
| mean slices | **6.0** | ≥ 1 |
| mean active | **352** | ≤ 352 |
| FIX count | **0** | — |
| Decision | **PROMOTE** | usable ∧ multi-source ∧ quality |

## Finding

1. Every AD0 trial pairs a secondary curated source (domain-related) with the primary.  
2. Combined L_eff **40928** with **6** slices mean (3+3); active stays ≤352.  
3. All 10 asks TRUE_HIT via wrap/SEMWRAP (scoped assist — **not** open chat).  
4. Forbidden unused: STREAM · KVCACHE-Q · GENCACHE · naive CTX.

## Reproduce

```bash
npm run nano:ad:session
npm run nano:compose
```

## Artifacts

- Summary: `results/nano-lm/wave-ad/compose_summary.json`  
- Trials: `results/nano-lm/wave-ad/trials/AD-COMPOSE-HITL-01.json` … `10.json`  
- Contract: `nano_lm/tests/test_compose.py`

Next: **AD3 H-ROUTEPLUS** (**DONE** — see [formal-hrouteplus-routeplus.md](formal-hrouteplus-routeplus.md)). Next wave stage: **AD4 H-DEPLPLUS**.
