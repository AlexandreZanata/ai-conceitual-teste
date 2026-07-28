# H-SHIPUX — modes + content after PRODNAT (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AX2 · Session: `.local/wave-ax/SESSION.md`  
> Parent: [formal-hprodnat-prodnat.md](formal-hprodnat-prodnat.md) · Charter: AX2 SHIPUX  
> Module: `nano_lm/src/shipux_ops.py` · Runner: `npm run nano:shipux`

## Hypothesis

Hold human ship/demo + ask + apps always show mode=LOOKUP|PEAK|DECODE|ABSTAIN after PRODNAT; content matches mode (DECODE usable or ABSTAIN on junk); hard-natural ask labeled; no unlabeled

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

## Near-miss (default ask)

- mode: **ABSTAIN**  
- completion: `NO_ANSWER`

| Modes banner | **LOOKUP · PEAK · DECODE · ABSTAIN** | banner_ok=**True** |
| Charter paths | nano:z:ask, apps ask, ship/demo | — |
| Arms honest | **True** | labeled + content |
| Core modes | **True** | LOOKUP·PEAK·ABSTAIN |
| Decision | **PROMOTE** | smoke + content · no unlabeled |

## Finding

1. Ship/demo arms stay labeled after PRODNAT; content matches mode.  
2. WRAP_DECODE gibberish refuses to ABSTAIN (DECODE content law holds).  
3. Banner still advertises LOOKUP|PEAK|DECODE|ABSTAIN (4/4).  
4. Apps surfaces stay labeled with usable LOOKUP gold.  
5. Near-miss on default ask stays ABSTAIN.  
6. Hard-natural live miss stays labeled LOOKUP on ship path.  
7. Demo card: [shipux-demo.md](shipux-demo.md).  
8. Wall ~5.3s · max safe CPU (`cpus-2`).  
9. Generative claim still locked (gen stance **defer**; AX3).

## Reproduce

```bash
npm run nano:shipux
npm run nano:prodnat
```

## Artifacts

- Summary: `results/nano-lm/wave-ax/shipux_summary.json`  
- Demo: [shipux-demo.md](shipux-demo.md)  
- Contract: `nano_lm/tests/test_shipux.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked | Open chat / mini-AGI |
| Mode + content honesty | Unlabeled · LOOKUP-as-IQ |
| DECODE usable or ABSTAIN | telemetry-only content_ok |
| Hard-natural labeled LOOKUP | Pack-para as world coverage |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack/pressure-para ≠ hard natural coverage; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; pack-para ≠ hard natural coverage; generative bar = AX3 only under real new method; no NANOGEN8 = NANOGEN7+rename; no CTX/SMART/FAST clone; no invent Wave AY without lab-book reopen; prefer HOLD/defer over fake PROMOTE

Next: **AX3 H-NANOGEN8** — real new method or HOLD/DEFER (never NANOGEN7+rename).
