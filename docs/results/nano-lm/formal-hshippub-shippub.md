# H-SHIPPUB — Track A++ utilization (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §9 BG2 · Session: `.local/wave-bg/SESSION.md`  
> Parent: [formal-hunaryint-unaryint.md](formal-hunaryint-unaryint.md) · Hold: [formal-hshipuse2-shipuse2.md](formal-hshipuse2-shipuse2.md)  
> Module: `nano_lm/src/shippub_ops.py` · Runner: `npm run nano:shippub`

## Hypothesis

Track A++ utilization: hold H-SHIPUSE2 demo·operator·paper; deepen paper/arXiv sync; live BG residual (abs≠add · upper≠f-string) ABSTAIN + append LOOKUP smoke under H-UNARYINT — no GPT unlock

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
| How do I append x to list a in one Python method | **LOOKUP** | `a.append(x)` |
| How do I convert string s to integer in Python? | **ABSTAIN** | `NO_ANSWER` |
| Write a Python function that returns True if a i | **ABSTAIN** | `NO_ANSWER` |
| Write a Python function that returns the absolut | **ABSTAIN** | `NO_ANSWER` |
| How do I uppercase string s in Python? | **ABSTAIN** | `NO_ANSWER` |
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
| Paper/arXiv sync | **True** | — |
| Decision | **PROMOTE** | Track A++ done |

## Finding

1. Known-ask HITL demo labeled LOOKUP on prod wrap path (H-SHIPUSE2 hold).  
2. BG residual abs/uppercase stays ABSTAIN (H-UNARYINT hold).  
3. BF residual even/predicate stays ABSTAIN; BE type ABSTAIN; append+clear LOOKUP.  
4. OOD stays ABSTAIN; near-miss ABSTAIN.  
5. Operator card exposes ask path + modes + H-UNARYINT.  
6. Paper claim = AF+AQ+AS STRICT refuse — no unlock; arXiv selective-retriever path synced.  
7. `npm run paper:build` ok=**True**.  
8. Wall ~4.8s · max safe CPU (`cpus-4`).  
9. Generative claim still locked (gen stance SKIP; H-NANOGEN17 not opened).

## Reproduce

```bash
npm run nano:shippub
npm run nano:unaryint
npm run paper:build
```

## Artifacts

- Summary: `results/nano-lm/wave-bg/shippub_summary.json`  
- Demo: [shippub-demo.md](shippub-demo.md)  
- Contract: `nano_lm/tests/test_shippub.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked | Open chat / mini-AGI unlock |
| Track A++ deepen + H-SHIPUSE2 hold | Claim/doc drift |
| Modes always visible | Unlabeled answers |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; type/coercion wrong-bank LOOKUP = false-hit (str→int→def add); BA…BD forever PASS with BE-FOREVER FP = PACK THEATER; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; unary/math LOOKUP = false-hit (BG-FOREVER abs/factorial→add); string-transform LOOKUP = false-hit (BG-FOREVER upper→f-string); aggregate/predicate LOOKUP = false-hit (all-truthy→clear); predicate/boolean LOOKUP = false-hit (BF-FOREVER even→add); type/coercion LOOKUP = false-hit (BE-FOREVER str→int→add); exact-gold ABSTAIN = miss (a.clear()); BA-FOREVER pow·mod·max·sort·len FH must stay 0; BB-FOREVER min·xor·absdiff·and·or FH must stay 0; BC-FOREVER floordiv·neg·gcd·lshift·rshift·nand FH must stay 0; BD-FOREVER reverse≠f-string · mul≠add FH must stay 0; BE-FOREVER str→int / type-coercion FH must stay 0; BF-FOREVER even/bool ≠ add FH must stay 0; AZ hold div·sub·BIP FH must stay 0; BA…BF PASS with BG FP = PACK THEATER; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = BG5 only under written method plan; no NANOGEN17 without M1|M2|M3 plan; no CTX/SMART/FAST clone; no invent Wave BH without lab-book reopen; prefer unary/transform/arity gate over bank stuffing; prefer HOLD/SKIP over fake PROMOTE

Next: **BG3 H-FASTBG** — speed p50/p99 hold/improve without FP regress.
