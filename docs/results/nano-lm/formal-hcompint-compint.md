# H-COMPINT — BE-FOREVER FH 0 + BA…BD/AZ hold (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §9 BE1 · Session: `.local/wave-be/SESSION.md`  
> Parent: [wave-be-session.md](wave-be-session.md) · Suite: BE0 scoreboard  
> Module: `nano_lm/src/compint_ops.py` · Runner: `npm run nano:compint`

## Hypothesis

Drive BE-FOREVER held-out FH → 0 (type/coercion str→int≠add · paraphrases · type-schema neighbors) via compositional SEMWRAP type/schema gate — not bank stuffing; hold BA…BD-FOREVER + AZ div·sub·BIP FH 0 + a.clear() LOOKUP; live ask scoreboard OK|FP|MISS|ABSTAIN-OK (≥10 novel); modes · p50/p99 · DECODE law

## Gate

| Metric | Result | Bar |
|--------|-------:|-----|
| be_forever_false_hit | **0** (12/12 ABSTAIN) | **0** |
| bd_forever_false_hit | **0** (12/12 ABSTAIN) | **0** |
| ba_forever_false_hit | **0** (15/15 ABSTAIN) | **0** |
| bb_forever_false_hit | **0** (15/15 ABSTAIN) | **0** |
| bc_forever_false_hit | **0** (18/18 ABSTAIN) | **0** |
| az_hold_false_hit | **0** (12/12 ABSTAIN) | **0** |
| overrefuse_miss | **0** (3/3 LOOKUP) | **0** |
| live_ask (OK/FP/MISS+ABSTAIN-OK) | **1/0/0+17** (FP=0) | FP **0** |
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
| PEAK | **0.026270499802194536** | **0.03350129481987096** |
| DECODE | **11.790170501626562** | **13.190018421591958** |
| ABSTAIN | **100.87521150126122** | **245.6522589431554** |

## KB holes

- `open-world chat / unbounded general knowledge`
- `languages beyond Python + Rust (bank scope)`
- `BIPs / RFCs not present in curated+bank golds`
- `math proofs and multi-step symbolic reasoning`
- `live web retrieval / tool-use agency`
- `unlabeled PEAK sold as DECODE IQ (anti-FP)`

## Finding

1. BE-FOREVER (N≥12 · type/coercion str→int≠add · schema neighbors) scored on production `nano:z:ask --wrap --semwrap`.  
2. SEMWRAP compositional type/schema gate (`intent_ask_must_abstain` + contrastive reject) closes str→int→add FP — **not** bank stuffing.  
3. BA…BD-FOREVER hold + AZ hold + over-refuse `a.clear()` LOOKUP held.  
4. Live ask scoreboard OK|FP|MISS|ABSTAIN-OK (prod=eval).  
5. Near-miss BIP-39+SegWit stays ABSTAIN.  
6. DECODE content law holds — usable or ABSTAIN.  
7. Modes + latency + KB republished.  
8. Wall clock ~14.4s · max safe CPU (`cpus-6`).  
9. Generative claim still locked (gen stance **defer once**; H-NANOGEN15; NANOGEN6·7 HOLD · NANOGEN8…14 DEFER).

## Reproduce

```bash
npm run nano:compint
npm run nano:be:session
```

## Artifacts

- Summary: `results/nano-lm/wave-be/compint_summary.json`  
- Contract: `nano_lm/tests/test_compint.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked | Open chat / mini-AGI |
| BE-FOREVER mismatch → ABSTAIN | BD FP as LOOKUP hit · BA+BB+BC PASS with BD FP |
| Exact clear → LOOKUP | Over-refuse as “safe” win |
| Eval path = prod ask path | LOOKUP-as-IQ · pack theater |
| BA+BB+BC PASS ≠ BD forever coverage | Bank stuffing |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; type/coercion wrong-bank LOOKUP = false-hit (str→int→def add); BA…BD forever PASS with BE-FOREVER FP = PACK THEATER; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; type/coercion LOOKUP = false-hit (BE-FOREVER str→int→add); exact-gold ABSTAIN = miss (a.clear()); BA-FOREVER pow·mod·max·sort·len FH must stay 0; BB-FOREVER min·xor·absdiff·and·or FH must stay 0; BC-FOREVER floordiv·neg·gcd·lshift·rshift·nand FH must stay 0; BD-FOREVER reverse≠f-string · mul≠add FH must stay 0; AZ hold div·sub·BIP FH must stay 0; BA…BD PASS with BE FP = PACK THEATER; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = BE5 only under real new method; no NANOGEN15 = NANOGEN14+rename; no CTX/SMART/FAST clone; no invent Wave BF without lab-book reopen; prefer compositional gate over bank stuffing; prefer HOLD/defer over fake PROMOTE

Next: **BE2 H-SHIPUSE** — utilization demo + recipes + paper sync.
