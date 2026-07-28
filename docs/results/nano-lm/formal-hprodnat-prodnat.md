# H-PRODNAT — hard-natural Caminho A (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AX1 · Session: `.local/wave-ax/SESSION.md`  
> Parent: [wave-ax-session.md](wave-ax-session.md) · Suite: AX0 product-nat  
> Module: `nano_lm/src/prodnat_ops.py` · Runner: `npm run nano:prodnat`

## Hypothesis

Close hard-natural human para debt on Caminho A: hard-natural ≥ bar; FH 0; DECODE usable or ABSTAIN; publish para · FH · p50/p99 · KB · modes 4/4; pack-para ≠ hard-natural coverage claim

## Gate

| Metric | Result | Bar |
|--------|-------:|-----|
| hard_natural_para_hit | **1.0** (18/18) | ≥ 0.7 · n≥15 |
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
| PEAK | **0.03354299769853242** | **0.09134564970736392** |
| DECODE | **15.41926199934096** | **16.145512283110293** |
| ABSTAIN | **831.6031095018843** | **1591.7017181125993** |

## KB holes

- `open-world chat / unbounded general knowledge`
- `languages beyond Python + Rust (bank scope)`
- `BIPs / RFCs not present in curated+bank golds`
- `math proofs and multi-step symbolic reasoning`
- `live web retrieval / tool-use agency`
- `unlabeled PEAK sold as DECODE IQ (anti-FP)`

## DECODE probe (content law)

- mode: **ABSTAIN**  
- abstained: **True**  
- sample: `NO_ANSWER`

## PEAK sample

`_Ownership_ is a set of rules that govern how a Rust program manages memory`

## Finding

1. Hard-natural held-out (N≥15 ≠ AW/AV/AU) scored on production `nano:z:ask --wrap --semwrap`.  
2. SEMWRAP same-gold whitespace collapse closes live miss (multiline vs one-liner `def add`) — **not** bank stuffing.  
3. Near-miss BIP-39+SegWit stays ABSTAIN on default ask.  
4. DECODE content law holds — usable or ABSTAIN.  
5. Modes + latency + KB republished; pack-para ≠ hard-natural.  
6. Wall clock ~40.4s · max safe CPU (`cpus-2`).  
7. Generative claim still locked (gen stance **defer**; NANOGEN6·7 HOLD).

## Reproduce

```bash
npm run nano:prodnat
npm run nano:ax:session
```

## Artifacts

- Summary: `results/nano-lm/wave-ax/prodnat_summary.json`  
- Contract: `nano_lm/tests/test_prodnat.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked | Open chat / mini-AGI |
| Eval path = prod ask path | LOOKUP-as-IQ · SAFE-as-quality |
| Hard-natural hit ≥ bar | Pack-para as world coverage |
| Honest HOLD/KILL on bar fail | Paraphrase bank stuffing |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack/pressure-para ≠ hard natural coverage; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; pack-para ≠ hard natural coverage; generative bar = AX3 only under real new method; no NANOGEN8 = NANOGEN7+rename; no CTX/SMART/FAST clone; no invent Wave AY without lab-book reopen; prefer HOLD/defer over fake PROMOTE

Next: **AX2 H-SHIPUX** — ship/demo mode+content honesty.
