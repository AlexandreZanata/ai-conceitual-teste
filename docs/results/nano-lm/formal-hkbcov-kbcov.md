# H-KBCOV — KB coverage + holes (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AQ4 · Session: `.local/wave-aq/SESSION.md`  
> Parent: [formal-hlatp-latp.md](formal-hlatp-latp.md) · AQ0: [wave-aq-session.md](wave-aq-session.md)  
> Module: `nano_lm/src/kbcov_ops.py` · Runner: `npm run nano:kbcov`

## Hypothesis

Publish honest **curated∩bank coverage %** plus an **explicit hole list**. Registry 100% ≠ complete product KB.

## Gate

| Metric | Value |
|--------|------:|
| curated covered | **22** / **22** |
| coverage_pct | **100.0** |
| curated blobs present | **22** / **22** (100.0%) |
| PARA parent LOOKUP golds | **20** / **20** (100.0%) |
| complete_claim_forbidden | **True** |
| Decision | **PROMOTE** |

## Missing curated ids in bank

_(none)_

## PARA parent gold misses

_(none)_

## Explicit holes (product + registry)

- open-world chat / unbounded general knowledge
- languages beyond Python + Rust (bank scope)
- BIPs / RFCs not present in curated+bank golds
- math proofs and multi-step symbolic reasoning
- live web retrieval / tool-use agency
- unlabeled PEAK sold as DECODE IQ (anti-FP)

## Finding

1. Coverage % published under max safe CPU threads (`cpus-2`).  
2. Product holes always listed — no fake 100% completeness.  
3. Frozen product holes n=6 (open-world · languages · BIPs/RFCs · math · tools · anti-FP).

## Reproduce

```bash
npm run nano:kbcov
npm run nano:z:ask -- --wrap --question "Write a short Python function named add that returns the sum of two integers a and b."
```

## Artifacts

- Summary: `results/nano-lm/wave-aq/kbcov_summary.json`  
- Contract: `nano_lm/tests/test_kbcov.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| Publish coverage % + holes | Fake complete product KB |
| Registry 100% with product holes | Selling curated∩bank as open-world |
| List PARA gold misses | Expanding bank until HITL theater |

Next: **AQ5 H-MODEUI** — ship/demo UI shows `mode=LOOKUP|PEAK|DECODE`.
