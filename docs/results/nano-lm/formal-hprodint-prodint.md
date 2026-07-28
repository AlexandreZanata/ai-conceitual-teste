# H-PRODINT — intent FH 0 Caminho A (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AY1 · Session: `.local/wave-ay/SESSION.md`  
> Parent: [wave-ay-session.md](wave-ay-session.md) · Suite: AY0 product-int  
> Module: `nano_lm/src/prodint_ops.py` · Runner: `npm run nano:prodint`

## Hypothesis

Close intent/adversary false-hit debt on Caminho A: intent FH 0 on live FP class (mul≠add · diff≠sum · remove≠clear · half-known BIP); hold hard-natural ≥ bar; FH 0 near-miss; DECODE usable or ABSTAIN; publish para · FH · p50/p99 · KB · modes 4/4 — no bank stuffing

## Gate

| Metric | Result | Bar |
|--------|-------:|-----|
| intent_false_hit | **0** (12/12 ABSTAIN) | **0** |
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
| PEAK | **0.024089004000416026** | **0.0409542455599876** |
| DECODE | **10.948937997454777** | **11.769715572881978** |
| ABSTAIN | **93.52753849816509** | **137.85343998119063** |

## KB holes

- `open-world chat / unbounded general knowledge`
- `languages beyond Python + Rust (bank scope)`
- `BIPs / RFCs not present in curated+bank golds`
- `math proofs and multi-step symbolic reasoning`
- `live web retrieval / tool-use agency`
- `unlabeled PEAK sold as DECODE IQ (anti-FP)`

## Finding

1. Intent-FP held-out (N≥12 · 4 classes) scored on production `nano:z:ask --wrap --semwrap`.  
2. SEMWRAP `contrastive_reject` + `intent_ask_must_abstain` close mul→add · difference-add · remove≠clear · BIP wordlist sibling — **not** bank stuffing.  
3. Hard-natural AX pack held (≥ bar).  
4. Near-miss BIP-39+SegWit stays ABSTAIN.  
5. DECODE content law holds — usable or ABSTAIN.  
6. Modes + latency + KB republished.  
7. Wall clock ~12.5s · max safe CPU (`cpus-2`).  
8. Generative claim still locked (gen stance **defer**; H-NANOGEN9; NANOGEN6·7 HOLD · NANOGEN8 DEFER).

## Reproduce

```bash
npm run nano:prodint
npm run nano:ay:session
```

## Artifacts

- Summary: `results/nano-lm/wave-ay/prodint_summary.json`  
- Contract: `nano_lm/tests/test_prodint.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked | Open chat / mini-AGI |
| Intent mismatch → ABSTAIN | Intent-FP as LOOKUP hit |
| Eval path = prod ask path | LOOKUP-as-IQ · SAFE-as-quality |
| Hard-natural hold | Pack FH as live intent coverage |
| Honest HOLD/KILL on bar fail | Bank stuffing |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ live intent/adversary coverage; intent-mismatch LOOKUP = false-hit; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; intent-mismatch LOOKUP = false-hit (mul/diff/remove/half-known); truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; pack FH 0 ≠ live intent coverage; generative bar = AY3 only under real new method; no NANOGEN9 = NANOGEN8+rename; no CTX/SMART/FAST clone; no invent Wave AZ without lab-book reopen; prefer HOLD/defer over fake PROMOTE

Next: **AY2 H-SHIPAY** — ship/demo mode+content honesty.
