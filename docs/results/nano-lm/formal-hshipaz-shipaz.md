# H-SHIPAZ — modes + content after PRODGEN (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AZ2 · Session: `.local/wave-az/SESSION.md`  
> Parent: [formal-hprodgen-prodgen.md](formal-hprodgen-prodgen.md) · Charter: AZ2 SHIPAZ  
> Module: `nano_lm/src/shipaz_ops.py` · Runner: `npm run nano:shipaz`

## Hypothesis

Hold human ship/demo + ask + apps always show mode=LOOKUP|PEAK|DECODE|ABSTAIN after PRODGEN; content matches mode (DECODE usable or ABSTAIN on junk); hard-natural LOOKUP; held-out FP ABSTAIN; over-refuse clear LOOKUP; named intent ABSTAIN; no unlabeled

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

## Named intent (default ask)

- mode: **ABSTAIN**  
- modeui: `mode=ABSTAIN · wall_ms=0.0000 · n_new=0 · raw=NO_ANSWER`  
- completion: `NO_ANSWER`

## Held-out FP (default ask)

- mode: **ABSTAIN**  
- modeui: `mode=ABSTAIN · wall_ms=0.0000 · n_new=0 · raw=NO_ANSWER`  
- completion: `NO_ANSWER`

## Over-refuse clear (default ask)

- mode: **LOOKUP**  
- modeui: `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP`  
- completion: `a.clear()`

## Near-miss (default ask)

- mode: **ABSTAIN**  
- completion: `NO_ANSWER`

| Modes banner | **LOOKUP · PEAK · DECODE · ABSTAIN** | banner_ok=**True** |
| Charter paths | nano:z:ask, apps ask, ship/demo | — |
| Arms honest | **True** | labeled + content |
| Core modes | **True** | LOOKUP·PEAK·ABSTAIN |
| Decision | **PROMOTE** | smoke + content · no unlabeled |

## Finding

1. Ship/demo arms stay labeled after PRODGEN; content matches mode.  
2. WRAP_DECODE gibberish refuses to ABSTAIN (DECODE content law holds).  
3. Banner still advertises LOOKUP|PEAK|DECODE|ABSTAIN (4/4).  
4. Apps surfaces stay labeled with usable LOOKUP gold.  
5. Near-miss on default ask stays ABSTAIN.  
6. Hard-natural stays labeled LOOKUP on ship path.  
7. Named intent (mul) stays labeled ABSTAIN on ship path.  
8. Held-out FP (div) stays labeled ABSTAIN on ship path.  
9. Over-refuse clear stays labeled LOOKUP `a.clear()`.  
10. Demo card: [shipaz-demo.md](shipaz-demo.md).  
11. Wall ~5.3s · max safe CPU (`cpus-2`).  
12. Generative claim still locked (gen stance **defer**; AZ3 H-NANOGEN10).

## Reproduce

```bash
npm run nano:shipaz
npm run nano:prodgen
```

## Artifacts

- Summary: `results/nano-lm/wave-az/shipaz_summary.json`  
- Demo: [shipaz-demo.md](shipaz-demo.md)  
- Contract: `nano_lm/tests/test_shipaz.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked | Open chat / mini-AGI |
| Mode + content honesty | Unlabeled · LOOKUP-as-IQ |
| Held-out FP → ABSTAIN | Held-out FP as LOOKUP hit |
| Exact clear → LOOKUP | Over-refuse as “safe” win |
| DECODE usable or ABSTAIN | telemetry-only content_ok |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); named-class FH 0 ≠ held-out generalization; intent-mismatch LOOKUP = false-hit; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; intent-mismatch LOOKUP = false-hit (div/sub/wrong-slot held-out); exact-gold ABSTAIN = miss (a.clear()); truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; pack/named FH 0 ≠ held-out coverage; generative bar = AZ3 only under real new method; no NANOGEN10 = NANOGEN9+rename; no CTX/SMART/FAST clone; no invent Wave BA without lab-book reopen; prefer HOLD/defer over fake PROMOTE

Next: **AZ3 H-NANOGEN10** — real new method or HOLD/DEFER (never NANOGEN9+rename).
