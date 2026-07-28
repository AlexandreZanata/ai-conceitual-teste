# H-PRODGEN — held-out FH 0 + no over-refuse (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AZ1 · Session: `.local/wave-az/SESSION.md`  
> Parent: [wave-az-session.md](wave-az-session.md) · Suite: AZ0 product-gen  
> Module: `nano_lm/src/prodgen_ops.py` · Runner: `npm run nano:prodgen`

## Hypothesis

Close held-out intent FH + over-refuse on Caminho A: held-out FH 0 (div≠add · sub≠add · wrong-slot BIP); exact clear gold LOOKUP; hold AY named intent FH 0 + hard-natural ≥ bar; FH 0 near-miss; DECODE usable or ABSTAIN; publish para · FH · p50/p99 · KB · modes 4/4 — no bank stuffing

## Gate

| Metric | Result | Bar |
|--------|-------:|-----|
| heldout_false_hit | **0** (12/12 ABSTAIN) | **0** |
| overrefuse_miss | **0** (3/3 LOOKUP) | **0** |
| named_intent_false_hit | **0** (12/12 hold) | **0** |
| hard_natural_para_hit | **1.0** (18/18) | ≥ 0.7 hold |
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
| PEAK | **0.025749999622348696** | **0.04585624847095457** |
| DECODE | **11.370015501597663** | **13.2598652010347** |
| ABSTAIN | **95.44715250012814** | **119.4430812008068** |

## KB holes

- `open-world chat / unbounded general knowledge`
- `languages beyond Python + Rust (bank scope)`
- `BIPs / RFCs not present in curated+bank golds`
- `math proofs and multi-step symbolic reasoning`
- `live web retrieval / tool-use agency`
- `unlabeled PEAK sold as DECODE IQ (anti-FP)`

## Finding

1. Held-out FP (N≥12 · div·sub·wrong-slot) scored on production `nano:z:ask --wrap --semwrap`.  
2. SEMWRAP `contrastive_reject` + `intent_ask_must_abstain` close div→add · sub→add · BIP 12-word entropy≠32 — **not** bank stuffing.  
3. Over-refuse fix: clear-all paraphrases LOOKUP `a.clear()` (prefer clear gold; never reject exact clear).  
4. AY named intent FH 0 held (mul·diff·remove·half-known).  
5. Hard-natural AX pack held (≥ bar).  
6. Near-miss BIP-39+SegWit stays ABSTAIN.  
7. DECODE content law holds — usable or ABSTAIN.  
8. Modes + latency + KB republished.  
9. Wall clock ~14.1s · max safe CPU (`cpus-2`).  
10. Generative claim still locked (gen stance **defer**; H-NANOGEN10; NANOGEN6·7 HOLD · NANOGEN8·9 DEFER).

## Reproduce

```bash
npm run nano:prodgen
npm run nano:az:session
```

## Artifacts

- Summary: `results/nano-lm/wave-az/prodgen_summary.json`  
- Contract: `nano_lm/tests/test_prodgen.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked | Open chat / mini-AGI |
| Held-out mismatch → ABSTAIN | Held-out FP as LOOKUP hit |
| Exact clear → LOOKUP | Over-refuse as “safe” win |
| Eval path = prod ask path | LOOKUP-as-IQ · SAFE-as-quality |
| Named FH hold ≠ held-out coverage | Bank stuffing |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); named-class FH 0 ≠ held-out generalization; intent-mismatch LOOKUP = false-hit; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; intent-mismatch LOOKUP = false-hit (div/sub/wrong-slot held-out); exact-gold ABSTAIN = miss (a.clear()); truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; pack/named FH 0 ≠ held-out coverage; generative bar = AZ3 only under real new method; no NANOGEN10 = NANOGEN9+rename; no CTX/SMART/FAST clone; no invent Wave BA without lab-book reopen; prefer HOLD/defer over fake PROMOTE

Next: **AZ2 H-SHIPAZ** — ship/demo mode+content honesty.
