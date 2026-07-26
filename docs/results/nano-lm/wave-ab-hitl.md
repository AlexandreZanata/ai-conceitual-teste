# AB-HITL-10 — Wave AB final pack verify (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8.3 AB6 · Session: `.local/wave-ab/SESSION.md`  
> Declared stack: ZWRAP · WRAPBANK · SEMWRAP · ASKFAST · LONGAPP · ASKSMART · REALAPP  
> Module: `nano_lm/src/ab_hitl_ops.py` · Runner: `npm run nano:ab:hitl`

## Hypothesis

Final Cursor **ASK→EVAL→FIX×10** on the **declared AB packaged stack** (route known/howto → `app-known`, long-doc → `app-longdoc`) passes mean ≥ **7.0** and errors ≤ **3**/10 without open-chat claims.

## Gate

| Metric | Result | Pass bar |
|--------|-------:|----------|
| mean score | **9.0** | ≥ **7.0** |
| errors | **0**/10 | ≤ **3** |
| false-hit | **0** | must be 0 |
| FIX count | **0** | logged if any |
| claim | scoped packaged stack | not open chat LM |
| Decision | **PROMOTE** | pass_bar ∧ claim_ok ∧ no false-hit |

## Finding

1. Unified router serves all 10 frozen AB asks on the champion wrap + ASKFAST path.  
2. Long-doc items attach LONGAPP (ROLL/SUMCACHE) context metadata (L_eff≫W).  
3. No FIX required — SEMWRAP TRUE_HIT on the full pack.  
4. Honest claim: **scoped AB packaged apps**, not open chat LM. Default demo remains H-ZWRAP + H-WRAPBANK (+ AB stack).

## Reproduce

```bash
npm run nano:ab:hitl
```

## Artifacts

- Summary: `results/nano-lm/wave-ab/ab_hitl_summary.json`  
- Trials: `AB-FINAL-HITL-01.json` … `10.json`  
- Contract: `nano_lm/tests/test_ab_hitl.py`

Next: **AB7 AB-REPORT** (public `wave-ab-summary.md` + paper-lab + FIX log).
