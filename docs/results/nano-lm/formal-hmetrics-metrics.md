# H-METRICS — latency tetrad + KB refresh (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AS5 · Session: `.local/wave-as/SESSION.md`  
> Parent: [formal-hparaext2-paraext2.md](formal-hparaext2-paraext2.md) · Protocol: AS0 METRICS  
> Module: `nano_lm/src/metrics_ops.py` · Runner: `npm run nano:metrics`

## Hypothesis

After ASKABSTAIN · SEMFIX · ADVSAFE · PARAEXT2, republish honest **p50/p99 wall_ms** for LOOKUP · PEAK · DECODE · **ABSTAIN** plus **KB coverage %** with explicit holes.

## Latency gate

| Path | p50 wall_ms | p99 wall_ms | n | sample mode |
|------|------------:|------------:|--:|-------------|
| LOOKUP | **0.0000** | **0.0000** | 64 | WRAP_LOOKUP |
| PEAK | **0.0235** | **0.0276** | 256 | PEAK_FAST+GENBASE |
| DECODE | **11.0160** | **140.1569** | 12 | QT+EARLY n=1 |
| ABSTAIN | **99.1236** | **137.1255** | 32 | NO_ANSWER |

| FASTBASE hot (baseline) | **0.0471** | — | — | PEAK_FAST |
| PEAK regress vs baseline | **False** | — | — | — |
| Decision | **PROMOTE** | — | — | — |

## Regress note

PEAK p50 0.0235 ms ≤ FASTBASE hot 0.0471 ms — no regress.

## Protocol (AS0)

| Path | Rule |
|------|------|
| LOOKUP | `wall_ms` may be 0 — **not** speed IQ |
| PEAK | `wall_ms` > 0; labeled extractive |
| DECODE | `wall_ms` > 0 and `n_new` > 0 (sample abstain off) |
| ABSTAIN | default ask OOD → `NO_ANSWER`; publish `wall_ms` |

## KB coverage refresh

| Metric | Value |
|--------|------:|
| curated covered | **22** / **22** |
| coverage_pct | **100.0** |
| curated blobs present | **22** / **22** (100.0%) |
| PARAEXT2 parent LOOKUP golds | **20** / **20** (100.0%) |
| complete_claim_forbidden | **True** |

## Missing curated ids in bank

_(none)_

## PARAEXT2 parent gold misses

_(none)_

## Explicit holes (product + registry)

- open-world chat / unbounded general knowledge
- languages beyond Python + Rust (bank scope)
- BIPs / RFCs not present in curated+bank golds
- math proofs and multi-step symbolic reasoning
- live web retrieval / tool-use agency
- unlabeled PEAK sold as DECODE IQ (anti-FP)

## Finding

1. Tetrad(+ABSTAIN) published under max safe CPU (`cpus-2`).  
2. LOOKUP wall=0 not sold as speed IQ.  
3. ABSTAIN path measured on default ask after AS1.  
4. KB holes explicit — no fake world-complete claim.  
5. Product holes n=6.

## Reproduce

```bash
npm run nano:metrics
npm run nano:z:ask -- --wrap --question "Write a short Python function named add that returns the sum of two integers a and b."
npm run nano:z:ask -- --semwrap --question "Which nation hosted the 2016 Summer Olympics?"
```

## Artifacts

- Summary: `results/nano-lm/wave-as/metrics_summary.json`  
- Contract: `nano_lm/tests/test_metrics.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| Publish tetrad p50/p99 + KB holes | LOOKUP wall=0 as speed IQ |
| Honest PEAK regress note | Silent regress / fake complete KB |
| ABSTAIN wall published | Mini-AGI / open-chat claim |

Next: **AS6 H-SHIPUI** — mode visible on ship/demo + ask.
