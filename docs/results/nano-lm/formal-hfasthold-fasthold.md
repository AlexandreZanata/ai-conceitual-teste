# H-FASTHOLD (BB2) — prod p50/p99 + anti-FP hold (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 · §8 BB2 · Session: `.local/wave-bb/SESSION.md`  
> Parent: [formal-hintentgen-intentgen.md](formal-hintentgen-intentgen.md) · BB0 speed baseline (= BA H-FASTREAL)  
> Module: `nano_lm/src/bb_fasthold_ops.py` · Runner: `npm run nano:bb:fasthold`  
> **Not** BA [formal-hfastreal-ba2.md](formal-hfastreal-ba2.md) (`npm run nano:ba:fastreal`) · **Not** AG [formal-hfastreal-fastreal.md](formal-hfastreal-fastreal.md) (`npm run nano:fastreal`)

## Hypothesis

Hold/improve prod-ask p50/p99 for LOOKUP·PEAK·DECODE·ABSTAIN; PROMOTE only if §1 anti-FP holds (BB-FOREVER FH 0 · BA-FOREVER hold · AZ hold · over-refuse 0 · live FP 0) and live p99 does not regress vs BB0/BA-FASTREAL baseline — never warm-cache vanity; LOOKUP wall=0 ≠ speed IQ; sub-ms PEAK walls ≠ speed IQ; ≠ BA H-FASTREAL rename · ≠ AG H-FASTREAL archive

## Gate

| Metric | Result | Bar |
|--------|-------:|-----|
| bb_forever_false_hit | **0** (15/15) | **0** |
| ba_forever_false_hit | **0** (15/15) | **0** |
| az_hold_false_hit | **0** (12/12) | **0** |
| overrefuse_miss | **0** (3/3) | **0** |
| live_fp | **0** | **0** |
| p99_regress | **False** ([]) | false (≤1.5× BB0/BA-FASTREAL) |
| modes_visible | **ABSTAIN · DECODE · LOOKUP · PEAK** (4/4) | 4/4 |
| Decision | **PROMOTE** | — |

## Latency p50/p99 (prod ask path)

| Path | p50 wall_ms | p99 wall_ms | n |
|------|------------:|------------:|--:|
| LOOKUP | **0.0** | **0.0** | 64 |
| PEAK | **0.009229501301888376** | **0.02309217110450848** | 128 |
| DECODE | **10.989629001414869** | **12.43256526067853** | 12 |
| ABSTAIN | **94.12569499909296** | **121.80530938683661** | 32 |

Samples: LOOKUP=64 · PEAK=128 · DECODE=12 · ABSTAIN=32

## Finding

1. Prod-path tetrad measured under max safe CPU (`cpus-6`, workers≤6).  
2. LOOKUP wall=0 **and** sub-ms PEAK walls **not** sold as speed IQ (regress gate uses base p99 ≥1ms).  
3. INTENTGEN anti-FP hold: BB FH 0 · BA FH 0 · AZ hold · over-refuse 0 · live FP 0.  
4. Live product p99 (DECODE·ABSTAIN) checked vs BB0/BA-FASTREAL (max ratio 1.5).  
5. Warm-cache vanity forbidden.  
6. Wall clock ~10.6s · workers parallel antifp packs.  
7. BA `nano:ba:fastreal` + AG `nano:fastreal` archives untouched.  
8. Generative claim still locked (H-NANOGEN12 defer stance).

## Reproduce

```bash
npm run nano:bb:fasthold
npm run nano:intentgen
# ≠ BA archive: npm run nano:ba:fastreal
# ≠ AG archive: npm run nano:fastreal
```

## Artifacts

- Summary: `results/nano-lm/wave-bb/bb_fasthold_summary.json`  
- Contract: `nano_lm/tests/test_bb_fasthold.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked | Open chat / mini-AGI |
| Publish prod p50/p99 | LOOKUP wall=0 as speed IQ |
| Anti-FP hold required | Trade FP for ms |
| BB0/BA-FASTREAL baseline p99 | Warm-cache vanity as product win |
| BA/AG FASTREAL archives stay | Rewrite BA/AG formal-hfastreal |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; intent-mismatch LOOKUP = false-hit (min/xor/absdiff/and/or); BA-FOREVER PASS with BB-FOREVER FP = PACK THEATER; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; intent-mismatch LOOKUP = false-hit (BB-FOREVER min/xor/absdiff/and/or → add); exact-gold ABSTAIN = miss (a.clear()); BA-FOREVER pow·mod·max·sort·len FH must stay 0; AZ hold div·sub·BIP FH must stay 0; BA PASS with BB FP = PACK THEATER; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = BB4 only under real new method; no NANOGEN12 = NANOGEN11+rename; no CTX/SMART/FAST clone; no invent Wave BC without lab-book reopen; prefer HOLD/defer over fake PROMOTE

Next: **BB3 H-CTXHOLD** — context content bars without FP regress.
