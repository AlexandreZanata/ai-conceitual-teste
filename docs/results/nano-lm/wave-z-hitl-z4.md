# Wave Z4 — HITL-10 verify (**DONE** — PASS · claim **H-ZWRAP**)

> Lab: `.local/pesquisa.md` §8–§9 · Live: `.local/wave-z/SESSION.md`  
> Same 10 questions as Z1/Z2. Three mandatory arms.

## Gate (primary = arm A)

| Arm | Stack | mean | errors | Pass bar |
|-----|-------|-----:|-------:|:--------:|
| **A** (primary) | `zerr` + `--wrap` | **9.0** | **0**/10 | **PASS** |
| **B** | `champion-qpfb2-v0` + `--wrap` | **9.0** | **0**/10 | PASS (ablation) |
| **C** | `zerr` raw (no wrap) | **1.0** | **10**/10 | FAIL (ablation) |

| Metric | Value | Rule |
|--------|------:|------|
| Δ vs Z1 (arm A) | **+8.0** | ≥ +0.5 |
| Decision | **PASS** | arm A pass bar + beats Z1 |
| Claim branch | **H-ZWRAP** | PASS only with lookup; raw CE does not fix open decode |

## Finding

1. **Product HITL** on the known-ask set is **`--wrap` LOOKUP** (`champion-wrap-v0`), with or without ZERR weights (A ≡ B).  
2. **H-ZERR** remains **story-safe CE** (Z3 smoke) — **not** an interactive chat LM: arm C still collapses to `........` under QT+EARLY n=1.  
3. Do **not** open **H-SERVEALIGN** unless the product goal shifts to open generative ask (ladder §8 #3). Known-ask demo stays wrap.

## Trials

| Arm | ids | mode | score |
|-----|-----|------|------:|
| A | Z4A-01 … Z4A-10 | WRAP_LOOKUP | 9.0 |
| B | Z4B-01 … Z4B-10 | WRAP_LOOKUP | 9.0 |
| C | Z4C-01 … Z4C-10 | QT+EARLY n=1 | 1.0 |

Judge: `cursor-composer-frontier-chat`. Manual adjust: lookup held (A/B); open decode unchanged (C).  
Error bank: **no new rows** (C reconfirms Z1 failures already banked).

## Reproduce

```bash
npm run nano:z:z4 -- --arms A,B,C
# or single ask:
npm run nano:z:ask -- --wrap --root results/nano-lm/wave-z/models/zerr --question "…"
npm run nano:z:ask -- --wrap --question "…"
npm run nano:z:ask -- --root results/nano-lm/wave-z/models/zerr --question "…"
```

## Artifacts

- Trials: `results/nano-lm/wave-z/trials/Z4{A,B,C}-01.json` … `-10.json` (gitignored)
- Summary: `results/nano-lm/wave-z/z4_summary.json`
- Gate module: `nano_lm/src/z_z4.py` · runner: `nano_lm/src/run_z4_hitl.py`
- Contract: `nano_lm/tests/test_z_z4.py`

Next: **DEPL-Y** · **Z6** — **DONE** → [wave-z-hitl.md](wave-z-hitl.md) (Wave Z **COMPLETE**).
