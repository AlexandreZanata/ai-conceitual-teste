# H-PRODREG — Caminho A regression (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AT1 · Session: `.local/wave-at/SESSION.md`  
> Parent: [wave-at-session.md](wave-at-session.md) · Suite: AT0 PRODREG  
> Module: `nano_lm/src/prodreg_ops.py` · Runner: `npm run nano:prodreg`

## Hypothesis

Caminho A regression: remeasure para hit · FH · p50/p99 · KB holes · modes · default-ask abstain against AT0/AS bars; PROMOTE iff all hold

## Gate

| Pillar | Decision |
|--------|----------|
| askabstain | **PROMOTE** |
| advsafe | **PROMOTE** |
| paraext2 | **PROMOTE** |
| metrics | **PROMOTE** |
| shipui | **PROMOTE** |

| Metric | Result | Bar |
|--------|-------:|-----|
| para_hit | **0.8** (16/20) | ≥ 0.7 |
| false_hit | **0** | **0** |
| modes_visible | **ABSTAIN · DECODE · LOOKUP · PEAK** (4/4) | LOOKUP·PEAK·DECODE·ABSTAIN |
| default_ask_abstain_rate | **1.0** | ABSTAIN |
| kb_coverage_pct | **100.0** | publish + holes |
| Decision | **PROMOTE** | — |

## Latency p50/p99 (republish)

| Path | p50 wall_ms | p99 wall_ms |
|------|------------:|------------:|
| LOOKUP | **0.0** | **0.0** |
| PEAK | **0.023110500478651375** | **0.039549148641526685** |
| DECODE | **11.908825501450337** | **12.667424389328517** |
| ABSTAIN | **100.4442064986506** | **198.39388846768998** |

## KB holes

- `open-world chat / unbounded general knowledge`
- `languages beyond Python + Rust (bank scope)`
- `BIPs / RFCs not present in curated+bank golds`
- `math proofs and multi-step symbolic reasoning`
- `live web retrieval / tool-use agency`
- `unlabeled PEAK sold as DECODE IQ (anti-FP)`

## Finding

1. Live remeasure of AS product pillars under `write_docs=False` (AS formal archives stay frozen).  
2. Bars from AT0 PRODREG suite (para≥0.70 · FH0 · modes · abstain · latency/KB publish).  
3. No vanity re-SEMFIX / re-ADVSAFE unless this gate fails.  
4. Wall clock ~19.9s · max safe CPU (`cpus-2`).  
5. Generative claim still locked until AT3 H-NANOGEN4.

## Reproduce

```bash
npm run nano:prodreg
npm run nano:at:session
```

## Artifacts

- Summary: `results/nano-lm/wave-at/prodreg_summary.json`  
- Pillar regs: `results/nano-lm/wave-at/*_reg.json`  
- Contract: `nano_lm/tests/test_prodreg.py`

## Claims

| Allowed | Forbidden |
|---------|-----------|
| AF packaged stack + AQ product layer + AS trust path — not open chat LM | Open chat / mini-AGI |
| Honest HOLD/KILL on bar fail | LOOKUP-as-IQ · SAFE-as-quality |
| Republish p50/p99 + KB holes | Rewrite AS locked formals |

SAFE note: SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP)  
Anti-FP: LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; generative bar = AT3 only; no vanity re-SEMFIX/ADVSAFE unless PRODREG fails; no Wave AU invent

Next: **AT2 H-SHIPAPP** — **DONE PROMOTE** → [formal-hshipapp-shipapp.md](formal-hshipapp-shipapp.md). **AT3 H-NANOGEN4** — ablated DECODE ≥ **5.0**.
