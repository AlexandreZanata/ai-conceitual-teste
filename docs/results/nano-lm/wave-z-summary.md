# Wave Z — HITL product eval (in progress)

> Lab: `.local/pesquisa.md` §9.  
> Champion export: `results/nano-lm/wave-z/models/champion/` (gitignored weights).

**Status: ACTIVE** · Wave Y **COMPLETE** → [wave-y-summary.md](wave-y-summary.md).

## Stage queue

| Stage | ID | Status | Notes |
|------:|----|--------|-------|
| Z0 | **EXPORT** | **DONE** | `champion-qpfb2-v0` = H-ABS-QPFB2 (QT int8 + EARLY + PFB K=2 card) |
| Z1 | **HITL-10** | **NEXT** | Exactly 10 trials; per-trial score + error bank |
| Z2 | MANUAL×10 | queued | Wrapper/few-shot from Z1 errors |
| Z3 | H-ZERR / H-ZWRAP | queued | Retrain or wrap-only |
| Z4 | HITL-10 verify | queued | mean ≥ Z1 + 0.5; pass bar mean≥7, errors≤3 |
| Z5 | LOOP≤3 | queued | — |
| Z6 | REPORT | queued | `wave-z-hitl.md` |

## Z0 evidence

| Artifact | Path |
|----------|------|
| Recipe card | `results/nano-lm/wave-z/models/champion/recipe.json` |
| Manifest | `…/MANIFEST.json` |
| Ckpt | `…/B2_seed0.pt` (from `formal-hdeck-b4`) |
| EARLY gene | `…/genes/HEARLY_seed0_train.json` |
| Public note | [wave-z-export.md](wave-z-export.md) |

Commands:

```bash
npm run nano:z:export
npm run nano:z:ask -- --question "…" --trial Z0-smoke
npm run nano:z:log-trial -- path/to/trial.json
npm run nano:z:error-bank
```

## Doctrine

- Judge = frontier chat model (not ≤5M self-grade).  
- Forbidden: STREAM / KVCACHE-Q / GENCACHE / GPFB K=2 / MIXD retrain.  
- Live checklist: `.local/wave-z/SESSION.md`.
