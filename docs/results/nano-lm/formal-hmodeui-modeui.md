# H-MODEUI — mode-visible ship/demo (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AQ5 · Session: `.local/wave-aq/SESSION.md`  
> Parent: [formal-hkbcov-kbcov.md](formal-hkbcov-kbcov.md) · Charter: [wave-aq-session.md](wave-aq-session.md)  
> Module: `nano_lm/src/modeui_ops.py` · Runner: `npm run nano:modeui`

## Hypothesis

Every ship/demo answer shows exactly one of `mode=LOOKUP|PEAK|DECODE` — never unlabeled.

## Gate

| Arm | product_mode | modeui_line |
|-----|--------------|-------------|
| LOOKUP | **LOOKUP** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |
| PEAK | **PEAK** | `mode=PEAK · wall_ms=0.0251 · n_new=3 · raw=PEAK_FAST+GENBASE` |
| DECODE | **DECODE** | `mode=DECODE · wall_ms=154.6275 · n_new=8 · raw=QT+EARLY n=1` |

| Modes required | **LOOKUP · PEAK · DECODE** | — |
| Decision | **PROMOTE** | — |

## Finding

1. ASK payloads attach `product_mode` + `modeui_line`.  
2. LOOKUP · PEAK · DECODE smokes each render a visible mode.  
3. Demo card published at `modeui-demo.md`.

## Reproduce

```bash
npm run nano:modeui
npm run nano:z:ask -- --wrap --question "Write a short Python function named add that returns the sum of two integers a and b."
npm run nano:z:ask -- --question "Explain Merkle trees briefly"
```

## Artifacts

- Summary: `results/nano-lm/wave-aq/modeui_summary.json`  
- Demo: [modeui-demo.md](modeui-demo.md)  
- Contract: `nano_lm/tests/test_modeui.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| Labeled LOOKUP/PEAK/DECODE UI | Unlabeled answers |
| Mode banner on every ask | LOOKUP sold as DECODE IQ |
| Three-arm smoke | Peak-as-open-chat |

Next: **AQ6 H-NANOGEN** — **DONE HOLD** → [formal-hnanogen-nanogen.md](formal-hnanogen-nanogen.md).
