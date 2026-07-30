# Quantum-inspired hypothesis ledger

> One row per hypothesis. **No narrative.** Readable in thirty seconds.
> Protocol: [P13](pipeline/P13-quantum-inspired-training-lab.md). Falsifications appear here as prominently as promotions.

**There is no quantum hardware.** Every entry is a classical algorithm inspired by quantum mechanics, benchmarked against the classical technique it most resembles. A hypothesis that beats `N32-base` but not its named control is **falsified**.

---

## Ledger

| ID | Hypothesis | Named control | Predicted | Measured | Verdict | Artifact |
|---|---|---|---|---|---|---|
| Q1 | Tensor-train FFN | Low-rank `UV^T`, equal params | −0.01 to −0.03 BPB | — | pending | — |
| Q2 | Entanglement-entropy diagnostic | Attention entropy probes | Entropy peaks at global layers | — | pending | — |
| Q3 | Transverse-field annealing | SGD + linear-decay Gaussian noise | ≤0.005 BPB (expect falsify) | — | pending | — |
| Q4 | Born-rule output layer | Softmax, equal params | ~equal BPB, better calibration | — | pending | — |
| Q5 | Amplitude-amplification decoding | Top-k speculative decoding | No gain (expect falsify) | — | pending | — |
| Q6 | Simulated VQC layer | Givens-rotation orthogonal matrix | ~equal (expect falsify) | — | pending | — |
| Q7 | Unitary recurrent memory | Diagonal-complex SSM, equal params | −0.01 to −0.02 BPB @16–32k | — | pending | — |
| Q8 | Dequantized embedding compression | Truncated SVD, same rank | ~equal | — | pending | — |
| Q9 | Interference routing MoE | Soft top-k gating, learned temperature | Small gain on mixed data | — | pending | — |
| Q10 | Density-matrix purity abstention | Attention entropy / max-logit | +0.05 AUROC | — | pending | — |
| Q11 | Imaginary-time LR schedule | P07-tuned cosine | ≤0.005 BPB | — | pending | — |
| Q12 | Path-integral decoding | Beam search, equal width | Better sequence log-likelihood | — | pending | — |

---

## Status

| | Count |
|---|---:|
| Resolved | **0** |
| `PROMOTE` | 0 |
| `FALSIFY` | 0 |
| `INCONCLUSIVE` | 0 |
| **Gate ([P13](pipeline/P13-quantum-inspired-training-lab.md))** | **≥8 resolved** |

**A gate that passes with 8 falsifications and 0 promotions is a full `PASS`.** The stage measures whether the questions were answered, not whether the answers were flattering.

## Recording rules

1. Fill `Predicted` and commit **before** running. A prediction added afterwards is not a prediction.
2. `Measured` cites a JSON path under `results/quantum/`.
3. `INCONCLUSIVE` at most twice per hypothesis, then it becomes `FALSIFY`.
4. Every `FALSIFY` is also appended to [`negative_results.md`](negative_results.md).
5. Rows are never deleted.
