# H-LONGAPP — curated long-doc windows (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8.3 AB3 · Session: `.local/wave-ab/SESSION.md`  
> Parent: **H-ROLL** · **H-SUMCACHE** · **H-SEMWRAP** / **H-ASKFAST** · Pack: AB0 frozen asks  
> Module: `nano_lm/src/longapp_ops.py` · Runner: `npm run nano:longapp`

## Hypothesis

Serve real curated documents under **SUMCACHE + ROLL** (active ≤ 352, L_eff ≫ W) and answer the frozen AB asks via ASKFAST/SEMWRAP — proving longer usable context **without** STREAM / naive flat CTX.

## Gate (Cursor ASK→EVAL→FIX×10)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| mean score | **9.0** | ≥ 7.0 |
| usable | **10**/10 | ≥ **7**/10 |
| FALSE_HIT | **0**/10 | any → **KILL** |
| mean L_eff | **10545** | ≥ 512 |
| mean active | **352** | ≤ 352 (SUMCACHE cap) |
| mean L_eff/W | **82.4** | ≥ 3 |
| FIX count | **0** | — |
| Decision | **PROMOTE** | usable ∧ L_eff ∧ ratio ∧ active ∧ quality |

## Finding

1. Every AB `source_id` loads a real curated blob; SUMCACHE keeps active=352 while L_eff spans 833–37k tokens.  
2. ROLL best-segment overlap selects an in-doc window (not open web).  
3. Answers stay SEMWRAP/ASKFAST TRUE_HIT (scoped assist — **not** open chat).  
4. Forbidden paths unused: STREAM · KVCACHE-Q · GENCACHE · naive CTX.

## Reproduce

```bash
npm run nano:longapp
```

## Artifacts

- Summary: `results/nano-lm/wave-ab/longapp_summary.json`  
- Trials: `results/nano-lm/wave-ab/trials/AB-LONGAPP-HITL-01.json` … `10.json`  
- Contract: `nano_lm/tests/test_longapp.py`

Next: **AB5 H-REALAPP**.
