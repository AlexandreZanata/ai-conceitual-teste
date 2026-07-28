# H-SHIPAY — modes + content after PRODINT (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AY2 · Session: `.local/wave-ay/SESSION.md`  
> Parent: [formal-hprodint-prodint.md](formal-hprodint-prodint.md) · Charter: AY2 SHIPAY  
> Module: `nano_lm/src/shipay_ops.py` · Runner: `npm run nano:shipay`

## Hypothesis

Hold human ship/demo + ask + apps always show mode=LOOKUP|PEAK|DECODE|ABSTAIN after PRODINT; content matches mode (DECODE usable or ABSTAIN on junk); hard-natural LOOKUP; intent-FP ABSTAIN labeled; no unlabeled

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

## Hard-natural (default ask)

- mode: **LOOKUP**  
- modeui: `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=SEMWRAP_LOOKUP`  
- completion: `def add(a, b):
    return a + b`

## Intent-FP (default ask)

- mode: **ABSTAIN**  
- modeui: `mode=ABSTAIN · wall_ms=0.0000 · n_new=0 · raw=NO_ANSWER`  
- completion: `NO_ANSWER`

## Near-miss (default ask)

- mode: **ABSTAIN**  
- completion: `NO_ANSWER`

| Modes banner | **LOOKUP · PEAK · DECODE · ABSTAIN** | banner_ok=**True** |
| Charter paths | nano:z:ask, apps ask, ship/demo | — |
| Arms honest | **True** | labeled + content |
| Core modes | **True** | LOOKUP·PEAK·ABSTAIN |
| Decision | **PROMOTE** | smoke + content · no unlabeled |

## Finding

1. Ship/demo arms stay labeled after PRODINT; content matches mode.  
2. WRAP_DECODE gibberish refuses to ABSTAIN (DECODE content law holds).  
3. Banner still advertises LOOKUP|PEAK|DECODE|ABSTAIN (4/4).  
4. Apps surfaces stay labeled with usable LOOKUP gold.  
5. Near-miss on default ask stays ABSTAIN.  
6. Hard-natural stays labeled LOOKUP on ship path.  
7. Intent-FP (mul) stays labeled ABSTAIN on ship path.  
8. Demo card: [shipay-demo.md](shipay-demo.md).  
9. Wall ~5.3s · max safe CPU (`cpus-2`).  
10. Generative claim still locked (gen stance **defer**; AY3 H-NANOGEN9).

## Reproduce

```bash
npm run nano:shipay
npm run nano:prodint
```

## Artifacts

- Summary: `results/nano-lm/wave-ay/shipay_summary.json`  
- Demo: [shipay-demo.md](shipay-demo.md)  
- Contract: `nano_lm/tests/test_shipay.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked | Open chat / mini-AGI |
| Mode + content honesty | Unlabeled · LOOKUP-as-IQ |
| Intent-FP → ABSTAIN | Intent-mismatch as LOOKUP hit |
| DECODE usable or ABSTAIN | telemetry-only content_ok |
| Hard-natural labeled LOOKUP | Pack FH as live intent coverage |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ live intent/adversary coverage; intent-mismatch LOOKUP = false-hit; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; intent-mismatch LOOKUP = false-hit (mul/diff/remove/half-known); truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; pack FH 0 ≠ live intent coverage; generative bar = AY3 only under real new method; no NANOGEN9 = NANOGEN8+rename; no CTX/SMART/FAST clone; no invent Wave AZ without lab-book reopen; prefer HOLD/defer over fake PROMOTE

Next: **AY3 H-NANOGEN9** — real new method or HOLD/DEFER (never NANOGEN8+rename).
