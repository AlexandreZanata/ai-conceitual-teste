# H-PRODKEEP — Caminho A keep (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §2 AW1 · Session: `.local/wave-aw/SESSION.md`  
> Parent: [wave-aw-session.md](wave-aw-session.md) · Suite: AW0 product-keep  
> Module: `nano_lm/src/prodkeep_ops.py` · Runner: `npm run nano:prodkeep`

## Hypothesis

Hold Caminho A under pressure-para ≠ AV/AU: para ≥ bar; FH 0; DECODE usable or ABSTAIN; publish para · FH · p50/p99 · KB · modes 4/4; regression_hold vs AV PRODSHIP/SHIPUI2

## Gate

| Metric | Result | Bar |
|--------|-------:|-----|
| pressure_para_hit | **0.95** (19/20) | ≥ 0.7 · n≥20 |
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
| PEAK | **0.024570999812567607** | **0.029902652386226684** |
| DECODE | **11.111777002952294** | **12.18761410935258** |
| ABSTAIN | **94.5078824988741** | **101.50719203884364** |

## KB holes

- `open-world chat / unbounded general knowledge`
- `languages beyond Python + Rust (bank scope)`
- `BIPs / RFCs not present in curated+bank golds`
- `math proofs and multi-step symbolic reasoning`
- `live web retrieval / tool-use agency`
- `unlabeled PEAK sold as DECODE IQ (anti-FP)`

## DECODE probe (content law hold)

- mode: **ABSTAIN**  
- abstained: **True**  
- sample: `NO_ANSWER`

## PEAK sample

`_Ownership_ is a set of rules that govern how a Rust program manages memory`

## Finding

1. Pressure held-out para (N≥20 ≠ AV/AU) scored on production `nano:z:ask --wrap --semwrap`.  
2. Near-miss BIP-39+SegWit stays ABSTAIN on default ask.  
3. DECODE content law holds — usable or ABSTAIN (gibberish ≠ content_ok).  
4. Modes + latency + KB republished under pressure.  
5. Wall clock ~15.8s · max safe CPU (`cpus-2`).  
6. Generative claim still locked until AW3 H-NANOGEN7 TAC (true continue; span-fallback ≠ gen).

## Reproduce

```bash
npm run nano:prodkeep
npm run nano:aw:session
```

## Artifacts

- Summary: `results/nano-lm/wave-aw/prodkeep_summary.json`  
- Contract: `nano_lm/tests/test_prodkeep.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM | Open chat / mini-AGI |
| Eval path = prod ask path | LOOKUP-as-IQ · SAFE-as-quality |
| DECODE usable or ABSTAIN | telemetry-only content_ok |
| Honest HOLD/KILL on bar fail | Eval-only patches · bank stuffing |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); gold-substring / gibberish-tail / truncate-to-span ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = AW3 only; no vanity re-SEMFIX/ADVSAFE unless PRODKEEP fails; no Wave AX invent; no CTX/SMART/FAST clone; no NANOGEN7 = NANOGEN6+rename; TAC ≠ refuse-or-continue clone

Next: **AW2 H-SHIPKEEP** — **DONE PROMOTE** (`npm run nano:shipkeep`) · next **AW3 H-NANOGEN7**.
