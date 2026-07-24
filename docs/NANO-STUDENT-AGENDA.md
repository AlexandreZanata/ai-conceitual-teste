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
| Train | **H-STAG** | PROMOTE (`n_stages=4` @ lo=6) | Official train tip |
| Train parents | H-CURL2 ← H-CURL ← H-CUR | PROMOTE lineage | Keep for ablations |
| Decode speed | **H-EARLY** | PROMOTE vs B4 | Official fast |
| Decode quality@wall | **H-POOL** | PROMOTE vs H-DECKL | Official quality@wall |
| Decode parents | H-DECKL ← H-DECK ← H-DEC | PROMOTE vs B4 | Search lineage |
| Metrics | **H-FLOP** | smoke PROMOTE | wall + tok/s + est GFLOPs |
| Wave I | **H-LAY** | smoke PROMOTE (formal deferred) | layer skip; GFLOPs tie |
| Wave I | **H-AMP** | smoke **KILL** | CUDA bf16 autocast; quality+wall fail |
| Wave I | **H-TIE** | smoke **KILL** | shared block; quality < STAG−ε |
| Wave I | **H-PRUN** | smoke PROMOTE (formal deferred) | 30% mag prune; density FLOPs |
| Wave I | **H-WIN** | smoke **KILL** | local window=32; quality < STAG−ε |
| Wave I | **H-SHORT** | smoke PROMOTE (formal deferred) | short draft; GFLOPs tie |
| Wave I | **H-SOFT** | smoke **KILL** | soft cache; train ms/step↑ |
| Wave I | **H-BAT** | smoke PROMOTE (formal deferred) | batched tok/s↑; tip unchanged |

Protocol: train **H-STAG**, decode **H-EARLY** or **H-POOL**. Never paste tips (SYS/JOINT/CACHE/CAP KILL).  
Wave I complete: **H-LAY** / **H-PRUN** / **H-SHORT** / **H-BAT** smoke PROMOTE (formal deferred); **H-AMP** / **H-TIE** / **H-WIN** / **H-SOFT** smoke **KILL**. Next: `.local/pesquisa.md`. Card: [`champion-card.md`](results/nano-lm/champion-card.md).

## Archived hypotheses

Weight-evo, compose kills, and Waves A–H deepeners (EAR2/BUD/THIN/…/HOR/CURL3) were **purged** from active `nano_lm/` code. Markdown: [`docs/results/nano-lm/archive/`](results/nano-lm/archive/).

## Eval

- Primary: teacher length-normalized log-prob  
- Secondary: wall-ms, token-evals, VRAM, tokens/s, **est. GFLOPs** (`npm run nano:flop`)  
- Matrix: `npm run nano:matrix` / `npm run nano:matrix:report`

## Success

Frozen tips beat B2 / B4 under the protocol. Negatives archived as science wins.
