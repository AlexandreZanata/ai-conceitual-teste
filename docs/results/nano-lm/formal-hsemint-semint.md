# H-SEMINT — BD-FOREVER FH 0 + BA/BB/BC/AZ hold (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §9 BD1 · Session: `.local/wave-bd/SESSION.md`  
> Parent: [wave-bd-session.md](wave-bd-session.md) · Suite: BD0 scoreboard  
> Module: `nano_lm/src/semint_ops.py` · Runner: `npm run nano:semint`

## Hypothesis

Drive BD-FOREVER held-out FH → 0 (reverse≠f-string · mul≠add · wrong-bank neighbors) via SEMWRAP semantic intent gate — not bank stuffing; hold BA-FOREVER + BB-FOREVER + BC-FOREVER + AZ div·sub·BIP FH 0 + a.clear() LOOKUP; live ask scoreboard OK|FP|MISS|ABSTAIN-OK (≥10 novel); modes · p50/p99 · DECODE law

## Gate

| Metric | Result | Bar |
|--------|-------:|-----|
| bd_forever_false_hit | **0** (12/12 ABSTAIN) | **0** |
| ba_forever_false_hit | **0** (15/15 ABSTAIN) | **0** |
| bb_forever_false_hit | **0** (15/15 ABSTAIN) | **0** |
| bc_forever_false_hit | **0** (18/18 ABSTAIN) | **0** |
| az_hold_false_hit | **0** (12/12 ABSTAIN) | **0** |
| overrefuse_miss | **0** (3/3 LOOKUP) | **0** |
| live_ask (OK/FP/MISS+ABSTAIN-OK) | **1/0/0+16** (FP=0) | FP **0** |
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
| PEAK | **0.028152004233561456** | **0.03572350324247962** |
| DECODE | **11.02755099782371** | **13.08165011309029** |
| ABSTAIN | **95.06595800121431** | **215.32104923200697** |

## KB holes

- `open-world chat / unbounded general knowledge`
- `languages beyond Python + Rust (bank scope)`
- `BIPs / RFCs not present in curated+bank golds`
- `math proofs and multi-step symbolic reasoning`
- `live web retrieval / tool-use agency`
- `unlabeled PEAK sold as DECODE IQ (anti-FP)`

## Finding

1. BD-FOREVER (N≥12 · reverse≠f-string · mul≠add · wrong-bank) scored on production `nano:z:ask --wrap --semwrap`.  
2. SEMWRAP `contrastive_reject` + `intent_ask_must_abstain` close reverse→f-string · mul→add · wrong-bank neighbors — **not** bank stuffing.  
3. BA-FOREVER + BB-FOREVER + BC-FOREVER hold + AZ hold + over-refuse `a.clear()` LOOKUP held.  
4. Live ask scoreboard OK|FP|MISS|ABSTAIN-OK (prod=eval).  
5. Near-miss BIP-39+SegWit stays ABSTAIN.  
6. DECODE content law holds — usable or ABSTAIN.  
7. Modes + latency + KB republished.  
8. Wall clock ~13.9s · max safe CPU (`cpus-4`).  
9. Generative claim still locked (gen stance **defer**; H-NANOGEN14; NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12·13 DEFER).

## Reproduce

```bash
npm run nano:semint
npm run nano:bd:session
```

## Artifacts

- Summary: `results/nano-lm/wave-bd/semint_summary.json`  
- Contract: `nano_lm/tests/test_semint.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked | Open chat / mini-AGI |
| BD-FOREVER mismatch → ABSTAIN | BD FP as LOOKUP hit · BA+BB+BC PASS with BD FP |
| Exact clear → LOOKUP | Over-refuse as “safe” win |
| Eval path = prod ask path | LOOKUP-as-IQ · pack theater |
| BA+BB+BC PASS ≠ BD forever coverage | Bank stuffing |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; semantic wrong-bank LOOKUP = false-hit (reverse→f-string · mul→add); BA+BB+BC forever PASS with BD-FOREVER FP = PACK THEATER; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; semantic wrong-bank LOOKUP = false-hit (BD-FOREVER reverse→f-string / mul→add); exact-gold ABSTAIN = miss (a.clear()); BA-FOREVER pow·mod·max·sort·len FH must stay 0; BB-FOREVER min·xor·absdiff·and·or FH must stay 0; BC-FOREVER floordiv·neg·gcd·lshift·rshift·nand FH must stay 0; AZ hold div·sub·BIP FH must stay 0; BA+BB+BC PASS with BD FP = PACK THEATER; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = BD4 only under real new method; no NANOGEN14 = NANOGEN13+rename; no CTX/SMART/FAST clone; no invent Wave BE without lab-book reopen; prefer HOLD/defer over fake PROMOTE

Next: **BD2 H-FASTGAIN** — speed p50/p99 hold/improve without FP regress.
