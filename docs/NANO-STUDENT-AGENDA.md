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

**Claim rule:** beat B2 (train) or B4 dual-gate (decode: quality ≥ B4−ε **and** wall < B4) on formal seeds `{0,1,2}` with fit≠eval.

## Champion tips (active code)

| Role | ID | Formal | Notes |
|------|-----|--------|-------|
| Train | **H-CURL2** | PROMOTE (`seq_lo=6` > H-CURL lo=8) | Official train tip |
| Train deepeners | H-CURD / H-STEP / H-ALAT | formal/smoke **KILL** | NLL bins; early-stop; α/T |
| Train parents | H-CURL / H-CUR | PROMOTE lineage | lo=8 / curriculum KD |
| Decode speed | **H-EARLY** (+ EAR2/BUD/…/EXIT/MID) | EARLY★; deepeners smoke/formal **KILL** | MID reverse smoke |
| Decode quality@wall | **H-POOL** (+ POOL2/PROX/POOLF) | POOL★; POOL2/PROX smoke **KILL**; POOLF formal **KILL** | n≤2 FLOP cut fails claim |
| Decode parents | H-DECKL / H-DECK / H-DEC | PROMOTE vs B4 | Search lineage |
| Instrumentation | **H-FLOP** | smoke **PROMOTE** | wall + tok/s + est GFLOPs |

Protocol: train with **H-CURL2** (`seq_lo=6`), decode with **H-EARLY** (speed) or **H-POOL** (quality@wall). Compose H-IDs smoke **KILL**.  
H-EAR2 / H-BUD / H-Q8 / H-EARS / H-COMP / H-PROX / H-POOL2 / H-STEP / H-ALAT / H-EARF / H-EXIT smoke **KILL**; H-MID / H-POOLF smoke PROMOTE / formal **KILL**; H-THIN / H-CURD formal **KILL**. H-FLOP instrumentation **PROMOTE**. Queue: `.local/pesquisa.md`. Card: [`champion-card.md`](results/nano-lm/champion-card.md).

## Archived hypotheses

Weight-evo, ENT*, absurd selection ops, KD cosmetics, compose kills, and non-champion decode siblings were **purged from active `nano_lm/` code**. Result markdown lives under [`docs/results/nano-lm/archive/`](results/nano-lm/archive/).

## Eval

- Primary: teacher length-normalized log-prob on student completions  
- Secondary: wall-ms, token-evals, VRAM, tokens/s, **est. GFLOPs** (`npm run nano:flop`)  
- Fit: `nano_lm/prompts/fit_prompts.yaml`; formal: `eval_prompts.yaml`  
- Matrix: `npm run nano:matrix` / `npm run nano:matrix:report`

## Success

Frozen tips beat B2 (train) and B4 (decode dual gate) under the protocol above. Negatives archived as science wins.
