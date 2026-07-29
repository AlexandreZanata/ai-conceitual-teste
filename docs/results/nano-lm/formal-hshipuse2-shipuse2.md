# H-SHIPUSE2 — Track A+ utilization (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §9 BF2 · Session: `.local/wave-bf/SESSION.md`  
> Parent: [formal-hpredint-predint.md](formal-hpredint-predint.md) · Hold: [formal-hshipuse-shipuse.md](formal-hshipuse-shipuse.md)  
> Module: `nano_lm/src/shipuse2_ops.py` · Runner: `npm run nano:shipuse2`

## Hypothesis

Track A+ utilization deepen: hold H-SHIPUSE demo·operator·paper; live BF residual (even≠add) ABSTAIN + append LOOKUP smoke; operator path + paper claim sync under H-PREDINT — no GPT unlock

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
| Decision | **PROMOTE** | Track A+ done |

## Finding

1. Known-ask HITL demo labeled LOOKUP on prod wrap path (H-SHIPUSE hold).  
2. BF residual even/predicate stays ABSTAIN (H-PREDINT hold).  
3. BE residual type/coercion stays ABSTAIN; append+clear LOOKUP.  
4. OOD stays ABSTAIN; near-miss ABSTAIN.  
5. Operator card exposes ask path + modes + H-PREDINT.  
6. Paper claim = AF+AQ+AS STRICT refuse — no unlock.  
7. `npm run paper:build` ok=**True**.  
8. Wall ~4.9s · max safe CPU (`cpus-6`).  
9. Generative claim still locked (gen stance SKIP; H-NANOGEN16 not opened).

## Reproduce

```bash
npm run nano:shipuse2
npm run nano:predint
npm run paper:build
```

## Artifacts

- Summary: `results/nano-lm/wave-bf/shipuse2_summary.json`  
- Demo: [shipuse2-demo.md](shipuse2-demo.md)  
- Contract: `nano_lm/tests/test_shipuse2.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked | Open chat / mini-AGI unlock |
| Track A+ deepen + H-SHIPUSE hold | Claim/doc drift |
| Modes always visible | Unlabeled answers |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; type/coercion wrong-bank LOOKUP = false-hit (str→int→def add); BA…BD forever PASS with BE-FOREVER FP = PACK THEATER; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; predicate/boolean LOOKUP = false-hit (BF-FOREVER even→add); type/coercion LOOKUP = false-hit (BE-FOREVER str→int→add); exact-gold ABSTAIN = miss (a.clear()); BA-FOREVER pow·mod·max·sort·len FH must stay 0; BB-FOREVER min·xor·absdiff·and·or FH must stay 0; BC-FOREVER floordiv·neg·gcd·lshift·rshift·nand FH must stay 0; BD-FOREVER reverse≠f-string · mul≠add FH must stay 0; BE-FOREVER str→int / type-coercion FH must stay 0; AZ hold div·sub·BIP FH must stay 0; BA…BE PASS with BF FP = PACK THEATER; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = BF5 only under written method plan; no NANOGEN16 without M1|M2|M3 plan; no CTX/SMART/FAST clone; no invent Wave BG without lab-book reopen; prefer predicate/schema gate over bank stuffing; prefer HOLD/SKIP over fake PROMOTE

Next: **BF3 H-FASTBF** — speed p50/p99 hold/improve without FP regress.
