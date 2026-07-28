# H-FASTREAL (BA2) — prod p50/p99 + anti-FP hold (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 · §8 BA2 · Session: `.local/wave-ba/SESSION.md`  
> Parent: [formal-hrealgain-realgain.md](formal-hrealgain-realgain.md) · BA0 speed baseline  
> Module: `nano_lm/src/ba_fastreal_ops.py` · Runner: `npm run nano:ba:fastreal`  
> **Not** AG archive [formal-hfastreal-fastreal.md](formal-hfastreal-fastreal.md) (`npm run nano:fastreal`)

## Hypothesis

Publish prod-ask p50/p99 for LOOKUP·PEAK·DECODE·ABSTAIN; PROMOTE only if §1 anti-FP holds (forever FH 0 · AZ hold · over-refuse 0 · live FP 0) and live p99 does not regress vs BA0 speed baseline — never warm-cache vanity; LOOKUP wall=0 ≠ speed IQ; ≠ AG H-FASTREAL gen microbench archive

## Gate

| Metric | Result | Bar |
|--------|-------:|-----|
| forever_false_hit | **0** (15/15) | **0** |
| az_hold_false_hit | **0** (12/12) | **0** |
| overrefuse_miss | **0** (3/3) | **0** |
| live_fp | **0** | **0** |
| p99_regress | **False** ([]) | false (≤1.5× BA0) |
| modes_visible | **ABSTAIN · DECODE · LOOKUP · PEAK** (4/4) | 4/4 |
| Decision | **PROMOTE** | — |

## Latency p50/p99 (prod ask path)

| Path | p50 wall_ms | p99 wall_ms | n |
|------|------------:|------------:|--:|
| LOOKUP | **0.0** | **0.0** | 64 |
| PEAK | **0.00948000160860829** | **0.016213351700571366** | 128 |
| DECODE | **12.682843498623697** | **17.01244352661888** | 12 |
| ABSTAIN | **95.4394950022106** | **125.30305242056787** | 32 |

Samples: LOOKUP=64 · PEAK=128 · DECODE=12 · ABSTAIN=32

## Finding

1. Prod-path tetrad measured under max safe CPU (`cpus-4`).  
2. LOOKUP wall=0 **not** sold as speed IQ.  
3. REALGAIN anti-FP hold: forever FH 0 · AZ hold · over-refuse 0 · live FP 0.  
4. Live p99 checked vs BA0 AZ-PRODGEN baseline (max ratio 1.5).  
5. Warm-cache vanity forbidden.  
6. Wall clock ~10.6s · workers parallel antifp packs.  
7. AG H-FASTREAL gen microbench archive untouched (`npm run nano:fastreal`).  
8. Generative claim still locked (H-NANOGEN11 defer stance).

## Reproduce

```bash
npm run nano:ba:fastreal
npm run nano:realgain
# AG archive (do not confuse): npm run nano:fastreal
```

## Artifacts

- Summary: `results/nano-lm/wave-ba/ba_fastreal_summary.json`  
- Contract: `nano_lm/tests/test_ba_fastreal.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked | Open chat / mini-AGI |
| Publish prod p50/p99 | LOOKUP wall=0 as speed IQ |
| Anti-FP hold required | Trade FP for ms |
| BA0 baseline p99 check | Warm-cache vanity as product win |
| AG FASTREAL archive stays | Rewrite AG formal-hfastreal |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; intent-mismatch LOOKUP = false-hit (pow/mod/max/sort/len); exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; intent-mismatch LOOKUP = false-hit (BA-FOREVER pow/mod/max/sort/len); exact-gold ABSTAIN = miss (a.clear()); AZ hold div·sub·BIP FH must stay 0; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; pack PASS with forever FP = PACK THEATER; generative bar = BA4 only under real new method; no NANOGEN11 = NANOGEN10+rename; no CTX/SMART/FAST clone; no invent Wave BB without lab-book reopen; prefer HOLD/defer over fake PROMOTE

Next: **BA3 H-CTXREAL2** — context content bars without FP regress.
