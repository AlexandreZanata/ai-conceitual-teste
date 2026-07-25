# Nano Student + Teacher — Research Agenda

> Lab-grade protocol. Side track under `nano_lm/`. Caps: ≤80 / ≤200 / cyclo ≤10.

## Focus (what works)

| Role | ID | Notes |
|------|-----|-------|
| Train tip | **H-STAG** | Curriculum `lo=6`, `stages=4` |
| Decode tips | **H-EARLY** / **H-POOL** | Speed / quality@wall |
| Serving systems | **SERVE** (min-wall) / **SROUTE** (Pareto) via **PACK** | wall↓ / quality@tok/s |
| Throughput | **SKIP**+**LAYB** via **BPACK** | tok/s↑ (CBAT demoted) |
| Quality | **FLAYB** via **QPACK** | tok/s↑ vs POOL |
| Train I/O | TOP→…→**PRE3** | ms/step↓ |
| Thin solo | DEPTH / PRUN | not under batch |
| Protocol | MIX / FUSE / PARETO / PACK / BPACK / **QPACK** | not tips |

**Next:** Wave T in `.local/pesquisa.md` — **TPACK** (QPACK smoke+formal PROMOTE).  
Card: [`champion-card.md`](results/nano-lm/champion-card.md).

## Archived KILLs

ASYNC, PINC, GALLF, DEPTHA/B, PRUNB/F, SHORTB, CFUSE, Q4, **ETRAIN** (formal e2e), TOPK, compose, A–H deepeners — code kept for ETRAIN report; older KILL code purged; markdown in [`archive/`](results/nano-lm/archive/).

## Claim rule

Formal: seeds `{0,1,2}`, fit≠eval; beat tip−ε on quality and win wall/tok/s/ms-step as gated.
