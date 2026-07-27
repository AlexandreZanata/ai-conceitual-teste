# H-SHIPDEMO — four-mode ship/demo (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AR2 · Session: `.local/wave-ar/SESSION.md`  
> Parent: [formal-habstain-abstain.md](formal-habstain-abstain.md) · Charter: [wave-ar-session.md](wave-ar-session.md)  
> Module: `nano_lm/src/shipdemo_ops.py` · Runner: `npm run nano:shipdemo`

## Hypothesis

Every ship/demo answer shows exactly one of `mode=LOOKUP|PEAK|DECODE|ABSTAIN` — never unlabeled.

## Gate

| Arm | product_mode | modeui_line |
|-----|--------------|-------------|
| LOOKUP | **LOOKUP** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |
| PEAK | **PEAK** | `mode=PEAK · wall_ms=0.0238 · n_new=3 · raw=PEAK_FAST+GENBASE` |
| DECODE | **DECODE** | `mode=DECODE · wall_ms=11.4219 · n_new=8 · raw=QT+EARLY n=1` |
| ABSTAIN | **ABSTAIN** | `mode=ABSTAIN · wall_ms=11.4055 · n_new=8 · raw=NO_ANSWER` |

| Modes required | **LOOKUP · PEAK · DECODE · ABSTAIN** | — |
| Decision | **PROMOTE** | — |

## Finding

1. ASK payloads attach `product_mode` + `modeui_line`.  
2. LOOKUP · PEAK · DECODE · ABSTAIN each render a visible mode.  
3. ABSTAIN arm uses H-ABSTAIN refuse-junk on OOD DECODE.  
4. Demo card published at `shipdemo-demo.md`.

## Reproduce

```bash
npm run nano:shipdemo
npm run nano:z:ask -- --wrap --question "Write a short Python function named add that returns the sum of two integers a and b."
npm run nano:abstain
```

## Artifacts

- Summary: `results/nano-lm/wave-ar/shipdemo_summary.json`  
- Demo: [shipdemo-demo.md](shipdemo-demo.md)  
- Contract: `nano_lm/tests/test_shipdemo.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| Labeled LOOKUP/PEAK/DECODE/ABSTAIN UI | Unlabeled answers |
| Mode banner on every ask | LOOKUP sold as DECODE IQ |
| Four-arm smoke | Peak-as-open-chat · mini-AGI claim |

Next: **AR3 H-PARAEXT** — **DONE HOLD** → [formal-hparaext-paraext.md](formal-hparaext-paraext.md). **AR6 AR-DUAL-HITL** — **DONE HOLD** → [wave-ar-dual-hitl.md](wave-ar-dual-hitl.md).
