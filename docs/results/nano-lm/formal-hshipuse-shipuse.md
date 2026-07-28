# H-SHIPUSE — Track A utilization (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §9 BE2 · Session: `.local/wave-be/SESSION.md`  
> Parent: [formal-hcompint-compint.md](formal-hcompint-compint.md) · Charter: BE0 Track A  
> Module: `nano_lm/src/shipuse_ops.py` · Runner: `npm run nano:shipuse`

## Hypothesis

Track A utilization: runnable known-ask HITL demo with modes visible; operator card (RECIPES + champion-card) synced; paper claim matches live AF+AQ+AS STRICT refuse stack — no GPT / open-chat unlock

## Gate — demo arms (mode + content)

| Arm | product_mode | content_ok | completion |
|-----|--------------|------------|------------|
| LOOKUP | **LOOKUP** | **True** | `def add(a, b):
    return a + b` |
| PEAK | **PEAK** | **True** | `_Ownership_ is a set of rules that govern how a Rust program manages mem` |
| ABSTAIN | **ABSTAIN** | **True** | `NO_ANSWER` |

## Gate — utilization probes

| Question | product_mode | completion |
|----------|--------------|------------|
| Write a short Python function named add that ret | **LOOKUP** | `def add(a, b):
    return a + b` |
| How do I convert string s to integer in Python? | **ABSTAIN** | `NO_ANSWER` |
| Remove all items from list `a` — one method call | **LOOKUP** | `a.clear()` |
| Who won the 2022 FIFA World Cup? | **ABSTAIN** | `NO_ANSWER` |

## Gate — DECODE path probe

- product_mode: **ABSTAIN**  
- honest: **True**  
- completion: `NO_ANSWER`

## Near-miss

- mode: **ABSTAIN**  
- completion: `NO_ANSWER`

| Modes banner | **LOOKUP · PEAK · DECODE · ABSTAIN** | banner_ok=**True** |
| Operator card | RECIPES + champion-card synced | — |
| Paper build | **True** (`npm run paper:build`) | — |
| Decision | **PROMOTE** | Track A done |

## Finding

1. Known-ask HITL demo labeled LOOKUP on prod wrap path.  
2. BE residual type/coercion ask stays ABSTAIN (H-COMPINT hold).  
3. Over-refuse clear stays LOOKUP; OOD stays ABSTAIN.  
4. Operator card exposes `nano:z:ask --wrap --semwrap` + four modes.  
5. Paper narrative/tex claim = AF+AQ+AS STRICT refuse — no unlock.  
6. `npm run paper:build` ok=**True**.  
7. Wall ~4.8s · max safe CPU (`cpus-6`).  
8. Generative claim still locked (H-NANOGEN15 defer-once stance).

## Reproduce

```bash
npm run nano:shipuse
npm run nano:compint
npm run paper:build
```

## Artifacts

- Summary: `results/nano-lm/wave-be/shipuse_summary.json`  
- Demo: [shipuse-demo.md](shipuse-demo.md)  
- Contract: `nano_lm/tests/test_shipuse.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked | Open chat / mini-AGI unlock |
| Demo + operator + paper sync | Claim/doc drift |
| Modes always visible | Unlabeled answers |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; type/coercion wrong-bank LOOKUP = false-hit (str→int→def add); BA…BD forever PASS with BE-FOREVER FP = PACK THEATER; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; type/coercion LOOKUP = false-hit (BE-FOREVER str→int→add); exact-gold ABSTAIN = miss (a.clear()); BA-FOREVER pow·mod·max·sort·len FH must stay 0; BB-FOREVER min·xor·absdiff·and·or FH must stay 0; BC-FOREVER floordiv·neg·gcd·lshift·rshift·nand FH must stay 0; BD-FOREVER reverse≠f-string · mul≠add FH must stay 0; AZ hold div·sub·BIP FH must stay 0; BA…BD PASS with BE FP = PACK THEATER; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = BE5 only under real new method; no NANOGEN15 = NANOGEN14+rename; no CTX/SMART/FAST clone; no invent Wave BF without lab-book reopen; prefer compositional gate over bank stuffing; prefer HOLD/defer over fake PROMOTE

Next: **BE3 H-FASTBE** — speed p50/p99 hold/improve without FP regress.
