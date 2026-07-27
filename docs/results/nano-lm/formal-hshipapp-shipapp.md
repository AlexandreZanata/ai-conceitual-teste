# H-SHIPAPP — human ask/apps/ship-demo modes (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AT2 · Session: `.local/wave-at/SESSION.md`  
> Parent: [formal-hprodreg-prodreg.md](formal-hprodreg-prodreg.md) · Charter: AT0 SHIPAPP  
> Module: `nano_lm/src/shipapp_ops.py` · Runner: `npm run nano:shipapp`

## Hypothesis

Human-facing nano:z:ask · apps ask · ship/demo always show mode=LOOKUP|PEAK|DECODE|ABSTAIN (4/4); no unlabeled answer

## Gate — ship/demo arms

| Arm | product_mode | modeui_line |
|-----|--------------|-------------|
| LOOKUP | **LOOKUP** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |
| PEAK | **PEAK** | `mode=PEAK · wall_ms=0.0281 · n_new=3 · raw=PEAK_FAST+GENBASE` |
| DECODE | **DECODE** | `mode=DECODE · wall_ms=213.9937 · n_new=8 · raw=QT+EARLY n=1` |
| ABSTAIN | **ABSTAIN** | `mode=ABSTAIN · wall_ms=399.1223 · n_new=64 · raw=NO_ANSWER` |

## Gate — apps ask

| app_id | product_mode | modeui_line |
|--------|--------------|-------------|
| known-ask | **LOOKUP** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |
| howto | **LOOKUP** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |
| long-doc | **LOOKUP** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |

| Modes required | **LOOKUP · PEAK · DECODE · ABSTAIN** | — |
| Charter paths | nano:z:ask, apps ask, ship/demo | — |
| Decision | **PROMOTE** | 4/4 · apps labeled |

## Finding

1. `nano:z:ask` default path keeps LOOKUP + ABSTAIN banners.  
2. Ship/demo four-arm smoke shows LOOKUP · PEAK · DECODE · ABSTAIN.  
3. Apps surfaces (known-ask, howto, long-doc) each emit `modeui_line`.  
4. Demo card: [shipapp-demo.md](shipapp-demo.md).  
5. Wall ~4.2s · max safe CPU (`cpus-2`); AS SHIPUI formal stays frozen.

## Reproduce

```bash
npm run nano:shipapp
npm run nano:z:ask -- --wrap --question "Write a short Python function named add that returns the sum of two integers a and b."
npm run nano:z:ask -- --semwrap --question "Which nation hosted the 2016 Summer Olympics?"
```

## Artifacts

- Summary: `results/nano-lm/wave-at/shipapp_summary.json`  
- Demo: [shipapp-demo.md](shipapp-demo.md)  
- Contract: `nano_lm/tests/test_shipapp.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path — not open chat LM | Open chat / mini-AGI |
| Labeled modes on ask · apps · ship/demo | Unlabeled answers |
| PEAK labeled extractive | Peak-as-open-chat |

Next: **AT3 H-NANOGEN4** — ablated DECODE ≥ **5.0** vs NANOGEN3 4.3.
