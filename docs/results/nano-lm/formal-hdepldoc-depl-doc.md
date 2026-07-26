# H-DEPL-DOC — public one-pager sync (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8.1 AA4 · Wave AA  
> Policy source: [wave-z-depl-y.md](wave-z-depl-y.md) · No new hypotheses

## Hypothesis

Public one-pagers (**RECIPES** · **champion-card** · **NANO-STUDENT-AGENDA** · **DEPL-Y**) stay consistent with frozen DEPL-Y routes and Wave AA outcomes (WRAPBANK **PROMOTE** · PARA **HOLD** · ZPREF **KILL**).

## Gate

| Check | Result |
|-------|--------|
| CORE markers (DEPL-Y / H-PACK / QPFB2 / ROLL / H-ZWRAP / H-ZERR) | **ok** on all four pages |
| AA outcomes on card/RECIPES/agenda | **ok** |
| `hitl_known` route includes **H-WRAPBANK** | **ok** |
| Forbidden list still rejects STREAM/… | **ok** |
| Wrap product smoke (`WRAP_LOOKUP` add) | **ok** |
| Decision | **PROMOTE** |

## Reproduce

```bash
npm run nano:depl-doc
# optional: --skip-ask
npm run nano:z:depl-y
```

## Finding

1. Doc-only closeout for Wave AA — no new serve/train hyps.  
2. Known-ask product string is **H-ZWRAP + H-WRAPBANK** across DEPL-Y + one-pagers.  
3. Wave AA status: **COMPLETE**.

## Artifacts

- Module: `nano_lm/src/depl_doc_ops.py` · Runner: `nano_lm/src/run_depl_doc.py`
- Summary: `results/nano-lm/wave-aa/depl_doc_summary.json`
- Contract: `nano_lm/tests/test_depl_doc.py`
