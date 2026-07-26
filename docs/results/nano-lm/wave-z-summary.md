# Wave Z — HITL product eval (in progress)

> Lab: `.local/pesquisa.md` §9.  
> Champion export: `results/nano-lm/wave-z/models/champion/` (gitignored weights).

**Status: ACTIVE** · Wave Y **COMPLETE** → [wave-y-summary.md](wave-y-summary.md).

## Stage queue

| Stage | ID | Status | Notes |
|------:|----|--------|-------|
| Z0 | **EXPORT** | **DONE** | `champion-qpfb2-v0` = H-ABS-QPFB2 |
| Z1 | **HITL-10** | **DONE — FAIL** | mean **1.0**, errors **10**/10 → [wave-z-hitl-z1.md](wave-z-hitl-z1.md) |
| Z2 | MANUAL×10 | **DONE — PASS** | mean **9.0**; `champion-wrap-v0` → [wave-z-hitl-z2.md](wave-z-hitl-z2.md) |
| Z3 | **H-ZERR** | **DONE — PROMOTE** | bank CE; story −14.56 ≥ parent−ε → [wave-z-zerr.md](wave-z-zerr.md) |
| Z4 | HITL-10 verify | **NEXT** | mean ≥ Z1 + 0.5; pass bar mean≥7, errors≤3 |
| Z5 | LOOP≤3 | queued | — |
| Z6 | REPORT | queued | `wave-z-hitl.md` |

## Z3 evidence

| Artifact | Path |
|----------|------|
| Ckpt | `results/nano-lm/wave-z/models/zerr/HZERR_seed0.pt` |
| Recipe | `…/zerr/recipe.json` (`zerr-qpfb2-v0`) |
| Summary | `results/nano-lm/wave-z/z3_zerr_summary.json` |
| Public note | [wave-z-zerr.md](wave-z-zerr.md) |

Commands:

```bash
npm run nano:z:retrain -- --steps 40 --seed 0
npm run nano:z:ask -- --wrap --question "…"
npm run nano:z:ask -- --root results/nano-lm/wave-z/models/zerr --question "…"
```

## Doctrine

- Judge = frontier chat model (not ≤5M self-grade).  
- Forbidden: STREAM / KVCACHE-Q / GENCACHE / GPFB K=2 / MIXD retrain.  
- Live checklist: `.local/wave-z/SESSION.md`.
