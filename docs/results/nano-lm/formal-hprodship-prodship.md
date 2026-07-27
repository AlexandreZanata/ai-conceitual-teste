# H-PRODSHIP — Caminho A ship (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AV1 · Session: `.local/wave-av/SESSION.md`  
> Parent: [wave-av-session.md](wave-av-session.md) · Suite: AV0 product-ship  
> Module: `nano_lm/src/prodship_ops.py` · Runner: `npm run nano:prodship`

## Hypothesis

Ship Caminho A on production ask: external human para ≥ bar; FH 0; DECODE gibberish ≠ content_ok (usable or ABSTAIN); publish para · FH · p50/p99 · KB · modes 4/4

## Gate

| Metric | Result | Bar |
|--------|-------:|-----|
| external_para_hit | **1.0** (20/20) | ≥ 0.7 · n≥20 |
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
| PEAK | **0.024386999939451925** | **0.03449509822530668** |
| DECODE | **11.80666100117378** | **12.905136199406115** |
| ABSTAIN | **99.68953350107768** | **198.66111726139943** |

## KB holes

- `open-world chat / unbounded general knowledge`
- `languages beyond Python + Rust (bank scope)`
- `BIPs / RFCs not present in curated+bank golds`
- `math proofs and multi-step symbolic reasoning`
- `live web retrieval / tool-use agency`
- `unlabeled PEAK sold as DECODE IQ (anti-FP)`

## DECODE probe (content debt)

- mode: **ABSTAIN**  
- abstained: **True**  
- sample: `NO_ANSWER`

## PEAK sample

`_Ownership_ is a set of rules that govern how a Rust program manages memory`

## Finding

1. External held-out para (N≥20 ≠ AU) scored on production `nano:z:ask --wrap --semwrap`.  
2. Near-miss BIP-39+SegWit stays ABSTAIN on default ask.  
3. WRAP_DECODE gibberish no longer passes content_ok — junk → ABSTAIN (closes AU-ASK-05 debt).  
4. Modes + latency + KB republished.  
5. Wall clock ~14.5s · max safe CPU (`cpus-2`).  
6. Generative claim still locked until AV3 H-NANOGEN6 (true continue; span-fallback ≠ gen).

## Reproduce

```bash
npm run nano:prodship
npm run nano:av:session
```

## Artifacts

- Summary: `results/nano-lm/wave-av/prodship_summary.json`  
- Contract: `nano_lm/tests/test_prodship.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM | Open chat / mini-AGI |
| Eval path = prod ask path | LOOKUP-as-IQ · SAFE-as-quality |
| DECODE usable or ABSTAIN | telemetry-only content_ok |
| Honest HOLD/KILL on bar fail | Eval-only patches |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); gold-substring / gibberish-tail / truncate-to-span ≠ generative PROMOTE  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = AV3 only; no vanity re-SEMFIX/ADVSAFE unless PRODSHIP fails; no Wave AW invent; no CTX/SMART/FAST clone; no NANOGEN6 = NANOGEN5+rename

Next: **AV2 H-SHIPUI2** — ship/demo mode+content honesty.
