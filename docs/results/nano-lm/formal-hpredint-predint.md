# H-PREDINT — BF-FOREVER FH 0 + BA…BE/AZ hold (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §9 BF1 · Session: `.local/wave-bf/SESSION.md`  
> Parent: [wave-bf-session.md](wave-bf-session.md) · Suite: BE0 scoreboard  
> Module: `nano_lm/src/predint_ops.py` · Runner: `npm run nano:predint`

## Hypothesis

Drive BF-FOREVER held-out FH → 0 (predicate/boolean even≠add · paraphrases · predicate/schema neighbors) via predicate SEMWRAP predicate/schema gate — not bank stuffing; hold BA…BE-FOREVER + AZ div·sub·BIP FH 0 + a.clear() LOOKUP; live ask scoreboard OK|FP|MISS|ABSTAIN-OK (≥10 novel); modes · p50/p99 · DECODE law

## Gate

| Metric | Result | Bar |
|--------|-------:|-----|
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
| PEAK | **0.030583498300984502** | **0.04709640634246169** |
| DECODE | **14.604409501771443** | **16.66161107845255** |
| ABSTAIN | **362.78180600493215** | **830.1813118899008** |

## KB holes

- `open-world chat / unbounded general knowledge`
- `languages beyond Python + Rust (bank scope)`
- `BIPs / RFCs not present in curated+bank golds`
- `math proofs and multi-step symbolic reasoning`
- `live web retrieval / tool-use agency`
- `unlabeled PEAK sold as DECODE IQ (anti-FP)`

## Finding

1. BF-FOREVER (N≥12 · predicate/boolean even≠add · schema neighbors) scored on production `nano:z:ask --wrap --semwrap`.  
2. SEMWRAP predicate predicate/schema gate (`intent_ask_must_abstain` + contrastive reject) closes str→int→add FP — **not** bank stuffing.  
3. BA…BE-FOREVER hold + AZ hold + over-refuse `a.clear()` LOOKUP held.  
4. Live ask scoreboard OK|FP|MISS|ABSTAIN-OK (prod=eval).  
5. Near-miss BIP-39+SegWit stays ABSTAIN.  
6. DECODE content law holds — usable or ABSTAIN.  
7. Modes + latency + KB republished.  
8. Wall clock ~26.4s · max safe CPU (`cpus-6`).  
9. Generative claim still locked (gen stance **SKIP**; H-NANOGEN16 not opened; NANOGEN6·7 HOLD · NANOGEN8…15 DEFER).

## Reproduce

```bash
npm run nano:predint
npm run nano:be:session
```

## Artifacts

- Summary: `results/nano-lm/wave-bf/predint_summary.json`  
- Contract: `nano_lm/tests/test_predint.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked | Open chat / mini-AGI |
| BF-FOREVER mismatch → ABSTAIN | BD FP as LOOKUP hit · BA+BB+BC PASS with BD FP |
| Exact clear → LOOKUP | Over-refuse as “safe” win |
| Eval path = prod ask path | LOOKUP-as-IQ · pack theater |
| BA+BB+BC PASS ≠ BD forever coverage | Bank stuffing |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; predicate/boolean wrong-bank LOOKUP = false-hit (even→def add); BA…BE forever PASS with BF-FOREVER FP = PACK THEATER; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; predicate/boolean LOOKUP = false-hit (BF-FOREVER even→add); type/coercion LOOKUP = false-hit (BE-FOREVER str→int→add); exact-gold ABSTAIN = miss (a.clear()); BA-FOREVER pow·mod·max·sort·len FH must stay 0; BB-FOREVER min·xor·absdiff·and·or FH must stay 0; BC-FOREVER floordiv·neg·gcd·lshift·rshift·nand FH must stay 0; BD-FOREVER reverse≠f-string · mul≠add FH must stay 0; BE-FOREVER str→int / type-coercion FH must stay 0; AZ hold div·sub·BIP FH must stay 0; BA…BE PASS with BF FP = PACK THEATER; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = BF5 only under written method plan; no NANOGEN16 without M1|M2|M3 plan; no CTX/SMART/FAST clone; no invent Wave BG without lab-book reopen; prefer predicate/schema gate over bank stuffing; prefer HOLD/SKIP over fake PROMOTE

Next: **BF2 H-SHIPUSE2** — utilization demo + recipes + paper sync.
