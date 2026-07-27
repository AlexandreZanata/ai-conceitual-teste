# H-SHIPKEEP — modes + DECODE keep (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §2 AW2 · Session: `.local/wave-aw/SESSION.md`  
> Parent: [formal-hprodkeep-prodkeep.md](formal-hprodkeep-prodkeep.md) · Charter: AW2 SHIPKEEP  
> Module: `nano_lm/src/shipkeep_ops.py` · Runner: `npm run nano:shipkeep`

## Hypothesis

Hold human ship/demo + ask + apps always show mode=LOOKUP|PEAK|DECODE|ABSTAIN after PRODKEEP; content matches mode (DECODE usable or ABSTAIN on junk); no unlabeled

## Gate — ship/demo arms (mode + content)

| Arm | product_mode | content_ok | completion |
|-----|--------------|------------|------------|
| LOOKUP | **LOOKUP** | **True** | `def add(a, b):
    return a + b` |
| PEAK | **PEAK** | **True** | `_Ownership_ is a set of rules that govern how a Rust program manages mem` |
| ABSTAIN | **ABSTAIN** | **True** | `NO_ANSWER` |

## Gate — DECODE path probe

- product_mode: **ABSTAIN**  
- honest: **True**  
- completion: `NO_ANSWER`

## Gate — apps ask

| app_id | product_mode | modeui_line |
|--------|--------------|-------------|
| known-ask | **LOOKUP** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |
| howto | **LOOKUP** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |
| long-doc | **LOOKUP** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |

## Near-miss (default ask)

- mode: **ABSTAIN**  
- completion: `NO_ANSWER`

| Modes banner | **LOOKUP · PEAK · DECODE · ABSTAIN** | banner_ok=**True** |
| Charter paths | nano:z:ask, apps ask, ship/demo | — |
| Arms honest | **True** | labeled + content |
| Core modes | **True** | LOOKUP·PEAK·ABSTAIN |
| Decision | **PROMOTE** | smoke + content · no unlabeled |

## Finding

1. Ship/demo arms stay labeled after PRODKEEP; content matches mode.  
2. WRAP_DECODE gibberish refuses to ABSTAIN (DECODE content law holds).  
3. Banner still advertises LOOKUP|PEAK|DECODE|ABSTAIN (4/4).  
4. Apps surfaces stay labeled with usable LOOKUP gold.  
5. Near-miss on default ask stays ABSTAIN.  
6. Pressure-para default ask stays labeled (keep under AW pack).  
7. Demo card: [shipkeep-demo.md](shipkeep-demo.md).  
8. Wall ~5.5s · max safe CPU (`cpus-2`).  
9. Generative claim still locked until AW3 H-NANOGEN7 TAC.

## Reproduce

```bash
npm run nano:shipkeep
npm run nano:prodkeep
```

## Artifacts

- Summary: `results/nano-lm/wave-aw/shipkeep_summary.json`  
- Demo: [shipkeep-demo.md](shipkeep-demo.md)  
- Contract: `nano_lm/tests/test_shipkeep.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM | Open chat / mini-AGI |
| Mode + content honesty | Unlabeled · LOOKUP-as-IQ |
| DECODE usable or ABSTAIN | telemetry-only content_ok |
| PEAK usable extractive | Peak-as-open-chat · gibberish PEAK |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); gold-substring / gibberish-tail / truncate-to-span ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = AW3 only; no vanity re-SEMFIX/ADVSAFE unless PRODKEEP fails; no Wave AX invent; no CTX/SMART/FAST clone; no NANOGEN7 = NANOGEN6+rename; TAC ≠ refuse-or-continue clone

Next: **AW3 H-NANOGEN7** — **DONE HOLD** (`npm run nano:nanogen7`) · **AW4 AW-REAL-EVAL** — **DONE PROMOTE** (`npm run nano:aw:real-eval`) · next **AW5 AW-REPORT**.
