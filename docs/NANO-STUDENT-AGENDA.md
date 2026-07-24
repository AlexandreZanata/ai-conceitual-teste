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
| Train | **H-CURL** | PROMOTE (`seq_lo=8` > H-CUR) | Official train tip |
| Train parent | H-CUR | PROMOTE vs B2 Δ+1.19 | Curriculum KD |
| Decode speed | **H-EARLY** / EAR2 / BUD / THIN / Q8 | EARLY★; others smoke/formal **KILL** | Q8 INT8 no wall win |
| Decode quality@wall | **H-POOL** | PROMOTE vs cold H-DECKL | Warm-start; `top_k=1` |
| Decode parents | H-DECKL / H-DECK / H-DEC | PROMOTE vs B4 | Search lineage |

Protocol: train with **H-CURL**, decode with **H-EARLY** (speed) or **H-POOL** (quality@wall). Compose H-IDs smoke **KILL**.  
H-EAR2 / H-BUD / H-Q8 smoke **KILL**; H-THIN formal **KILL**. Next: `.local/pesquisa.md` (**A2 H-EARS**). Card: [`champion-card.md`](results/nano-lm/champion-card.md).

## Archived hypotheses

Weight-evo, ENT*, absurd selection ops, KD cosmetics, compose kills, and non-champion decode siblings were **purged from active `nano_lm/` code**. Result markdown lives under [`docs/results/nano-lm/archive/`](results/nano-lm/archive/).

## Eval

- Primary: teacher length-normalized log-prob on student completions  
- Secondary: wall-ms, token-evals, VRAM, tokens/s  
- Fit: `nano_lm/prompts/fit_prompts.yaml`; formal: `eval_prompts.yaml`  
- Matrix: `npm run nano:matrix` / `npm run nano:matrix:report`

## Success

Frozen tips beat B2 (train) and B4 (decode dual gate) under the protocol above. Negatives archived as science wins.
