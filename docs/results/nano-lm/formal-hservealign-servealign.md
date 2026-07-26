# H-SERVEALIGN — QPFB2+BEAMKV open decode (**DONE** — HOLD)

> Lab: `.local/pesquisa.md` §8.1 AA2 · Wave AA  
> Stack: QT∘**QPFB2** commit on **BEAMKV** shared K=2 · **no wrap**  
> Parent baseline: Z1 mean **1.0** (EARLY n=1 greedy period collapse)

## Hypothesis

Re-open open decode with code-smart serve (QPFB2+BEAMKV), not EARLY n=1 greedy. Gate: HITL mean ≥ Z1+0.5 **or** KILL with evidence; product bar (≥7 / ≤3 errors) required for PROMOTE.

## Gate

| Metric | Result | Rule |
|--------|-------:|------|
| mean score | **3.4** | ≥ 1.5 beats Z1; ≥ 7.0 for PROMOTE |
| errors | **10**/10 | ≤ 3 for PROMOTE |
| beats Z1+0.5 | **yes** (+2.4) | required else KILL |
| pass_bar | **no** | product open-chat bar |
| Decision | **HOLD** | beats Z1; not shippable chat |

## Finding

1. QPFB2+BEAMKV open decode **beats period-collapse Z1** (mean 3.4 vs 1.0) — not identity with EARLY n=1.  
2. Completions still **fail curated golds** (errors 10/10) → **not** an interactive LM.  
3. Product known-ask path remains **H-ZWRAP** + **H-WRAPBANK**.  
4. Do **not** claim SERVEALIGN = open chat; HOLD documents the gap.

## Reproduce

```bash
npm run nano:servealign
```

## Artifacts

- Module: `nano_lm/src/servealign_ops.py` · Runner: `run_servealign.py`
- Summary: `results/nano-lm/wave-aa/servealign_summary.json`
- Trials: `results/nano-lm/wave-aa/trials/AA2-01.json` … `AA2-10.json`
- Contract: `nano_lm/tests/test_servealign.py`

Wave AA remaining optional work: none required (AA2 closed as HOLD).
