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
| H-BAL | Lifetime GD + Darwinian inherit | No faster than H-SEL/B2 — **smoke KILL/hold** (≤ B2) |
| H-LAM | Phenotype → genotype write-back | Unstable or loses to H-BAL — **smoke PROMOTE**; **formal KILL** (≤ H-BAL) |
| H-ELI | Strong elitism | Diversity collapse + worse OOD — **smoke KILL/hold** (≤ H-SEL; no collapse) |
| H-FIT | Fitness = teacher_lp on completions (not probe CE) | ≤ H-SEL — **smoke PROMOTE**; **formal KILL** (overfit + ≤ B2) |
| H-TOU | Tournament selection (k=3) vs truncation | ≤ H-SEL — **smoke KILL/hold** |
| H-XOV | Uniform weight crossover then mutate | ≤ H-SEL / collapse — **smoke PROMOTE**; **formal KILL** (≤ B2) |
| H-NIC | Fitness sharing by weight-space crowding | No diversity↑ or quality↓ — **smoke KILL/hold** (tie vs H-SEL; diversity↑) |
| H-MUT | Adaptive mutate scale (1/5 success rule) | Fixed scale wins — **smoke KILL/hold** |
| H-RAN | Linear rank selection vs truncation | ≤ H-SEL — **smoke KILL/hold** |
| H-AGE | Age-layered pops + immigrants (ALPS-lite) | ≤ H-SEL wall-matched — **smoke KILL/hold** |
| H-MOR | Soft mortality (cull bottom quartile) | ≤ H-SEL — **smoke KILL/hold** |
| H-SPE | 2 islands + ring migrate top-1 | ≤ single-island H-SEL — **smoke KILL/hold** |
| H-SEX | Mate choice: high fit × high pairwise L2 | ≤ H-SEL / random pairing — **smoke KILL/hold** |
| H-ANTI | Anti-selection: breed worst half only | ≤ H-SEL / B2 — **smoke KILL/hold** |
| H-TAX | Wealth tax: scale elite weights ×(1−τ) | ≤ H-SEL — **smoke KILL/hold** |
| H-CAN | Winner copies loser LayerNorm stats | No gain / NaN — **smoke KILL/hold** (tie) |
| H-PAR | Parasite vector steals selection credit | Parasite dominates / no host gain — **smoke KILL** |
| H-SYM | Obligate pair: both must beat mean to breed | ≤ H-SEL — **smoke PROMOTE**; **formal KILL** (≤ B2) |
| H-FOS | Fossil vault: resurrect extinct lineage every K gens | ≤ no-resurrect — **smoke KILL/hold** (tie vs H-SEL) |
| H-ZOM | Zombie: reinject dead weights with sign-flipped noise | Diverges / ≤ H-SEL — **smoke KILL/hold** |
| H-LOTU | Underdog lottery: worst gets one free elite clone | ≤ H-SEL — **smoke KILL/hold** |
| H-GLD | Goldilocks: reward mid teacher_lp band | ≤ max-lp fitness — **smoke KILL/hold** (tie vs H-FIT) |
| H-SEA | Seasons: odd gens CE, even gens teacher_lp | ≤ fixed H-FIT — **smoke KILL/hold** |
| H-RPS | RPS niches: cyclic dominance over 3 niches | Collapse to 1 niche — **smoke KILL** |
| H-CAT | Catastrophe: wipe all but top-1 + immigrants | ≤ steady H-SEL — **smoke KILL/hold** |
| H-HIB | Hibernation: skip eval; inherit parent fit × decay | Cheating / ≤ H-SEL — **smoke KILL/hold** |
| H-SHO | Shock: reinit one random child layer after mutate | ≤ plain mutate — **smoke PROMOTE**; **formal KILL** (≤ B2) |
| H-HOLD | Select on fit prompts; eval on disjoint claim prompts | Overfit train≫eval or ≤ B2 — **smoke PROMOTE**; **formal KILL** (overfit + ≤ B2) |
| H-FXS | H-FIT fitness + H-XOV crossover + H-SHO shock | ≤ max(H-FIT,H-XOV) — **smoke KILL/hold** |
| H-LOFI | CE-rank pop; teacher_lp rescore top-k only | Quality < H-FIT or no wall save — **smoke KILL** (wall save; quality↓) |
| H-DEC | Evolve decode knobs | Fixed BoN better — **smoke PROMOTE**; **formal PROMOTE** vs B4 |
| H-LAT | Latency-aware gene fitness `lp − λ·log1p(wall)` | No wall win vs B4 — **smoke KILL** (lp↑, slower) |
| H-LAT2 | H-LAT + λ≥0.4 + n≤2 clamp | No wall win vs B4 — **smoke/formal PROMOTE** |
| H-DECK | Student proxy ranks genes; teacher rescores top-k | < H-DEC−ε or no save — **smoke PROMOTE**; **formal PROMOTE** vs B4 |
| H-DECK2 | Sweep `top_k`∈{1,2,3} equal pop×gens | Best k ≤ H-DECK (k=2) — **smoke KILL**; **formal PROMOTE** (best k=1) |
| H-PROXY2 | Teacher-forced CE proxy vs self-lp | ≤ H-DECK @forwards — **smoke PROMOTE**; **formal KILL** |
| H-CASC | Proxy → short mid teacher → full top-k | No save or ≤ B4 — **smoke PROMOTE**; **formal PROMOTE** |
| H-BAND | UCB1 over fixed gene arms (no mutate) | ≤ H-DECK/H-CASC — **smoke KILL** |
| H-DECKL | DECK search; lat-aware claim (Pareto) | Dominated vs B4 — **smoke/formal PROMOTE** |
| H-POOL | Warm-start pop from other seeds’ best genes | ≤ cold H-DECKL — **smoke/formal PROMOTE** |
| H-PARE | Archive (lp, wall); claim knee of front | Empty front / ≤ B4 — **smoke/formal PROMOTE** |
| H-DECP | Per-prompt gene bank; proxy pick at claim | ≤ global / B4 — **smoke PROMOTE**; **formal KILL** |
| H-DECM | Elite gene mixture; proxy pick completion | ≤ H-LAT2 / B4 — **smoke/formal PROMOTE** |
| H-DECQ | Quantized T/top_p codebook + mixture claim | ≤ H-DECM / B4 — **smoke PROMOTE**; **formal KILL** |
| H-DRAFT/H-BEAM | Evolved draft / beam knobs | No wall win — **smoke KILL** |
| H-EARLY | Confidence early-exit / adaptive length | ≤ B4 / no wall — **smoke/formal PROMOTE** |
| H-STACK/ROUT/ORAC | Tip dual / conf / oracle | no dual — **smoke KILL** |
| H-NGRAM forks | Grid★ / NGE / ×EARLY / ×DECM | NGRAM★; all stacks **smoke KILL** |

