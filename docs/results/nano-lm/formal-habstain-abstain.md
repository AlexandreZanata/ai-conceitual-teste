# H-ABSTAIN — refuse junk DECODE (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AR1 · Session: `.local/wave-ar/SESSION.md`  
> Parent: [wave-ar-session.md](wave-ar-session.md) · Protocol: AR0 abstention  
> Module: `nano_lm/src/abstain_ops.py` · Runner: `npm run nano:abstain`

## Hypothesis

Junk DECODE on OOD/miss (period-collapse · empty · TinyStories sludge) must surface as `NO_ANSWER` / `mode=ABSTAIN` — not unlabeled garbage. Known LOOKUP stays LOOKUP. False-hit stays 0.

## Gate

| Metric | Result | Pass bar |
|--------|-------:|----------|
| OOD abstain rate | **1.0** (8/8) | ≥ 0.8 |
| FALSE_HIT | **0** | **0** |
| Known LOOKUP ok | **True** | True |
| Modes labeled | **True** | True |
| Decision | **PROMOTE** | — |

## Abstention protocol (from AR0)

- trigger: DECODE junk on OOD/miss (TinyStories garbage, empty, period-collapse, low-grounding)  
- action: `NO_ANSWER` → `ABSTAIN`  
- anti-FP: ABSTAIN is honest product mode — not generative IQ

## OOD / miss pack

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

1. Pure DECODE on OOD/miss under max safe CPU (`cpus-2`).  
2. `apply_abstain` maps junk → `NO_ANSWER` / ABSTAIN.  
3. Known-ask WRAP_LOOKUP control must not abstain.  
4. Product honesty only — **not** generative IQ / mini-AGI.

## Reproduce

```bash
npm run nano:abstain
npm run nano:z:ask -- --question "Which nation hosted the 2016 Summer Olympics?"
```

## Artifacts

- Summary: `results/nano-lm/wave-ar/abstain_summary.json`  
- Trials: `results/nano-lm/wave-ar/trials/AR-ADVREG-*.json`  
- Contract: `nano_lm/tests/test_abstain.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| ABSTAIN / NO_ANSWER on junk DECODE | Unlabeled garbage answer |
| OOD abstain↑ with FH 0 | LOOKUP-as-IQ · SAFE-as-quality |
| Product honesty gate | mini-AGI claim · Wave AS invent |

Next: **AR2 H-SHIPDEMO** — ship/demo UI shows all four modes.
