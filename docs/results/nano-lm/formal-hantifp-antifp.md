# H-ANTIFP — anti-false-positive harness (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AG1 · Session: `.local/wave-ag/SESSION.md`  
> Module: `nano_lm/src/antifp_ops.py` · Runner: `npm run nano:antifp` (`nano:ag:antifp`)  
> Parent: [wave-ag-session.md](wave-ag-session.md) · AF audit: LOOKUP `wall_ms=0` ≢ generative IQ

## Hypothesis

A dual-arm harness forbids **intelligence / smarter-model PROMOTE** from LOOKUP-only scores; every ask logs `mode` · `wall_ms` · `n_new`; LOOKUP and GENERATE stay distinctly labeled.

## Gate

| Check | Result | Pass bar |
|-------|--------|----------|
| LOOKUP smoke labeled `WRAP_LOOKUP` | **ok** | LOOKUP ≠ GENERATE |
| GENERATE smoke `wall_ms>0` ∧ `n_new>0` | **ok** | raw arm runs |
| Telemetry present on both arms | **ok** | mode/wall_ms/n_new |
| IQ gate rejects LOOKUP-only “smarter” claim | **ok** | anti-FP law |
| IQ gate allows dual-arm smarter claim | **ok** | gen arm required |
| Decision | **PROMOTE** | contract + smoke |

## Smoke pack

| Arm | Trials | Notes |
|-----|--------|-------|
| LOOKUP | `AG-ANTIFP-LOOKUP-KNOWN` | Z1 `add` bank hit · product path |
| GENERATE | `AG-ANTIFP-GEN-KNOWN` + `AG-HITL-01…03` | no wrap · Cursor scores completion |

## Reproduce

```bash
npm run nano:ag:session
npm run nano:antifp
# alias: npm run nano:ag:antifp
npm run nano:test && npm run verify
```

## Finding

1. WRAP_LOOKUP remains a **product retrieval** path — high score ≠ generative IQ.  
2. Raw decode arm runs with real wall time; period-collapse still fails gold (honest).  
3. Harness blocks PROMOTE when an intelligence claim has LOOKUP logs only.  
4. Ship claim stays **AF packaged stack** until AG6.

## Artifacts

- Summary: `results/nano-lm/wave-ag/antifp_summary.json` (gitignored tree)
- Trials: `results/nano-lm/wave-ag/trials/AG-ANTIFP-*.json`
- Contract: `nano_lm/tests/test_antifp.py`

Next: **AG2 H-CTXREAL**.