### B — Inference as learning
| ID | Mechanism | Kill if |
|----|-----------|---------|
| H-BON/H-MAE | Distill BoN / MAE winners | No gain vs B2 |
| H-SPEC | Student draft; teacher accept/reject | No speedup — **smoke KILL** |
| H-TKD | Top-k sparse KD (teacher mass on k) | ≤ B2 — **smoke PROMOTE**; **formal KILL** |
| H-CLIP / H-LS | Logit clip / label-smooth KD | ≤ B2 — both **smoke KILL** |

### C — Quantum-inspired (classical only)
| ID | Mechanism | Kill if |
|----|-----------|---------|
| H-SUP | Amplitude weights over K futures; collapse by \|α\|² / score | Uniform BoN ≥ |
| H-INT | Signed/phase interference scores | No better than softmax BoN |
| H-ENT | Dual heads, shared noise | Collapses to one head — **smoke KILL** (TV≈0.005) |
| H-ENT2 | Dual heads + TV floor loss (punish TV < τ) | Collapses again or ≤ B2 — **smoke KILL** (collapsed again) |
| H-ENT3 | Maximize TV (disagreement) + KD on mix | Mode chaos / ≤ B2 — **smoke KILL** (collapsed) |
| H-ANN | Annealing schedule vs cosine | Cosine wins — **smoke/formal PROMOTE** (Δ+0.15 vs KD-cos; still ≪ B2) |

