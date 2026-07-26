# Wave Z — HITL product eval (in progress)

> Lab: `.local/pesquisa.md` §9.  
> Champion export: `results/nano-lm/wave-z/models/champion/` (gitignored weights).

**Status: ACTIVE** · Wave Y **COMPLETE** → [wave-y-summary.md](wave-y-summary.md).

## Stage queue

| Stage | ID | Status | Notes |
|------:|----|--------|-------|
| Z0 | **EXPORT** | **DONE** | `champion-qpfb2-v0` = H-ABS-QPFB2 (QT int8 + EARLY + PFB K=2 card) |
| Z1 | **HITL-10** | **DONE — FAIL** | mean **1.0**, errors **10**/10 → [wave-z-hitl-z1.md](wave-z-hitl-z1.md) |
| Z2 | MANUAL×10 | **NEXT** | Wrapper/few-shot/decode from Z1 error bank |
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

## Z1 evidence

| Artifact | Path |
|----------|------|
| Trials | `results/nano-lm/wave-z/trials/Z1-01.json` … `Z1-10.json` |
| Error bank | `results/nano-lm/wave-z/error_bank.jsonl` (10 rows) |
| Summary | `results/nano-lm/wave-z/z1_summary.json` |
| Public note | [wave-z-hitl-z1.md](wave-z-hitl-z1.md) |

**Finding:** QT+EARLY greedy ask collapses to period tokens; formal dual-gate ≠ product Q&A.

Commands:

```bash
npm run nano:z:export
npm run nano:z:ask -- --question "…" --trial Z1-01
npm run nano:z:log-trial -- results/nano-lm/wave-z/trials/Z1-01.json
npm run nano:z:error-bank
```

## Doctrine

- Judge = frontier chat model (not ≤5M self-grade).  
- Forbidden: STREAM / KVCACHE-Q / GENCACHE / GPFB K=2 / MIXD retrain.  
- Live checklist: `.local/wave-z/SESSION.md`.
