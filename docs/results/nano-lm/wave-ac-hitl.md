# AC-HITL-10 — Wave AC final pack verify (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8.5 AC5 · Session: `.local/wave-ac/SESSION.md`  
> Declared stack: ZWRAP · WRAPBANK · SEMWRAP · ASKFAST · ASKSMART · CTXPLUS · SMARTPLUS · FASTPLUS · APPPLUS  
> Module: `nano_lm/src/ac_hitl_ops.py` · Runner: `npm run nano:ac:hitl`

## Hypothesis

Final Cursor **ASK→EVAL→FIX×10** on the **declared AC packaged stack** (route known → `app-known`, howto → `app-howto`, long-doc → `app-longdoc`) passes mean ≥ **7.0** and errors ≤ **3**/10 without open-chat claims.

## Gate

| Metric | Result | Pass bar |
|--------|-------:|----------|
| mean score | **9.0** | ≥ **7.0** |
| errors | **0**/10 | ≤ **3** |
| false-hit | **0** | must be 0 |
| FIX count | **0** | logged if any |
| apps | known 3 · howto 3 · longdoc 4 | router covers pack |
| claim | scoped AC packaged stack | not open chat LM |
| Decision | **PROMOTE** | pass_bar ∧ claim_ok ∧ no false-hit |

## Finding

1. Unified router serves all 10 held-out AC asks on the champion wrap + ASKFAST path.  
2. Long-doc items attach CTXPLUS (ROLL/SUMCACHE) context metadata (L_eff≫AB LONGAPP).  
3. No FIX required — SEMWRAP TRUE_HIT on the full pack.  
4. Honest claim: **scoped AC packaged apps** (app-known + app-howto + app-longdoc), not open chat LM.

## Reproduce

```bash
npm run nano:ac:hitl
```

## Artifacts

- Summary: `results/nano-lm/wave-ac/ac_hitl_summary.json`  
- Trials: `AC-FINAL-HITL-01.json` … `10.json`  
- Contract: `nano_lm/tests/test_ac_hitl.py`

Next: **AC6 AC-REPORT** (see [wave-ac-summary.md](wave-ac-summary.md) when written).
