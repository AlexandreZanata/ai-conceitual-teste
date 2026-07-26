# AD-HITL-10 — Wave AD final pack verify (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8.6 AD5 · Session: `.local/wave-ad/SESSION.md`  
> Declared stack: AC spine + HARDPARA · COMPOSE · ROUTEPLUS · DEPLPLUS  
> Module: `nano_lm/src/ad_hitl_ops.py` · Runner: `npm run nano:ad:hitl`

## Hypothesis

Final Cursor **ASK→EVAL→FIX×10** on the **declared AD packaged stack** (ROUTEPLUS → APPPLUS apps; long-doc CTXPLUS) passes mean ≥ **7.0** and errors ≤ **3**/10 on held-out AD0 asks (≠ AB · ≠ AC) without open-chat claims.

## Gate

| Metric | Result | Pass bar |
|--------|-------:|----------|
| mean score | **9.0** | ≥ **7.0** |
| errors | **0**/10 | ≤ **3** |
| false-hit | **0** | must be 0 |
| held-out vs AB/AC | **ok** | no question-text overlap |
| FIX count | **0** | logged if any |
| apps | known 3 · howto 3 · longdoc 4 | ROUTEPLUS covers pack |
| claim | scoped AD packaged stack | not open chat LM |
| Decision | **PROMOTE** | pass_bar ∧ claim_ok ∧ held_out ∧ no false-hit |

## Finding

1. Unified ROUTEPLUS router serves all 10 held-out AD asks on champion wrap + ASKFAST.  
2. Long-doc items attach CTXPLUS (ROLL/SUMCACHE) context metadata.  
3. No FIX required — SEMWRAP TRUE_HIT on the full pack.  
4. Honest claim: **scoped AD packaged stack** on APPPLUS — not open chat LM.

## Reproduce

```bash
npm run nano:ad:hitl
```

## Artifacts

- Summary: `results/nano-lm/wave-ad/ad_hitl_summary.json`  
- Trials: `AD-FINAL-HITL-01.json` … `10.json`  
- Contract: `nano_lm/tests/test_ad_hitl.py`

Next: **AD6 AD-REPORT** (**DONE** — see [wave-ad-summary.md](wave-ad-summary.md) · [paper-lab-wave-ad.md](paper-lab-wave-ad.md)). Next wave stage: **AD7 AD-FREEZE**.
