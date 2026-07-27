# H-PRODHARD — live-audit close (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AU1 · Session: `.local/wave-au/SESSION.md`  
> Parent: [wave-au-session.md](wave-au-session.md) · Suite: AU0 product-debt  
> Module: `nano_lm/src/prodhard_ops.py` · Runner: `npm run nano:prodhard`

## Hypothesis

Close live-audit debts on production ask path: near-miss → ABSTAIN; held-out human para ≥ bar; PEAK usable span or ABSTAIN; publish para · FH · p50/p99 · KB · modes

## Gate

| Metric | Result | Bar |
|--------|-------:|-----|
| human_para_hit | **1.0** (8/8) | ≥ 0.7 |
| false_hit (near-miss) | **0** | **0** |
| near_miss_ok | **True** (ABSTAIN) | ABSTAIN |
| peak_ok | **True** (PEAK) | usable or ABSTAIN |
| known_lookup_ok | **True** | True |
| modes_visible | **ABSTAIN · DECODE · LOOKUP · PEAK** (4/4) | LOOKUP·PEAK·DECODE·ABSTAIN |
| kb_coverage_pct | **100.0** | publish + holes |
| Decision | **PROMOTE** | — |

## Latency p50/p99 (republish)

| Path | p50 wall_ms | p99 wall_ms |
|------|------------:|------------:|
| LOOKUP | **0.0** | **0.0** |
| PEAK | **0.02545400093367789** | **0.038037948979763314** |
| DECODE | **11.21577649792016** | **139.12690012901302** |
| ABSTAIN | **91.99922000152583** | **174.43748208970655** |

## KB holes

- `open-world chat / unbounded general knowledge`
- `languages beyond Python + Rust (bank scope)`
- `BIPs / RFCs not present in curated+bank golds`
- `math proofs and multi-step symbolic reasoning`
- `live web retrieval / tool-use agency`
- `unlabeled PEAK sold as DECODE IQ (anti-FP)`

## PEAK sample

`_Ownership_ is a set of rules that govern how a Rust program manages memory`

## Finding

1. Near-miss BIP-39+SegWit refuses on **default** `nano:z:ask --wrap --semwrap` (not eval-only).  
2. Held-out human para of `add` scored on production SEMWRAP.  
3. PEAK returns usable ownership span (or ABSTAIN).  
4. Modes + latency + KB republished.  
5. Wall clock ~12.9s · max safe CPU (`cpus-2`).  
6. Generative claim still locked until AU3 H-NANOGEN5.

## Reproduce

```bash
npm run nano:prodhard
npm run nano:au:session
```

## Artifacts

- Summary: `results/nano-lm/wave-au/prodhard_summary.json`  
- Contract: `nano_lm/tests/test_prodhard.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix) — not unlabeled open chat LM | Open chat / mini-AGI |
| Eval path = prod ask path | LOOKUP-as-IQ · SAFE-as-quality |
| Honest HOLD/KILL on bar fail | Eval-only near-miss patch |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); gold-substring ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; no gibberish-tail PROMOTE; eval path = prod ask path; generative bar = AU3 only; no vanity re-SEMFIX/ADVSAFE unless PRODHARD fails; no Wave AV invent; no CTX/SMART/FAST clone

Next: **AU2 H-SHIPREAL** — human ship/demo mode honesty.
