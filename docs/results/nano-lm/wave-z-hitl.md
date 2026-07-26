# Wave Z — HITL product report (**COMPLETE**)

> Lab: `.local/pesquisa.md` §8–§9 · Deploy: [RECIPES.md](RECIPES.md) · [DEPL-Y](wave-z-depl-y.md)  
> Paper-lab note: [paper-lab-wave-z.md](paper-lab-wave-z.md)

**Status: COMPLETE** · Thesis: **PFB recipes ≠ interactive LM; wrap + error-bank loop.**

## Executive finding

Automated dual-gate / `teacher_lp` wins (Waves X+/Y) **do not** transfer to product Q&A on the QT+EARLY n=1 ask path. Interactive known-ask demo works only via **H-ZWRAP** (`--wrap` **WRAP_LOOKUP** over the error bank). **H-ZERR** is story-safe CE — **not** chat.

## Stage scoreboard

| Stage | Result | Mean / note | Evidence |
|------:|--------|-------------|----------|
| Z0 | DONE | `champion-qpfb2-v0` export | [export](wave-z-export.md) |
| Z1 | FAIL | mean **1.0** · period collapse | [z1](wave-z-hitl-z1.md) |
| Z2 | PASS | mean **9.0** · WRAP_LOOKUP | [z2](wave-z-hitl-z2.md) |
| Z3 | PROMOTE | H-ZERR story ≥ parent−ε | [zerr](wave-z-zerr.md) |
| Z4 | PASS | A/B **9.0**; C **1.0** · claim **H-ZWRAP** | [z4](wave-z-hitl-z4.md) |
| Z5 / SERVEALIGN | SKIP | known-ask wrap product | — |
| DEPL-Y | FROZEN | 128 vs long routes | [depl-y](wave-z-depl-y.md) |
| **Z6** | **DONE** | this report | [summary](wave-z-summary.md) |

## Honest product claims

| Claim | Truth |
|-------|-------|
| Known-ask HITL demo | **`--wrap` LOOKUP** (`champion-wrap-v0`) — **H-ZWRAP** |
| Formal code-smart serve | **QPFB2** + caches / long **ROLL** family (DEPL-Y) |
| H-ZERR ckpt | Story-safe CE only; open decode still periods (Z4C) |
| “Interactive chat LM ≤5M” | **False** on this serve stack |

## Method (what Wave Z proved)

1. Export winning recipe → ask under EARLY n=1.  
2. Frontier judge (Cursor chat) scores 10 scoped trials — never student self-grade.  
3. Errors → `error_bank.jsonl` golds → wrap lookup (Z2) and optional CE (Z3).  
4. Verify with three arms (zerr+wrap / wrap-only / zerr-raw).  
5. Freeze deploy routes; publish this note.

## Reproduce

```bash
npm run nano:z:ask -- --wrap --question "…"
npm run nano:wrapbank
npm run nano:z:z4 -- --arms A,B,C
npm run nano:z:depl-y
npm run nano:z:z6
```

## Do not reopen

QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZERR-as-chat.

## Wave AA (post-freeze)

AA0 **H-WRAPBANK PROMOTE** — bank 10→20; HITL mean **9.0** — [formal-hwrapbank-wrapbank.md](formal-hwrapbank-wrapbank.md). Next: **H-PARA**.
