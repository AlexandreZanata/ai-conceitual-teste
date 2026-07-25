# Nano Student + Teacher — Research Agenda

> Lab-grade protocol. Side track under `nano_lm/`. Not C++ EvoGen Domain.  
> Caps: ≤80 lines/function, ≤200 lines/file, cyclomatic ≤10.

## Honesty clause

Mechanisms are math/code. Every H-ID has a null and a kill criterion.  
**No claims of literal quantum cognition.**

## Hardware lock

| Resource | Cap |
|----------|-----|
| GPU | RTX 4060 Laptop **8 GiB** |
| Teacher (frozen) | `roneneldan/TinyStories-33M` (fp16) |
| Student | **≤5M params**, context ≤512 |
| VRAM stop | **7.0 GiB** peak |
| Data | TinyStories (Eldan & Li, [arXiv:2305.07759](https://arxiv.org/abs/2305.07759)) |

## Baselines (claim gate)

| ID | Name |
|----|------|
| B0–B4 | Floor / CE / KD / AR / BoN — see prior docs |

**Claim rule:** beat B2 (train) or B4 dual-gate (decode) on formal seeds `{0,1,2}` with fit≠eval.

## Focus stack (what works)

| Role | ID | Status |
|------|-----|--------|
| Train tip | **H-STAG** | formal PROMOTE |
| Decode tips | **H-EARLY** / **H-POOL** | formal PROMOTE |
| Systems decode | FLASH / KVSEL / **CHUNK** | formal PROMOTE |
| Throughput | BAT / **POOLB** / **CBAT** | formal PROMOTE |
| Train util | TOP / **PIN** / PRUN / DEPTH | formal PROMOTE |
| Quant | **H-Q4** | smoke PROMOTE / formal **KILL** |
| Protocol | MIX / FUSE / CFUSE | PROTOCOL / CFUSE smoke **KILL** |

**Do not** gene-widen EARLY/POOL or paste tips. Deepen systems/batch/TOP/DEPTH axes only.  
Queue: `.local/pesquisa.md` (**Wave L** — next **H-CHB**; CBAT formal PROMOTE). Card: [`champion-card.md`](results/nano-lm/champion-card.md).

## Archived

A–H deepeners, I/J KILLs, **H-TOPK**, **H-Q4** formal KILL, **H-CFUSE** smoke KILL. [`archive/`](results/nano-lm/archive/).

## Eval

teacher_lp + wall + tok/s + GFLOPs + train ms/step. Matrix: `npm run nano:matrix:report`.
