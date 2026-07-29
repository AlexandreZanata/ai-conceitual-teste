# H-UNARYINT — BG-FOREVER FH 0 + BA…BF/AZ hold (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §9 BG1 · Session: `.local/wave-bg/SESSION.md`  
> Parent: [wave-bg-session.md](wave-bg-session.md) · Suite: BG0 scoreboard  
> Module: `nano_lm/src/unaryint_ops.py` · Runner: `npm run nano:unaryint`

## Hypothesis

Drive BG-FOREVER held-out FH → 0 (unary/math abs≠add · factorial≠add · string-transform upper≠f-string · aggregate all-truthy≠clear · paraphrases · arity/transform neighbors) via SEMWRAP unary/transform/arity gate — not bank stuffing; hold BA…BF-FOREVER + AZ div·sub·BIP FH 0 + a.clear() LOOKUP; live ask scoreboard OK|FP|MISS|ABSTAIN-OK (≥10 novel); modes · p50/p99 · DECODE law

## Gate

| Metric | Result | Bar |
|--------|-------:|-----|
| bg_forever_false_hit | **0** (12/12 ABSTAIN) | **0** |
| bf_forever_false_hit | **0** (12/12 ABSTAIN) | **0** |
| be_forever_false_hit | **0** (12/12 ABSTAIN) | **0** |
| bd_forever_false_hit | **0** (12/12 ABSTAIN) | **0** |
| ba_forever_false_hit | **0** (15/15 ABSTAIN) | **0** |
| bb_forever_false_hit | **0** (15/15 ABSTAIN) | **0** |
| bc_forever_false_hit | **0** (18/18 ABSTAIN) | **0** |
| az_hold_false_hit | **0** (12/12 ABSTAIN) | **0** |
| overrefuse_miss | **0** (3/3 LOOKUP) | **0** |
| live_ask (OK/FP/MISS+ABSTAIN-OK) | **1/0/0+18** (FP=0) | FP **0** |
| false_hit (near-miss) | **0** | **0** |
| near_miss_ok | **True** (ABSTAIN) | ABSTAIN |
| decode_content_ok | **True** (ABSTAIN) | usable or ABSTAIN |
| peak_ok | **True** (PEAK) | usable or ABSTAIN |
| known_lookup_ok | **True** | True |
| modes_visible | **ABSTAIN · DECODE · LOOKUP · PEAK** (4/4) | LOOKUP·PEAK·DECODE·ABSTAIN |
| kb_coverage_pct | **100.0** | publish + holes |
| Decision | **PROMOTE** | — |

## Latency p50/p99 (republish)

| Path | p50 wall_ms | p99 wall_ms |
|------|------------:|------------:|
| LOOKUP | **0.0** | **0.0** |
| PEAK | **0.027760500415752176** | **0.043207650196563904** |
| DECODE | **12.17199350003284** | **15.593801900558901** |
| ABSTAIN | **109.05569600026865** | **264.78938037014825** |

## KB holes

- `open-world chat / unbounded general knowledge`
- `languages beyond Python + Rust (bank scope)`
- `BIPs / RFCs not present in curated+bank golds`
- `math proofs and multi-step symbolic reasoning`
- `live web retrieval / tool-use agency`
- `unlabeled PEAK sold as DECODE IQ (anti-FP)`

## Finding

1. BG-FOREVER (N≥12 · unary/math abs≠add · factorial≠add · string-transform upper≠f-string · aggregate all-truthy≠clear) scored on production `nano:z:ask --wrap --semwrap`.  
2. SEMWRAP unary/transform/arity gate (`intent_ask_must_abstain` + contrastive reject) closes class FP — **not** bank stuffing.  
3. BA…BF-FOREVER hold + AZ hold + over-refuse `a.clear()` LOOKUP held.  
4. Live ask scoreboard OK|FP|MISS|ABSTAIN-OK (prod=eval).  
5. Near-miss BIP-39+SegWit stays ABSTAIN.  
6. DECODE content law holds — usable or ABSTAIN.  
7. Modes + latency + KB republished.  
8. Wall clock ~15.4s · max safe CPU (`cpus-4`).  
9. Generative claim still locked (gen stance **SKIP**; H-NANOGEN17; NANOGEN6·7 HOLD · NANOGEN8…15 DEFER · NANOGEN16 SKIP).

## Reproduce

```bash
npm run nano:unaryint
npm run nano:bg:session
```

## Artifacts

- Summary: `results/nano-lm/wave-bg/unaryint_summary.json`  
- Contract: `nano_lm/tests/test_unaryint.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked | Open chat / mini-AGI |
| BG-FOREVER mismatch → ABSTAIN | Unary/transform FP as LOOKUP · BA…BF PASS with BG FP |
| Exact clear → LOOKUP | Over-refuse as “safe” win |
| Eval path = prod ask path | LOOKUP-as-IQ · pack theater |
| BA…BF PASS ≠ BG forever coverage | Bank stuffing |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; unary/math/string-transform wrong-bank LOOKUP = false-hit (abs→def add · upper→f-string · all-truthy→clear); BA…BF forever PASS with BG-FOREVER FP = PACK THEATER; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; unary/math LOOKUP = false-hit (BG-FOREVER abs/factorial→add); string-transform LOOKUP = false-hit (BG-FOREVER upper→f-string); aggregate/predicate LOOKUP = false-hit (all-truthy→clear); predicate/boolean LOOKUP = false-hit (BF-FOREVER even→add); type/coercion LOOKUP = false-hit (BE-FOREVER str→int→add); exact-gold ABSTAIN = miss (a.clear()); BA-FOREVER pow·mod·max·sort·len FH must stay 0; BB-FOREVER min·xor·absdiff·and·or FH must stay 0; BC-FOREVER floordiv·neg·gcd·lshift·rshift·nand FH must stay 0; BD-FOREVER reverse≠f-string · mul≠add FH must stay 0; BE-FOREVER str→int / type-coercion FH must stay 0; BF-FOREVER even/bool ≠ add FH must stay 0; AZ hold div·sub·BIP FH must stay 0; BA…BF PASS with BG FP = PACK THEATER; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = BG5 only under written method plan; no NANOGEN17 without M1|M2|M3 plan; no CTX/SMART/FAST clone; no invent Wave BH without lab-book reopen; prefer unary/transform/arity gate over bank stuffing; prefer HOLD/SKIP over fake PROMOTE

Next: **BG2 H-SHIPPUB** — utilization++ + paper/arXiv sync + live smoke.