### D — Plasticity
| ID | Mechanism | Kill if |
|----|-----------|---------|
| H-HEB | Local Hebbian layers | Diverges or ≪ B2 — **smoke KILL** (≤ B2) |
| H-EPI | Context-dependent LR/masks | No better than fixed LR — **smoke KILL** (≤ B2) |
| H-LOT | Sparse lottery ticket | Quality cliff — **smoke PROMOTE**; **formal KILL** (cliff) |

### E — Memory / non-AR
| ID | Mechanism | Kill if |
|----|-----------|---------|
| H-HOP | Tiny Hopfield prior | No gain vs deeper AR — **smoke PROMOTE**; **formal KILL** |
| H-BLK | Block-parallel decode | Quality crash — **smoke KILL** (no speedup vs B3) |
| H-DIF | Discrete diffusion nano | Too slow/VRAM — **smoke KILL** (≤ B2 Δ−0.72) |

### F — Multi-agent
| ID | Mechanism | Kill if |
|----|-----------|---------|
| H-ADV | Discriminator + teacher judge | Mode collapse — **smoke KILL** (≤ B2; no collapse) |
| H-DEB | Dual student; teacher picks | No gain vs B2 — **smoke PROMOTE**; **formal KILL** |

## Out of scope
Literal quantum claims; teacher >33M in wave 1; GPT-4 judge as required gate; merge into C++ Domain.

## Eval (preregistered)
- **Primary:** teacher length-normalized log-prob / NLL on student completions
- **Secondary:** distinct-1/2, wall-ms, token-evals, VRAM peak, tokens/s
- Smoke: `nano_lm/prompts/smoke_prompts.yaml`; formal: `eval_prompts.yaml`
- Reports: `results/nano-lm/` + `docs/results/nano-lm/`

## Waves

