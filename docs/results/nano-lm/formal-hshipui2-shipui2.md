# H-SHIPUI2 — modes + DECODE content law (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AV2 · Session: `.local/wave-av/SESSION.md`  
> Parent: [formal-hprodship-prodship.md](formal-hprodship-prodship.md) · Charter: AV2 SHIPUI2  
> Module: `nano_lm/src/shipui2_ops.py` · Runner: `npm run nano:shipui2`

## Hypothesis

Human ship/demo + ask + apps always show mode=LOOKUP|PEAK|DECODE|ABSTAIN; content matches mode (DECODE usable or ABSTAIN on junk); no unlabeled

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

1. Ship/demo arms stay labeled; content matches mode claim.  
2. WRAP_DECODE gibberish refuses to ABSTAIN (closes telemetry-only content_ok).  
3. Banner still advertises LOOKUP|PEAK|DECODE|ABSTAIN (4/4).  
4. Apps surfaces stay labeled with usable LOOKUP gold.  
5. Near-miss on default ask stays ABSTAIN.  
6. Demo card: [shipui2-demo.md](shipui2-demo.md).  
7. Wall ~5.9s · max safe CPU (`cpus-2`).  
8. Generative claim still locked until AV3 H-NANOGEN6.

## Reproduce

```bash
npm run nano:shipui2
npm run nano:prodship
```

## Artifacts

- Summary: `results/nano-lm/wave-av/shipui2_summary.json`  
- Demo: [shipui2-demo.md](shipui2-demo.md)  
- Contract: `nano_lm/tests/test_shipui2.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM | Open chat / mini-AGI |
| Mode + content honesty | Unlabeled · LOOKUP-as-IQ |
| DECODE usable or ABSTAIN | telemetry-only content_ok |
| PEAK usable extractive | Peak-as-open-chat · gibberish PEAK |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); gold-substring / gibberish-tail / truncate-to-span ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = AV3 only; no vanity re-SEMFIX/ADVSAFE unless PRODSHIP fails; no Wave AW invent; no CTX/SMART/FAST clone; no NANOGEN6 = NANOGEN5+rename

Next: **AV3 H-NANOGEN6** — true continue; span-fallback ≠ gen IQ.
