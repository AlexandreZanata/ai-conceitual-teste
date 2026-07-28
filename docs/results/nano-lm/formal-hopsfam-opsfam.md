# H-OPSFAM — BC-FOREVER FH 0 + BA/BB/AZ hold (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §9 BC1 · Session: `.local/wave-bc/SESSION.md`  
> Parent: [wave-bc-session.md](wave-bc-session.md) · Suite: BC0 scoreboard  
> Module: `nano_lm/src/opsfam_ops.py` · Runner: `npm run nano:opsfam`

## Hypothesis

Drive BC-FOREVER held-out FH → 0 (floordiv≠add · neg≠add · gcd≠add · lshift≠add · rshift≠add · nand≠add) via SEMWRAP family ops/intent gate — not bank stuffing; hold BA-FOREVER + BB-FOREVER + AZ div·sub·BIP FH 0 + a.clear() LOOKUP; live ask scoreboard OK|FP|MISS|ABSTAIN-OK (≥10 novel); modes · p50/p99 · DECODE law

## Gate

| Metric | Result | Bar |
|--------|-------:|-----|
| bc_forever_false_hit | **0** (18/18 ABSTAIN) | **0** |
| ba_forever_false_hit | **0** (15/15 ABSTAIN) | **0** |
| bb_forever_false_hit | **0** (15/15 ABSTAIN) | **0** |
| az_hold_false_hit | **0** (12/12 ABSTAIN) | **0** |
| overrefuse_miss | **0** (3/3 LOOKUP) | **0** |
| live_ask (OK/FP/MISS+ABSTAIN-OK) | **1/0/0+15** (FP=0) | FP **0** |
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
| PEAK | **0.024180499167414382** | **0.02803564857458695** |
| DECODE | **10.862536495551467** | **12.158582682022825** |
| ABSTAIN | **94.97414900033618** | **113.08607884602682** |

## KB holes

- `open-world chat / unbounded general knowledge`
- `languages beyond Python + Rust (bank scope)`
- `BIPs / RFCs not present in curated+bank golds`
- `math proofs and multi-step symbolic reasoning`
- `live web retrieval / tool-use agency`
- `unlabeled PEAK sold as DECODE IQ (anti-FP)`

## Finding

1. BC-FOREVER (N≥18 · floordiv·neg·gcd·lshift·rshift·nand) scored on production `nano:z:ask --wrap --semwrap`.  
2. SEMWRAP `contrastive_reject` + `intent_ask_must_abstain` close floordiv→add · neg→add · gcd→add · lshift→add · rshift→add · nand→add — **not** bank stuffing.  
3. BA-FOREVER + BB-FOREVER hold + AZ hold + over-refuse `a.clear()` LOOKUP held.  
4. Live ask scoreboard OK|FP|MISS|ABSTAIN-OK (prod=eval).  
5. Near-miss BIP-39+SegWit stays ABSTAIN.  
6. DECODE content law holds — usable or ABSTAIN.  
7. Modes + latency + KB republished.  
8. Wall clock ~14.0s · max safe CPU (`cpus-4`).  
9. Generative claim still locked (gen stance **defer**; H-NANOGEN13; NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12 DEFER).

## Reproduce

```bash
npm run nano:opsfam
npm run nano:bc:session
```

## Artifacts

- Summary: `results/nano-lm/wave-bc/opsfam_summary.json`  
- Contract: `nano_lm/tests/test_opsfam.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked | Open chat / mini-AGI |
| BC-FOREVER mismatch → ABSTAIN | BC FP as LOOKUP hit · BA+BB PASS with BC FP |
| Exact clear → LOOKUP | Over-refuse as “safe” win |
| Eval path = prod ask path | LOOKUP-as-IQ · pack theater |
| BA+BB PASS ≠ BC forever coverage | Bank stuffing |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; intent-mismatch LOOKUP = false-hit (floordiv/neg/gcd/lshift/rshift/nand); BA+BB forever PASS with BC-FOREVER FP = PACK THEATER; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; intent-mismatch LOOKUP = false-hit (BC-FOREVER floordiv/neg/gcd/lshift/rshift/nand → add); exact-gold ABSTAIN = miss (a.clear()); BA-FOREVER pow·mod·max·sort·len FH must stay 0; BB-FOREVER min·xor·absdiff·and·or FH must stay 0; AZ hold div·sub·BIP FH must stay 0; BA+BB PASS with BC FP = PACK THEATER; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = BC4 only under real new method; no NANOGEN13 = NANOGEN12+rename; no CTX/SMART/FAST clone; no invent Wave BD without lab-book reopen; prefer HOLD/defer over fake PROMOTE

Next: **BC2 H-FASTLIFT** — speed p50/p99 hold/improve without FP regress.
