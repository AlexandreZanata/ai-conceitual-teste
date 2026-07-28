# H-REALGAIN — forever FH 0 + AZ hold (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8 BA1 · Session: `.local/wave-ba/SESSION.md`  
> Parent: [wave-ba-session.md](wave-ba-session.md) · Suite: BA0 scoreboard  
> Module: `nano_lm/src/realgain_ops.py` · Runner: `npm run nano:realgain`

## Hypothesis

Drive forever held-out FH → 0 (pow≠add · mod≠add · max≠add · sort≠reverse · len≠junk) via SEMWRAP gate — not bank stuffing; hold AZ div·sub·BIP FH 0 + a.clear() LOOKUP; live ask scoreboard OK|FP|MISS|ABSTAIN-OK; modes · p50/p99 · DECODE law

## Gate

| Metric | Result | Bar |
|--------|-------:|-----|
| forever_false_hit | **0** (15/15 ABSTAIN) | **0** |
| az_hold_false_hit | **0** (12/12 ABSTAIN) | **0** |
| overrefuse_miss | **0** (3/3 LOOKUP) | **0** |
| live_ask (OK/FP/MISS+ABSTAIN-OK) | **1/0/0+4** (FP=0) | FP **0** |
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
| PEAK | **0.02425799539196305** | **0.046144901352818124** |
| DECODE | **10.972698000841774** | **11.99417079849809** |
| ABSTAIN | **98.61733800062211** | **128.33288095869648** |

## KB holes

- `open-world chat / unbounded general knowledge`
- `languages beyond Python + Rust (bank scope)`
- `BIPs / RFCs not present in curated+bank golds`
- `math proofs and multi-step symbolic reasoning`
- `live web retrieval / tool-use agency`
- `unlabeled PEAK sold as DECODE IQ (anti-FP)`

## Finding

1. BA-FOREVER (N≥15 · pow·mod·max·sort·len) scored on production `nano:z:ask --wrap --semwrap`.  
2. SEMWRAP `contrastive_reject` + `intent_ask_must_abstain` close pow→add · mod→add · max→add · sort→reverse · len→junk — **not** bank stuffing.  
3. AZ hold div·sub·BIP FH 0 + over-refuse `a.clear()` LOOKUP held.  
4. Live ask scoreboard OK|FP|MISS|ABSTAIN-OK (prod=eval).  
5. Near-miss BIP-39+SegWit stays ABSTAIN.  
6. DECODE content law holds — usable or ABSTAIN.  
7. Modes + latency + KB republished.  
8. Wall clock ~14.1s · max safe CPU (`cpus-4`).  
9. Generative claim still locked (gen stance **defer**; H-NANOGEN11; NANOGEN6·7 HOLD · NANOGEN8·9·10 DEFER).

## Reproduce

```bash
npm run nano:realgain
npm run nano:ba:session
```

## Artifacts

- Summary: `results/nano-lm/wave-ba/realgain_summary.json`  
- Contract: `nano_lm/tests/test_realgain.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked | Open chat / mini-AGI |
| Forever mismatch → ABSTAIN | Forever FP as LOOKUP hit |
| Exact clear → LOOKUP | Over-refuse as “safe” win |
| Eval path = prod ask path | LOOKUP-as-IQ · pack theater |
| Pack PASS ≠ forever coverage | Bank stuffing |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; intent-mismatch LOOKUP = false-hit (pow/mod/max/sort/len); exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; intent-mismatch LOOKUP = false-hit (BA-FOREVER pow/mod/max/sort/len); exact-gold ABSTAIN = miss (a.clear()); AZ hold div·sub·BIP FH must stay 0; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; pack PASS with forever FP = PACK THEATER; generative bar = BA4 only under real new method; no NANOGEN11 = NANOGEN10+rename; no CTX/SMART/FAST clone; no invent Wave BB without lab-book reopen; prefer HOLD/defer over fake PROMOTE

Next: **BA2 H-FASTREAL** — speed p50/p99 on prod path without FP regress.
