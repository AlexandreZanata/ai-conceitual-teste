# H-LATP — latency triad p50/p99 (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AQ3 · Session: `.local/wave-aq/SESSION.md`  
> Parent: [formal-hadvfp-advfp.md](formal-hadvfp-advfp.md) · Baseline: [formal-hfastbase-fastbase.md](formal-hfastbase-fastbase.md)  
> Module: `nano_lm/src/latp_ops.py` · Runner: `npm run nano:latp`

## Hypothesis

Publish honest **p50/p99 wall_ms** for LOOKUP · PEAK · DECODE under AQ0 latency protocol. PEAK must not silently regress vs FASTBASE hot (**0.0471 ms**).

## Gate

| Path | p50 wall_ms | p99 wall_ms | n | sample mode |
|------|------------:|------------:|--:|-------------|
| LOOKUP | **0.0000** | **0.0000** | 64 | WRAP_LOOKUP |
| PEAK | **0.0223** | **0.0379** | 256 | PEAK_FAST+GENBASE |
| DECODE | **11.0099** | **133.1470** | 12 | QT+EARLY n=1 |

| FASTBASE hot (baseline) | **0.0471** | — | — | PEAK_FAST |
| PEAK regress vs baseline | **False** | — | — | — |
| Decision | **PROMOTE** | — | — | — |

## Regress note

PEAK p50 0.0223 ms ≤ FASTBASE hot 0.0471 ms — no regress.

## Protocol (AQ0)

| Path | Rule |
|------|------|
| LOOKUP | `wall_ms` may be 0 — **not** speed IQ |
| PEAK | `wall_ms` > 0; labeled extractive |
| DECODE | `wall_ms` > 0 and `n_new` > 0 |

## Finding

1. Triad published under max safe CPU threads (`cpus-2`).  
2. LOOKUP path labeled product retrieve — never sold as speed IQ.  
3. DECODE neural wall is a different regime than PEAK-fast hot.

## Reproduce

```bash
npm run nano:latp
npm run nano:z:ask -- --wrap --question "Write a short Python function named add that returns the sum of two integers a and b."
npm run nano:z:ask -- --question "Explain Merkle trees briefly"
```

## Artifacts

- Summary: `results/nano-lm/wave-aq/latp_summary.json`  
- Contract: `nano_lm/tests/test_latp.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| Publish triad p50/p99 | LOOKUP wall=0 as speed IQ |
| Honest PEAK regress note | Silent regress vs FASTBASE hot |
| DECODE wall>0 · n_new>0 | Peak-as-open-chat |

Next: **AQ4 H-KBCOV** — **DONE PROMOTE** → [formal-hkbcov-kbcov.md](formal-hkbcov-kbcov.md).
