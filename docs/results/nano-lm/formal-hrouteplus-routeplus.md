# H-ROUTEPLUS — cross-app route + honest OOS (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8.6 AD3 · §13.1 · Session: `.local/wave-ad/SESSION.md`  
> Parent: **H-APPPLUS** · Pack: AD0 held-out asks  
> Module: `nano_lm/src/routeplus_ops.py` · Runner: `npm run nano:routeplus`

## Hypothesis

Auto-select the canonical APPPLUS packaged app per held-out surface (`known-ask` → `app-known`, `howto` → `app-howto`, `long-doc` → `app-longdoc`), SERVE in-scope via SEMWRAP/ASKFAST, and **honestly refuse** when probed on a wrong app — no false app claim.

## Gate (Cursor ASK→EVAL→FIX×10)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| mean score | **9.0** | ≥ 7.0 |
| errors | **0**/10 | ≤ 3 |
| correct route | **10**/10 | = 10 |
| honest OOS | **10**/10 | = 10 |
| FALSE_HIT | **0**/10 | any → **KILL** |
| false app claim | **0**/10 | any → **KILL** |
| FIX count | **0** | — |
| Decision | **PROMOTE** | quality ∧ route ∧ OOS ∧ claims |

## Finding

1. Every AD0 surface maps to exactly one APPPLUS app; serve stays in-scope.  
2. Wrong-app probes return `Out of scope…` (howto uses narrow longdoc-only probe).  
3. All 10 asks TRUE_HIT via wrap/SEMWRAP (scoped assist — **not** open chat).  
4. Forbidden unused: STREAM · false app claim · open-chat product language.

## Reproduce

```bash
npm run nano:ad:session
npm run nano:routeplus
```

## Artifacts

- Summary: `results/nano-lm/wave-ad/routeplus_summary.json`  
- Trials: `results/nano-lm/wave-ad/trials/AD-ROUTEPLUS-HITL-01.json` … `10.json`  
- Contract: `nano_lm/tests/test_routeplus.py`

Next: **AD4 H-DEPLPLUS** (**DONE** — see [formal-hdeplplus-deplplus.md](formal-hdeplplus-deplplus.md)). Next wave stage: **AD5 AD-HITL-10**.
