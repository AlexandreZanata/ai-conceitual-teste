# H-SEMWRAP — fuzzy wrap recall (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8.3 AB1 · Session: `.local/wave-ab/SESSION.md`  
> Parent: **H-ZWRAP** exact LOOKUP · **H-PARA** HOLD (exact-match brittle) · Pack: AB0 frozen asks  
> Module: `nano_lm/src/semwrap_ops.py` · Runner: `npm run nano:semwrap`

## Hypothesis

Semantic / fuzzy recall over **WRAPBANK + error_bank golds** (optional curated-slice token boost) recovers near-known asks that exact `normalize_question` misses — **without** false-hits and **without** open-web RAG.

## Gate (Cursor ASK→EVAL→FIX×10)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| mean score | **9.0** | ≥ 7.0 for PROMOTE |
| errors | **0**/10 | ≤ 3 |
| FALSE_HIT | **0**/10 | any → **KILL** |
| MISS | **0**/10 | — |
| TRUE_HIT | **10**/10 | — |
| FIX count | **0** | no repair needed |
| Decision | **PROMOTE** | pass_bar ∧ no false-hit |

## Finding

1. All 10 frozen AB asks hit via `SEMWRAP_LOOKUP` (Jaccard + BIP canon + light gold/curated boost; threshold 0.25, margin 0.04).  
2. **0 false-hits** — product still scoped known/near-known assist, **not** open chat LM.  
3. Beats PARA (0/10 TRUE_HIT under exact match) on the AB paraphrase-style pack.  
4. Exact `WRAP_LOOKUP` remains first; SEMWRAP is fallback only.

## Reproduce

```bash
npm run nano:semwrap
npm run nano:z:ask -- --semwrap --question "How do BIP-39 mnemonic phrases turn into a wallet seed? Keep it short."
```

## Artifacts

- Summary: `results/nano-lm/wave-ab/semwrap_summary.json`  
- Trials: `results/nano-lm/wave-ab/trials/AB-SEMWRAP-HITL-01.json` … `10.json`  
- Contract: `nano_lm/tests/test_semwrap.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| Near-known ask via fuzzy bank/curated-slice recall | Open chat LM / open-web RAG |
| Honest DEPL: SEMWRAP ⊃ ZWRAP for paraphrases | Revive QI · STREAM · GENCACHE · MIXD · ZPREF |

Next: **AB3 H-LONGAPP**.
