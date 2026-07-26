# H-HARDPARA — adversarial paraphrase SEMWRAP+SMARTPLUS (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8.6 AD1 · §13.1 · Session: `.local/wave-ad/SESSION.md`  
> Parent: **H-SEMWRAP** · **H-SMARTPLUS** · Pack: AD0 held-out asks (adversarial paraphrases)  
> Module: `nano_lm/src/hardpara_ops.py` · Runner: `npm run nano:hardpara`

## Hypothesis

Stress **SEMWRAP retrieve + SMARTPLUS/ASKSMART routing** on **adversarial paraphrases** (informal phrasing / light noise) of the frozen AD0 questions — mean ≥ 7.0 with **false-hit ≈ 0** — without open-chat claims.

## Gate (Cursor ASK→EVAL→FIX×10)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| mean score | **9.0** | ≥ **7.0** |
| FALSE_HIT | **0**/10 | any → **KILL** |
| TRUE_HIT | **10**/10 | — |
| errors | **0**/10 | ≤ 3 |
| FIX count | **0** | — |
| SEMWRAP route | **10**/10 | compose SEMWRAP+SMARTPLUS |
| Decision | **PROMOTE** | mean≥7 ∧ false-hit=0 ∧ quality |

## Finding

1. All 10 adversarial paraphrases normalize-differ from AD0 parents and recover correct golds.  
2. Informal/noise cues (pls / btc / py / RFC glue) still resolve via scoped bank aliases.  
3. FALSE_HIT = 0 under hard-para stress (scoped assist — **not** open chat).  
4. Forbidden unused: QI · ZPREF · MIXD · open-chat claim.

## Reproduce

```bash
npm run nano:hardpara
```

## Artifacts

- Summary: `results/nano-lm/wave-ad/hardpara_summary.json`  
- Trials: `results/nano-lm/wave-ad/trials/AD-HARDPARA-HITL-01.json` … `10.json`  
- Contract: `nano_lm/tests/test_hardpara.py`

Next: **AD2 H-COMPOSE** (**DONE** — see [formal-hcompose-compose.md](formal-hcompose-compose.md)). **AD3 H-ROUTEPLUS** (**DONE** — see [formal-hrouteplus-routeplus.md](formal-hrouteplus-routeplus.md)). Next wave stage: **AD4 H-DEPLPLUS**.
