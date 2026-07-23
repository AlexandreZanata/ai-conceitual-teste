# Nano Student + Teacher — Research Agenda

> Lab-grade protocol. Side track under `nano_lm/`. Not C++ EvoGen Domain.  
> Caps: ≤80 lines/function, ≤200 lines/file, cyclomatic ≤10.

## Honesty clause

Mechanisms are math/code. Every H-ID has a null and a kill criterion.  
Novelty = ultra-small student + TinyStories teacher + wild operators under one protocol — not “never tested in ML history.”  
**No claims of literal quantum cognition.**

## Hardware lock

| Resource | Cap |
|----------|-----|
| GPU | RTX 4060 Laptop **8 GiB** |
| Teacher (frozen) | `roneneldan/TinyStories-33M` (fp16) |
| Student | **≤5M params**, context ≤512 |
| VRAM stop | **7.0 GiB** peak |
| Data | TinyStories (Eldan & Li, [arXiv:2305.07759](https://arxiv.org/abs/2305.07759)) |

## System

Frozen teacher → soft labels / scores → hypothesis operator → trainable student → eval (teacher NLL + speed).

## Baselines (claim gate)

| ID | Name |
|----|------|
| B0 | Random-init student AR (floor) |
| B1 | Supervised CE on TinyStories |
| B2 | KD (KL to teacher logits) |
| B3 | B2 + AR decode (decode control) |
| B4 | B2 + Best-of-N (decode control) |

**Claim rule:** wild H-ID must beat B2 on quality@budget **or** match B2 quality at lower wall/FLOPs (seeds ≥3 for formal; smoke may use fewer).  
**H-SPEC gate:** tokens/s > B3 **and** teacher_lp ≥ B3 − ε (ε=0.05 smoke).

## Hypothesis catalog

### A — Selection / evolution

| ID | Mechanism | Kill if |
|----|-----------|---------|
| H-SEL | Population; fitness = teacher NLL; tournament + mutate | Equal-FLOPs B2 wins |
| H-BAL | Lifetime GD + Darwinian inherit | No faster than H-SEL/B2 |
| H-LAM | Phenotype → genotype write-back | Unstable or loses to H-BAL |
| H-ELI | Strong elitism | Diversity collapse + worse OOD |
| H-DEC | Evolve decode knobs | Fixed BoN better |

### B — Inference as learning

| ID | Mechanism | Kill if |
|----|-----------|---------|
| H-BON | Distill teacher-chosen BoN winners | No gain vs B2 |
| H-MAE | Distill lookahead MAE commits | BoN distill cheaper/better |
| H-SPEC | Student draft; teacher accept/reject | No speedup or quality drop — **smoke KILL** (no speedup vs B3) |

### C — Quantum-inspired (classical only)

| ID | Mechanism | Kill if |
|----|-----------|---------|
| H-SUP | Amplitude weights over K futures; collapse by \|α\|² / score | Uniform BoN ≥ |
| H-INT | Signed/phase interference scores | No better than softmax BoN |
| H-ENT | Dual heads, shared noise | Collapses to one head |
| H-ANN | Annealing schedule vs cosine | Cosine wins |

### D — Plasticity

| ID | Mechanism | Kill if |
|----|-----------|---------|
| H-HEB | Local Hebbian layers | Diverges or ≪ B2 |
| H-EPI | Context-dependent LR/masks | No better than fixed LR |
| H-LOT | Sparse lottery ticket | Quality cliff |

### E — Memory / non-AR

| ID | Mechanism | Kill if |
|----|-----------|---------|
| H-HOP | Tiny Hopfield prior | No gain vs deeper AR |
| H-BLK | Block-parallel decode | Quality crash |
| H-DIF | Discrete diffusion nano | Too slow/VRAM |

### F — Multi-agent

| ID | Mechanism | Kill if |
|----|-----------|---------|
| H-ADV | Discriminator + teacher judge | Mode collapse |
| H-DEB | Dual student; teacher picks | No gain vs B2 |

## Out of scope

Literal quantum claims; teacher >33M in wave 1; GPT-4 judge as required gate; merge into C++ Domain.

## Eval (preregistered)

- **Primary:** teacher length-normalized log-prob / NLL on student completions  
- **Secondary:** distinct-1/2, wall-ms, token-evals, VRAM peak, tokens/s  
- Smoke prompts: `nano_lm/prompts/smoke_prompts.yaml`; formal: `eval_prompts.yaml`  
- Report paths under `results/nano-lm/` + `docs/results/nano-lm/`

## Waves

| Wave | Status target |
|------|----------------|
| 0 | This agenda + phase 11 refs |
| 1 | Student ≤5M + B0–B2 |
| 2 | H-SEL, H-BON, H-MAE vs B2 |
| 3 | H-SUP (+ H-INT) vs uniform BoN |
| 4 | Kill/promote matrix |
| 5 | B3/B4 decode controls + H-SPEC vs B3 (smoke KILL) |

## Success

≥1 non-baseline H-ID improves teacher-judged quality **or** tokens/s vs B2 at fixed budget, with ablation. Negatives are logged wins for science.
