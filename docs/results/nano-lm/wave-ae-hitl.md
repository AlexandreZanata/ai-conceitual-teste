# AE-HITL-10 — Wave AE final pack verify (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AE5 · Session: `.local/wave-ae/SESSION.md`  
> Declared stack: SEMWRAP/ASKFAST + **CTXMAX · SMARTMAX · FASTMAX · APPMAX**  
> Module: `nano_lm/src/ae_hitl_ops.py` · Runner: `npm run nano:ae:hitl`

## Hypothesis

Final Cursor **ASK→EVAL→FIX×10** on the **declared AE packaged stack** (APPMAX route → known/howto/longdoc; long-doc CTXMAX) passes mean ≥ **7.0** and errors ≤ **3**/10 on held-out AE0 asks (≠ AB · ≠ AC · ≠ AD) without open-chat claims.

## Gate

| Metric | Result | Pass bar |
|--------|-------:|----------|
| mean score | **9.0** | ≥ **7.0** |
| errors | **0**/10 | ≤ **3** |
| false-hit | **0** | must be 0 |
| held-out vs AB/AC/AD | **ok** | no question-text overlap |
| FIX count | **0** | logged if any |
| apps | known 3 · howto 3 · longdoc 4 | APPMAX `select_app` |
| claim | scoped AE packaged stack | not open chat LM |
| Decision | **PROMOTE** | pass_bar ∧ claim_ok ∧ held_out ∧ no false-hit |

## Finding

1. Unified APPMAX router serves all 10 held-out AE asks on champion wrap + ASKFAST.  
2. Long-doc items attach CTXMAX multi-doc context metadata.  
3. No FIX required — SEMWRAP TRUE_HIT on the full pack.  
4. Honest claim: **scoped AE packaged stack** — not open chat LM.  
5. Ship claim may now reference the **AE stack** (no longer AD-only).

## Reproduce

```bash
npm run nano:ae:session
npm run nano:ae:hitl
```

## Artifacts

- Summary: `results/nano-lm/wave-ae/ae_hitl_summary.json`  
- Trials: `AE-FINAL-HITL-01.json` … `10.json`  
- Contract: `nano_lm/tests/test_ae_hitl.py`

Next: **AE6 AE-REPORT**.
