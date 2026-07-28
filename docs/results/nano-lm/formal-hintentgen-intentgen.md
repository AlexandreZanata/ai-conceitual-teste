# H-INTENTGEN — BB-FOREVER FH 0 + BA/AZ hold (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8 BB1 · Session: `.local/wave-bb/SESSION.md`  
> Parent: [wave-bb-session.md](wave-bb-session.md) · Suite: BB0 scoreboard  
> Module: `nano_lm/src/intentgen_ops.py` · Runner: `npm run nano:intentgen`

## Hypothesis

Drive BB-FOREVER held-out FH → 0 (min≠add · xor≠add · absdiff≠add · and≠add · or≠add) via SEMWRAP compositional intent gate — not bank stuffing; hold BA-FOREVER pow·mod·max·sort·len FH 0 + AZ div·sub·BIP FH 0 + a.clear() LOOKUP; live ask scoreboard OK|FP|MISS|ABSTAIN-OK; modes · p50/p99 · DECODE law

## Gate

| Metric | Result | Bar |
|--------|-------:|-----|
| bb_forever_false_hit | **0** (15/15 ABSTAIN) | **0** |
| ba_forever_false_hit | **0** (15/15 ABSTAIN) | **0** |
| az_hold_false_hit | **0** (12/12 ABSTAIN) | **0** |
| overrefuse_miss | **0** (3/3 LOOKUP) | **0** |
| live_ask (OK/FP/MISS+ABSTAIN-OK) | **1/0/0+10** (FP=0) | FP **0** |
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
| PEAK | **0.024296001356560737** | **0.03886515405611134** |
| DECODE | **11.20741750128218** | **12.639104200716247** |
| ABSTAIN | **95.81625450300635** | **196.9088080990333** |

## KB holes

- `open-world chat / unbounded general knowledge`
- `languages beyond Python + Rust (bank scope)`
- `BIPs / RFCs not present in curated+bank golds`
- `math proofs and multi-step symbolic reasoning`
- `live web retrieval / tool-use agency`
- `unlabeled PEAK sold as DECODE IQ (anti-FP)`

## Finding

1. BB-FOREVER (N≥15 · min·xor·absdiff·and·or) scored on production `nano:z:ask --wrap --semwrap`.  
2. SEMWRAP `contrastive_reject` + `intent_ask_must_abstain` close min→add · xor→add · absdiff→add · and→add · or→add — **not** bank stuffing.  
3. BA-FOREVER pow·mod·max·sort·len FH 0 + AZ hold + over-refuse `a.clear()` LOOKUP held.  
4. Live ask scoreboard OK|FP|MISS|ABSTAIN-OK (prod=eval).  
5. Near-miss BIP-39+SegWit stays ABSTAIN.  
6. DECODE content law holds — usable or ABSTAIN.  
7. Modes + latency + KB republished.  
8. Wall clock ~14.7s · max safe CPU (`cpus-6`).  
9. Generative claim still locked (gen stance **defer**; H-NANOGEN12; NANOGEN6·7 HOLD · NANOGEN8·9·10·11 DEFER).

## Reproduce

```bash
npm run nano:intentgen
npm run nano:bb:session
```

## Artifacts

- Summary: `results/nano-lm/wave-bb/intentgen_summary.json`  
- Contract: `nano_lm/tests/test_intentgen.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked | Open chat / mini-AGI |
| BB-FOREVER mismatch → ABSTAIN | BB FP as LOOKUP hit · BA PASS with BB FP |
| Exact clear → LOOKUP | Over-refuse as “safe” win |
| Eval path = prod ask path | LOOKUP-as-IQ · pack theater |
| BA PASS ≠ BB forever coverage | Bank stuffing |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; intent-mismatch LOOKUP = false-hit (min/xor/absdiff/and/or); BA-FOREVER PASS with BB-FOREVER FP = PACK THEATER; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; intent-mismatch LOOKUP = false-hit (BB-FOREVER min/xor/absdiff/and/or → add); exact-gold ABSTAIN = miss (a.clear()); BA-FOREVER pow·mod·max·sort·len FH must stay 0; AZ hold div·sub·BIP FH must stay 0; BA PASS with BB FP = PACK THEATER; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = BB4 only under real new method; no NANOGEN12 = NANOGEN11+rename; no CTX/SMART/FAST clone; no invent Wave BC without lab-book reopen; prefer HOLD/defer over fake PROMOTE

Next: **BB2 H-FASTHOLD** — speed p50/p99 hold/improve without FP regress.
