# H-SMARTPLUS — hard-paraphrase SEMWRAP+ASKSMART (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8.5 AC2 · §12.1 · Session: `.local/wave-ac/SESSION.md`  
> Parent: **H-SEMWRAP** · **H-ASKSMART** · Pack: AC0 held-out asks (hard paraphrases)  
> Module: `nano_lm/src/smartplus_ops.py` · Runner: `npm run nano:smartplus`

## Hypothesis

Stress **SEMWRAP retrieve + ASKSMART stop/anti-period routing** on **harder paraphrases** of the frozen AC0 questions — mean ≥ 7.0 with **false-hit ≈ 0** — without open-chat claims.

## Gate (Cursor ASK→EVAL→FIX×10)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| mean score | **9.0** | ≥ **7.0** |
| FALSE_HIT | **0**/10 | any → **KILL** |
| TRUE_HIT | **10**/10 | — |
| errors | **0**/10 | ≤ 3 |
| FIX count | **0** | — |
| SEMWRAP route | **10**/10 | compose SEMWRAP+ASKSMART |
| Decision | **PROMOTE** | mean≥7 ∧ false-hit=0 ∧ quality |

## Finding

1. All 10 hard paraphrases normalize-differ from AC0 parents and recover correct golds.  
2. ASKSMART `strip_stop` polish keeps wrap completions clean (no period collapse).  
3. FALSE_HIT = 0 under paraphrase stress (scoped assist — **not** open chat).  
4. Forbidden unused: QI · ZPREF · MIXD · open-chat claim.

## Reproduce

```bash
npm run nano:smartplus
```

## Artifacts

- Summary: `results/nano-lm/wave-ac/smartplus_summary.json`  
- Trials: `results/nano-lm/wave-ac/trials/AC-SMARTPLUS-HITL-01.json` … `10.json`  
- Contract: `nano_lm/tests/test_smartplus.py`

Next: **AC3 H-FASTPLUS**.
