# H-ASKABSTAIN — default-ask ABSTAIN (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AS1 · Session: `.local/wave-as/SESSION.md`  
> Parent: [wave-as-session.md](wave-as-session.md) · Charter: AS0 ASKABSTAIN  
> Module: `nano_lm/src/askabstain_ops.py` · Runner: `npm run nano:askabstain`  
> Wire: `run_z_ask.ask_many(..., abstain=True)` default

## Hypothesis

Junk DECODE on OOD/miss must surface as `NO_ANSWER` / `mode=ABSTAIN` on the **default** `nano:z:ask` / apps ask path (not only stage runners). Known LOOKUP stays LOOKUP. False-hit stays 0.

## Gate

| Metric | Result | Pass bar |
|--------|-------:|----------|
| Default-path wired | **True** | True |
| OOD abstain rate | **1.0** (8/8) | ≥ 0.8 |
| FALSE_HIT | **0** | **0** |
| Known LOOKUP ok | **True** | True |
| Modes labeled | **True** | True |
| Decision | **PROMOTE** | — |

## ASKABSTAIN charter (from AS0)

- paths: `['nano:z:ask', 'apps ask']`  
- trigger: DECODE junk / OOD / miss on default ask (not only stage runner)  
- action: `NO_ANSWER` → `mode=ABSTAIN`  
- preserve: known LOOKUP hits stay LOOKUP  
- anti-FP: ABSTAIN on default ask is product honesty — not generative IQ

## OOD / miss pack (default ask)

| id | kind | source_id |
|----|------|-----------|
| AR-ADVREG-09 | ood | ood:sports |
| AR-ADVREG-10 | ood | ood:cooking |
| AR-ADVREG-11 | ood | ood:finance |
| AR-ADVREG-12 | ood | ood:medicine |
| AR-ADVREG-13 | ood | ood:history |
| AR-ADVREG-14 | ood | ood:math |
| AR-ADVREG-18 | trap | trap:period |
| AR-ADVREG-19 | trap | trap:empty |

## Finding

1. Default `ask_once` / `ask_many` apply refuse-junk under max safe CPU (`cpus-2`).  
2. Runner **does not** post-hoc `apply_abstain` — proves wire.  
3. Known-ask WRAP_LOOKUP control must not abstain.  
4. Product honesty only — **not** generative IQ / mini-AGI.

## SAFE ≠ quality

SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP)

## Anti-FP

LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; generative bar = AS7 only; abstain must land on default ask path (not runner-only)

## Reproduce

```bash
npm run nano:askabstain
npm run nano:z:ask -- --question "Which nation hosted the 2016 Summer Olympics?"
```

## Artifacts

- Summary: `results/nano-lm/wave-as/askabstain_summary.json`  
- Trials: `results/nano-lm/wave-as/trials/AS-*.json`  
- Contract: `nano_lm/tests/test_askabstain.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| ABSTAIN on default ask path | Runner-only abstain theater |
| OOD→NO_ANSWER · FH 0 · LOOKUP kept | LOOKUP-as-IQ · mini-AGI |

Next: **AS2 H-SEMFIX** — fix SEMWRAP near-miss (AR-ADVREG-01/05 class).
