# H-SHIPUI — mode-visible ask + ship/demo (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AS6 · Session: `.local/wave-as/SESSION.md`  
> Parent: [formal-hmetrics-metrics.md](formal-hmetrics-metrics.md) · Prior: [formal-hshipdemo-shipdemo.md](formal-hshipdemo-shipdemo.md)  
> Module: `nano_lm/src/shipui_ops.py` · Runner: `npm run nano:shipui`

## Hypothesis

After ASKABSTAIN on the **default** ask path, every ship/demo and ask answer shows exactly one of `mode=LOOKUP|PEAK|DECODE|ABSTAIN` — never unlabeled.

## Gate

| Arm | product_mode | modeui_line |
|-----|--------------|-------------|
| LOOKUP | **LOOKUP** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |
| PEAK | **PEAK** | `mode=PEAK · wall_ms=0.0228 · n_new=3 · raw=PEAK_FAST+GENBASE` |
| DECODE | **DECODE** | `mode=DECODE · wall_ms=158.2723 · n_new=8 · raw=QT+EARLY n=1` |
| ABSTAIN | **ABSTAIN** | `mode=ABSTAIN · wall_ms=144.1404 · n_new=64 · raw=NO_ANSWER` |

| Modes required | **LOOKUP · PEAK · DECODE · ABSTAIN** | — |
| Decision | **PROMOTE** | 4/4 visible · no unlabeled |

## Finding

1. Default `nano:z:ask` already emits `product_mode` + `modeui_line` (ASKABSTAIN + MODEUI).  
2. LOOKUP · PEAK · DECODE · ABSTAIN each render a visible mode.  
3. ABSTAIN arm uses default-path refuse-junk on OOD (not runner-only).  
4. Demo card published at `shipui-demo.md`.  
5. AR H-SHIPDEMO stays locked; AS6 re-validates after ask-path changes.

## Reproduce

```bash
npm run nano:shipui
npm run nano:z:ask -- --wrap --question "Write a short Python function named add that returns the sum of two integers a and b."
npm run nano:z:ask -- --semwrap --question "Which nation hosted the 2016 Summer Olympics?"
```

## Artifacts

- Summary: `results/nano-lm/wave-as/shipui_summary.json`  
- Demo: [shipui-demo.md](shipui-demo.md)  
- Contract: `nano_lm/tests/test_shipui.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| Labeled LOOKUP/PEAK/DECODE/ABSTAIN UI | Unlabeled answers |
| Mode banner on default ask | Runner-only abstain theater |
| Four-arm smoke 4/4 | Peak-as-open-chat · mini-AGI claim |

Next: **AS7 H-NANOGEN3** — **DONE HOLD** → [formal-hnanogen3-nanogen3.md](formal-hnanogen3-nanogen3.md) (ablated **4.3**).