| Wave | Status target |
|------|----------------|
| 0 | This agenda + phase 11 refs |
| 1 | Student ≤5M + B0–B2 |
| 2 | H-SEL, H-BON, H-MAE vs B2 |
| 3 | H-SUP (+ H-INT) vs uniform BoN |
| 4 | Kill/promote matrix |
| 5 | B3/B4 decode controls + H-SPEC vs B3 (smoke KILL) |
| 6 | H-BAL Baldwin vs B2 (smoke KILL/hold) |
| 7 | H-DEC evolve decode knobs vs B4 (smoke PROMOTE; **formal PROMOTE** Δ+2.43) |
| 8 | H-LAM Lamarckian write-back vs H-BAL (smoke PROMOTE; **formal KILL** — Δ−0.12) |
| 9 | H-ELI strong elitism vs H-SEL (smoke KILL/hold — ≤ H-SEL) |
| 10 | H-ENT dual heads (smoke KILL — collapsed to one head) |
| 11 | H-ANN anneal vs cosine KD (smoke/formal PROMOTE Δ+0.15; ≪ B2) |
| 12 | H-FIT teacher_lp fitness vs H-SEL (smoke PROMOTE; **formal KILL** — overfit + Δ−1.84) |
| 13 | H-TOU tournament vs H-SEL truncation (smoke KILL/hold) |
| 14 | H-XOV weight crossover vs H-SEL (smoke PROMOTE; **formal KILL** — Δ−1.65 vs B2) |
| 15 | H-NIC fitness sharing vs H-SEL (smoke KILL/hold — tie) |
| 16 | H-MUT adaptive mutate vs H-SEL (smoke KILL/hold) |
| 17 | H-RAN rank selection vs H-SEL (smoke KILL/hold) |
| 18 | H-AGE age layers vs H-SEL (smoke KILL/hold) |
| 19 | H-MOR soft mortality vs H-SEL (smoke KILL/hold) |
| 20 | H-SPE island migration vs H-SEL (smoke KILL/hold) |
| 21 | H-SEX mate choice vs H-SEL (smoke KILL/hold) |
| 22 | H-ANTI anti-selection vs H-SEL (smoke KILL/hold) |
| 23 | H-TAX wealth tax vs H-SEL (smoke KILL/hold) |
| 24 | H-CAN LN cannibalism vs H-SEL (smoke KILL/hold — tie) |
| 25 | H-PAR parasite genome vs H-SEL (smoke KILL — dominates) |
| 26 | H-SYM obligate pair vs H-SEL (smoke PROMOTE; **formal KILL** — Δ−1.66 vs B2) |
| 27 | H-FOS fossil vault vs H-SEL (smoke KILL/hold — tie) |
| 28 | H-ZOM zombie reinject vs H-SEL (smoke KILL/hold) |
| 29 | H-LOTU underdog lottery vs H-SEL (smoke KILL/hold) |
| 30 | H-GLD Goldilocks vs H-FIT (smoke KILL/hold — tie) |
| 31 | H-SEA seasonal fitness vs H-FIT (smoke KILL/hold) |
| 32 | H-RPS RPS niches vs H-SEL (smoke KILL — niche collapse) |
| 33 | H-CAT catastrophe vs H-SEL (smoke KILL/hold) |
| 34 | H-HIB hibernation vs H-SEL (smoke KILL/hold) |
| 35 | H-SHO layer shock vs H-SEL (smoke PROMOTE; **formal KILL** — Δ−1.86 vs B2) |
| 36 | H-HOLD holdout fitness vs B2 (smoke PROMOTE; **formal KILL** — overfit + Δ−1.84) |
| 37 | H-FXS FIT×XOV×SHO stack vs max(FIT,XOV) (smoke KILL/hold) |
| 38 | H-LOFI CE top-k + teacher rescore vs H-FIT (smoke KILL — quality↓) |
| 39 | H-ENT2 dual-head TV floor vs B2 (smoke KILL — collapsed again) |
| 40 | H-ENT3 max-TV + mix KD vs B2 (smoke KILL — collapsed) |
| 41 | Formal H-HOLD vs B2 (KILL — overfit + reverse smoke Δ−1.84) |
| 42 | Formal H-XOV vs B2 (KILL — reverse smoke Δ−1.65; no collapse) |
| 43 | Formal H-FIT vs B2 (KILL — overfit + reverse smoke Δ−1.84) |
| 44 | Formal H-SYM vs B2 (KILL — reverse smoke Δ−1.66) |
| 45 | Formal H-DEC vs B4 (PROMOTE confirmed — Δ+2.43; no overfit) |
| 46 | Formal H-SHO vs B2 (KILL — reverse smoke Δ−1.86) |
| 47 | Formal H-LAM vs H-BAL (KILL — reverse smoke Δ−0.12; also ≤ B2) |
| 48 | H-LAT latency-aware decode vs B4 (**smoke KILL** — no speedup) |
| 49 | H-DECK proxy+top-k decode vs B4 (**smoke PROMOTE**; **formal PROMOTE** Δ+2.53) |
| 50 | H-DECK2 top_k∈{1,2,3} ablation (**smoke KILL**; **formal PROMOTE** — best k=1 Δ+0.25 vs k=2) |
| 51 | H-PROXY2 CE proxy vs H-DECK self-lp (**smoke PROMOTE**; **formal KILL** — Δ−0.11) |
| 52 | H-CASC proxy→mid→full vs B4 (**smoke PROMOTE**; **formal PROMOTE** Δ+2.27) |
| 53 | H-BAND UCB1 gene arms vs H-CASC/H-DECK (**smoke KILL**) |
| 54 | H-DECKL DECK+lat claim vs B4 (**smoke/formal PROMOTE** — Pareto-dominates) |
| 55 | H-POOL cross-seed warm-start (**smoke/formal PROMOTE** Δ+0.04 vs cold H-DECKL) |
| 56 | H-PARE Pareto archive + knee claim (**smoke/formal PROMOTE** — dominates B4 Δ+2.14) |
| 57 | H-LAT2 λ≥0.4 + n≤2 vs B4 (**smoke/formal PROMOTE** — Δ+2.39 + wall win) |
| 58 | H-DECP per-prompt gene bank (**smoke PROMOTE**; **formal KILL** — ≤ GLOBAL) |
| 59 | H-DECM elite gene mixture (**smoke/formal PROMOTE** — > H-LAT2 Δ+0.34) |
| 60 | H-DECQ quantized gene codes (**smoke PROMOTE**; **formal KILL** — ≤ H-DECM) |
| 61 | NGRAM★; NGE/NGRE/NGDM stacks **KILL**; TKD formal KILL |
## Success
≥1 H-ID beats B2 quality **or** tokens/s at budget (+ ablation). Negatives logged.
