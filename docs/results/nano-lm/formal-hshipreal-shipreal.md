# H-SHIPREAL — modes + content bars (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AU2 · Session: `.local/wave-au/SESSION.md`  
> Parent: [formal-hprodhard-prodhard.md](formal-hprodhard-prodhard.md) · Charter: AU2 SHIPREAL  
> Module: `nano_lm/src/shipreal_ops.py` · Runner: `npm run nano:shipreal`

## Hypothesis

Human ship/demo + ask + apps always show mode=LOOKUP|PEAK|DECODE|ABSTAIN; answers match mode claim (content bars); no unlabeled

## Gate — ship/demo arms (mode + content)

| Arm | product_mode | content_ok | completion |
|-----|--------------|------------|------------|
| LOOKUP | **LOOKUP** | **True** | `def add(a, b):
    return a + b` |
| PEAK | **PEAK** | **True** | `_Ownership_ is a set of rules that govern how a Rust program manages mem` |
| DECODE | **DECODE** | **True** | `! followed at everything really have
. looking just something�. another ` |
| ABSTAIN | **ABSTAIN** | **True** | `NO_ANSWER` |

## Gate — apps ask

| app_id | product_mode | modeui_line |
|--------|--------------|-------------|
| known-ask | **LOOKUP** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |
| howto | **LOOKUP** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |
| long-doc | **LOOKUP** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |

## Near-miss (default ask)

- mode: **ABSTAIN**  
- completion: `NO_ANSWER`

| Modes required | **LOOKUP · PEAK · DECODE · ABSTAIN** | — |
| Charter paths | nano:z:ask, apps ask, ship/demo | — |
| Content bars | **True** | match mode claim |
| Decision | **PROMOTE** | 4/4 · content · no unlabeled |

## Finding

1. Ship/demo four-arm smoke keeps LOOKUP · PEAK · DECODE · ABSTAIN visible.  
2. Each arm completion matches its mode claim (content bars).  
3. Apps surfaces stay labeled; known-ask LOOKUP carries usable gold.  
4. Near-miss on default ask stays ABSTAIN (AU1 hold).  
5. Demo card: [shipreal-demo.md](shipreal-demo.md).  
6. Wall ~5.3s · max safe CPU (`cpus-2`).  
7. Generative claim still locked until AU3 H-NANOGEN5.

## Reproduce

```bash
npm run nano:shipreal
npm run nano:prodhard
```

## Artifacts

- Summary: `results/nano-lm/wave-au/shipreal_summary.json`  
- Demo: [shipreal-demo.md](shipreal-demo.md)  
- Contract: `nano_lm/tests/test_shipreal.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix) — not unlabeled open chat LM | Open chat / mini-AGI |
| Mode + content honesty | Unlabeled · LOOKUP-as-IQ |
| PEAK usable extractive | Peak-as-open-chat · gibberish PEAK |

Next: **AU3 H-NANOGEN5** — strict ablated generative gate.
