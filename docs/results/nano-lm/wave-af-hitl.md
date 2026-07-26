# AF-HITL-10 — Wave AF final pack verify (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AF5 · Session: `.local/wave-af/SESSION.md`  
> Declared stack: SEMWRAP/ASKFAST + **CTXULTRA · SMARTULTRA · FASTULTRA · APPULTRA**  
> Module: `nano_lm/src/af_hitl_ops.py` · Runner: `npm run nano:af:hitl`

## Hypothesis

Final Cursor **ASK→EVAL→FIX×10** on the **declared AF packaged stack** (APPULTRA route → known/howto/longdoc; long-doc CTXULTRA triple-doc) passes mean ≥ **7.0** and errors ≤ **3**/10 on held-out AF0 asks (≠ AB · ≠ AC · ≠ AD · ≠ AE) without open-chat claims.

## Gate

| Metric | Result | Pass bar |
|--------|-------:|----------|
| mean score | **9.0** | ≥ **7.0** |
| errors | **0**/10 | ≤ **3** |
| false-hit | **0** | must be 0 |
| held-out vs AB/AC/AD/AE | **ok** | no question-text overlap |
| FIX count | **0** | logged if any |
| apps | known 3 · howto 5 · longdoc 2 | APPULTRA `select_app` |
| claim | scoped AF packaged stack | not open chat LM |
| Decision | **PROMOTE** | pass_bar ∧ claim_ok ∧ held_out ∧ no false-hit |

## Frontier EVAL (Cursor)

| Trial | Score | error? | Notes (3 bullets) |
|-------|------:|:------:|-------------------|
| AF-FINAL-HITL-01 | 9 | no | BIP purpose · TRUE_HIT · app-known |
| AF-FINAL-HITL-02 | 9 | no | BIP 9 · wrap · app-known |
| AF-FINAL-HITL-03 | 9 | no | scalar+compound · app-known |
| AF-FINAL-HITL-04 | 9 | no | Point class · pasteable · app-howto |
| AF-FINAL-HITL-05 | 9 | no | range(3)→0,1,2 · app-howto |
| AF-FINAL-HITL-06 | 9 | no | add(a,b) · app-howto |
| AF-FINAL-HITL-07 | 9 | no | ownership vs GC · app-howto |
| AF-FINAL-HITL-08 | 9 | no | struct User · app-howto |
| AF-FINAL-HITL-09 | 9 | no | Core P2P · CTXULTRA · app-longdoc |
| AF-FINAL-HITL-10 | 9 | no | TLS handshake · CTXULTRA · app-longdoc |

**Running mean:** 9.0 · **Errors:** 0/10 · **FIX actions:** 0

## Finding

1. Unified APPULTRA router serves all 10 held-out AF asks on champion wrap + ASKFAST.  
2. Long-doc items attach CTXULTRA triple-doc context metadata (n_sources≥3).  
3. No FIX required — SEMWRAP TRUE_HIT on the full pack.  
4. Honest claim: **scoped AF packaged stack** — not open chat LM.  
5. Ship claim may now reference the **AF stack** (no longer AE-only).

## Reproduce

```bash
npm run nano:af:session
npm run nano:af:hitl
```

## Artifacts

- Summary: `results/nano-lm/wave-af/af_hitl_summary.json`  
- Trials: `AF-FINAL-HITL-01.json` … `10.json`  
- Contract: `nano_lm/tests/test_af_hitl.py`

Next: **AF6 AF-REPORT** (**DONE** — see [wave-af-summary.md](wave-af-summary.md) · [paper-lab-wave-af.md](paper-lab-wave-af.md)). Next wave stage: **AF7 AF-FREEZE**.
