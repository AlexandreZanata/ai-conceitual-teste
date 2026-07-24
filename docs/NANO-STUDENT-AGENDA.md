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
| B0 | Random-init student AR (floor) |
| B1 | Supervised CE on TinyStories |
| B2 | KD (KL to teacher logits) |
| B3 | B2 + AR decode |
| B4 | B2 + Best-of-N |

**Claim rule:** beat B2 (train) or B4 dual-gate (decode) on formal seeds `{0,1,2}` with fit≠eval.

## Champion tips (active code)

| Role | ID | Formal | Notes |
|------|-----|--------|-------|
| Train | **H-STAG** | PROMOTE | Official train (`lo=6`, `stages=4`) |
| Train parents | H-CURL2 ← H-CURL ← H-CUR | PROMOTE lineage | Ablations |
| Decode speed | **H-EARLY** | PROMOTE vs B4 | Official fast |
| Decode quality@wall | **H-POOL** | PROMOTE vs H-DECKL | Official quality@wall |
| Decode parents | H-DECKL ← H-DECK ← H-DEC | PROMOTE vs B4 | Search lineage |
| Utils | H-LAY / H-PRUN / H-SHORT / H-BAT / **H-TOP** | formal PROMOTE | tip unchanged |
| Metrics | **H-FLOP** | smoke PROMOTE | wall + tok/s + GFLOPs |

Protocol: train **H-STAG**, decode **H-EARLY** or **H-POOL**. Never paste tips.  
Next queue: `.local/pesquisa.md` (Wave J → **H-REP**). Card: [`champion-card.md`](results/nano-lm/champion-card.md).

## Archived hypotheses

Waves A–H deepeners + Wave I KILLs (WIN/TIE/AMP/SOFT) purged from `nano_lm/`.  
Wave J: **H-BUCKET** smoke **KILL** (tok/s↓ vs H-BAT).  
Markdown: [`docs/results/nano-lm/archive/`](results/nano-lm/archive/) + [`hbucket-vs-hbat.md`](results/nano-lm/hbucket-vs-hbat.md).

## Eval

- Primary: teacher length-normalized log-prob  
- Secondary: wall-ms, tokens/s, **est. GFLOPs**, train ms/step (H-TOP)  
- Matrix: `npm run nano:matrix` / `npm run nano:matrix:report`

## Success

Frozen tips beat B2 / B4. Utils may win wall/tok/s without replacing tip. Negatives archived.
