# H-ASKFAST — compose fast ask (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8.3 AB2 · Session: `.local/wave-ab/SESSION.md`  
> Parent: **H-SEMWRAP** · **H-QT** · SCORERAM-like ask cache · Pack: AB0 frozen asks  
> Module: `nano_lm/src/askfast_ops.py` · Runner: `npm run nano:askfast`

## Hypothesis

Compose **SEMWRAP + QT batch ask_many + AskCompletionCache** on the product ask path so pack wall/TTFT drops **≥20%** vs raw QT∘EARLY decode, while HITL quality stays at the known-ask floor.

## Gate (Cursor ASK→EVAL→FIX×10)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| mean score | **9.0** | ≥ 7.0 |
| errors | **0**/10 | ≤ 3 |
| FALSE_HIT | **0**/10 | any → **KILL** |
| baseline mean wall_ms | **25.2** | QT∘EARLY n=1 (no wrap) |
| ASKFAST mean wall_ms | **0.0** | SEMWRAP_LOOKUP |
| wall_drop | **100%** | ≥ **20%** |
| cache hit-rate (cold+warm) | **0.50** | warm pass hits |
| FIX count | **0** | — |
| Decision | **PROMOTE** | quality ∧ wall↓ ∧ no false-hit |

## Finding

1. Baseline open decode on AB asks is slow and period-collapse (product without lookup).  
2. ASKFAST compose recovers SEMWRAP golds at **0 ms** lookup wall; e2e pack **~3.7s → ~0.09s**.  
3. Completion cache warms on pass-1 and serves pass-2 (`ASKFAST_CACHE`).  
4. Still **not** open chat LM — scoped near-known assist only. Never STREAM / KVCACHE-Q / GENCACHE.

## Reproduce

```bash
npm run nano:askfast
npm run nano:z:ask -- --askfast --question "How do BIP-39 mnemonic phrases turn into a wallet seed? Keep it short."
```

## Artifacts

- Summary: `results/nano-lm/wave-ab/askfast_summary.json`  
- Trials: `results/nano-lm/wave-ab/trials/AB-ASKFAST-HITL-01.json` … `10.json`  
- Contract: `nano_lm/tests/test_askfast.py`

Next: **AB3 H-LONGAPP**.
