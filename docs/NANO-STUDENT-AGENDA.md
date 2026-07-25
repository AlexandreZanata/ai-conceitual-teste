# Nano Student + Teacher — Research Agenda

> Lab-grade protocol. Side track under `nano_lm/`. Caps: ≤80 / ≤200 / cyclo ≤10.

## Focus (what works)

| Role | ID | Notes |
|------|-----|-------|
| Train tip | **H-STAG** | Curriculum `lo=6`, `stages=4` |
| Decode tips | **H-EARLY** / **H-POOL** | Speed / quality@wall |
| Serving systems | FLASH→CHUNK→**CHB**; GRAPH→GRAPHF; **GALL** | wall↓ |
| Throughput | BAT…→**LAYB**; POOLB…→**FLAYB** | tok/s↑ |
| Train I/O | TOP→…→**PRE2** (+ **PRE3**) | ms/step↓ |
| Thin solo | DEPTH / PRUN | not under batch |
| Protocol | MIX / FUSE | not tips |

**Next:** Wave R in `.local/pesquisa.md` — **PRE3 → SERVE → ETRAIN → ROUTE**.  
Card: [`champion-card.md`](results/nano-lm/champion-card.md).

## Archived KILLs

ASYNC, PINC, GALLF, DEPTHA/B, PRUNB/F, SHORTB, CFUSE, Q4, TOPK, compose, A–H deepeners — code purged; markdown in [`archive/`](results/nano-lm/archive/).

## Claim rule

Formal: seeds `{0,1,2}`, fit≠eval; beat tip−ε on quality and win wall/tok/s/ms-step as gated.
