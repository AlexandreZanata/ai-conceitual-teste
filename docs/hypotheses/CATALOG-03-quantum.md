# Catalogue 03 — Quantum- and physics-inspired (T041–T060)

> Format and rules: [README](README.md). Active testing programme: [P13](../pipeline/P13-quantum-inspired-training-lab.md).
>
> **There is no quantum computer here.** Every entry is a classical algorithm inspired by physics. Entries T041–T052 correspond to hypotheses Q1–Q12 in [P13](../pipeline/P13-quantum-inspired-training-lab.md#3-the-hypothesis-set), where each is specified in full with its named classical control. **The anti-quantum-washing rule applies:** an entry is admissible only if it names the classical technique it most resembles and beats it.

---

### T041 — Tensor-train FFN *(= [Q1](../pipeline/P13-quantum-inspired-training-lab.md#q1--tensor-train-ffn-mps-weight-factorization))*
**Core.** Factor FFN weight matrices as matrix product states with bond dimension χ, giving `O(d·χ²)` parameters instead of `O(d²)`.
**Better because.** Captures multiplicative structure that plain low-rank `UV^T` cannot represent, with a theoretically motivated capacity knob from DMRG.
**Kill test.** Does not beat plain low-rank factorization at equal parameter count.
`Cost: M · Serves: light`

### T042 — Entanglement-entropy diagnostic *(= [Q2](../pipeline/P13-quantum-inspired-training-lab.md#q2--entanglement-entropy-as-a-context-diagnostic))*
**Core.** Compute von Neumann entropy of the singular-value spectrum of cross-block attention to measure information flow across a context cut.
**Better because.** It is a measurement, not a method — it localizes *which layer* stops transmitting long-range information, replacing the "global layer every 6th" guess with evidence.
**Kill test.** Provides no information beyond ordinary attention-weight inspection.
`Cost: S · Serves: long`

### T043 — Transverse-field annealing *(= [Q3](../pipeline/P13-quantum-inspired-training-lab.md#q3--transverse-field-annealing-schedule))*
**Core.** Gradient noise with amplitude decaying as a transverse field would in quantum annealing.
**Better because.** Barrier tunnelling depends on barrier width, not only height, suggesting a different noise schedule from thermal annealing.
**Kill test.** Indistinguishable from SGD with a linearly decaying Gaussian noise schedule. *(Predicted outcome: falsified.)*
`Cost: S · Serves: quality`

### T044 — Born-rule output layer *(= [Q4](../pipeline/P13-quantum-inspired-training-lab.md#q4--born-rule-output-layer))*
**Core.** Emit signed amplitudes ψ; token probability is `ψ²/Σψ²` rather than softmax over logits.
**Better because.** Softmax cannot express cancellation — every contribution strictly increases probability. Signed amplitudes let two evidence pathways destructively interfere and actively suppress a token.
**Kill test.** Worse BPB **and** no calibration improvement over softmax.
`Cost: S · Serves: quality`

### T045 — Unitary recurrent memory *(= [Q7](../pipeline/P13-quantum-inspired-training-lab.md#q7--unitary-recurrent-memory-for-long-context))*
**Core.** A recurrent state updated by a learned unitary (Householder or Cayley parameterization) running alongside sliding-window attention.
**Better because.** All singular values equal 1, so gradients neither vanish nor explode over arbitrary length — and the channel carries long-range information with **no KV growth**.
**Kill test.** Does not beat a diagonal-complex SSM of equal parameter count on positional BPB.
`Cost: L · Serves: long, light`

### T046 — Density-matrix attention with purity abstention *(= [Q10](../pipeline/P13-quantum-inspired-training-lab.md#q10--density-matrix-attention-with-purity-based-abstention))*
**Core.** Represent attended context as a density matrix ρ; use purity `Tr(ρ²)` as an uncertainty signal.
**Better because.** Reads uncertainty from *where the model looked* rather than from what it concluded — a structurally better abstention signal than output entropy.
**Kill test.** No AUROC gain over an attention-entropy baseline at predicting errors.
`Cost: M · Serves: quality`

### T047 — Path-integral decoding *(= [Q12](../pipeline/P13-quantum-inspired-training-lab.md#q12--path-integral-multi-trajectory-decoding))*
**Core.** Maintain `k` trajectories with complex weights; sum amplitudes when trajectories reconverge on the same prefix instead of taking a max.
**Better because.** Beam search discards a token supported by many mediocre paths in favour of one strong path; amplitude summation is closer to the marginal likelihood actually being sought.
**Kill test.** No sequence-log-likelihood gain over beam search at equal width.
`Cost: S · Serves: quality`

### T048 — Interference routing for MoE *(= [Q9](../pipeline/P13-quantum-inspired-training-lab.md#q9--interference-routing-for-mixture-of-experts))*
**Core.** Complex-valued expert weights `a_j·e^(iφ_j)` combined by magnitude of the sum, replacing top-k gating.
**Better because.** Phase lets the router express expert *conflict*, so disagreeing experts cancel rather than averaging into mush.
**Kill test.** No gain over soft top-k gating with a learned temperature.
`Cost: L · Serves: quality`

### T049 — Simulated variational quantum circuit layer *(= [Q6](../pipeline/P13-quantum-inspired-training-lab.md#q6--simulated-variational-quantum-circuit-as-a-mixing-layer))*
**Core.** A classically simulated 14-qubit parameterized circuit as a mixing layer: ~840 parameters acting on 16,384 dimensions.
**Better because.** Extreme parameter efficiency through structured unitary mixing.
**Kill test.** Indistinguishable from a Givens-rotation orthogonal matrix of equal parameter count — which is very likely what it is.
`Cost: L · Serves: light`

### T050 — Amplitude-amplification decoding *(= [Q5](../pipeline/P13-quantum-inspired-training-lab.md#q5--amplitude-amplification-shaped-speculative-decoding))*
**Core.** Grover-shaped iterative reweighting of a candidate-continuation pool.
**Better because.** Possibly a better exploration schedule for speculative drafting.
**Kill test.** No acceptance-rate gain over standard top-k speculative decoding. *(Predicted outcome: falsified — Grover's advantage requires superposition.)*
`Cost: S · Serves: fast`

### T051 — Imaginary-time learning-rate schedule *(= [Q11](../pipeline/P13-quantum-inspired-training-lab.md#q11--imaginary-time-evolution-as-a-learning-rate-schedule))*
**Core.** Derive step size from the estimated spectral gap, since gradient descent is discretized imaginary-time Schrödinger evolution.
**Better because.** A *derived* schedule adapting to local curvature, rather than a tuned cosine curve.
**Kill test.** Does not beat a [P07](../pipeline/P07-scaling-microlaws.md)-tuned cosine schedule, or Hessian probes cost >5% throughput.
`Cost: L · Serves: quality`

### T052 — Dequantized embedding compression *(= [Q8](../pipeline/P13-quantum-inspired-training-lab.md#q8--dequantized-low-rank-embedding-compression))*
**Core.** Length-squared importance sampling to build a low-rank sketch of the embedding matrix.
**Better because.** Embeddings are 8.4M of 42.2M parameters; 2× compression frees 4M for depth.
**Kill test.** Worse than truncated SVD at the same rank, or BPB cost above 0.02.
`Cost: M · Serves: light`

---

## Physics-inspired, non-quantum (T053–T060)

### T053 — Renormalization-group layer coarse-graining
**Core.** Treat successive layers as RG steps; explicitly coarse-grain the representation by a fixed factor at each depth, with an RG-flow regularizer.
**Better because.** Deep networks empirically perform coarse-graining already; making it explicit could reach the same abstraction in fewer layers.
**Kill test.** No BPB gain at equal depth versus an unconstrained stack.
`Cost: M · Serves: light`

### T054 — Spin-glass capacity bound for attention
**Core.** Model attention as an Ising system and use replica analysis to derive how many distinct patterns a given head count can store.
**Better because.** Yields a theoretical bound on head count and `d_model` — a principled version of the [P07](../pipeline/P07-scaling-microlaws.md) sweep.
**Kill test.** The predicted capacity does not match measured retrieval capacity.
`Cost: S · Serves: light`

### T055 — Free-energy (MDL) regularizer
**Core.** Add a description-length penalty on weights, minimizing `loss + λ·complexity` as a variational free energy.
**Better because.** Principled compression pressure: the model is explicitly optimized to be small *and* accurate, which is the project's objective stated as a loss function.
**Kill test.** No better size/quality trade-off than plain weight decay.
`Cost: M · Serves: light`

### T056 — Symplectic residual flow
**Core.** Structure residual blocks as symplectic integrators of a Hamiltonian system, conserving a norm-like quantity across depth.
**Better because.** Exact conservation prevents residual-stream growth with depth, which is the stability problem that forces careful initialization scaling.
**Kill test.** No stability gain — deep runs diverge as often as with standard `1/sqrt(2L)` scaling.
`Cost: M · Serves: quality`

### T057 — Diffusion text generation
**Core.** Train a discrete diffusion model that denoises a full sequence in parallel rather than generating left to right.
**Better because.** Parallel generation of all 32k tokens at once could be far faster than autoregressive decoding, and it allows global revision.
**Kill test.** BPB-equivalent quality requires more sampling steps than autoregressive tokens — i.e. no speed gain.
`Cost: XL · Serves: fast`

### T058 — Optimal-transport alignment loss
**Core.** Add a Wasserstein-distance term between the model's and the data's token-distribution geometry.
**Better because.** Cross-entropy treats all errors as equally wrong; OT respects semantic distance, so predicting a near-synonym is penalized less than predicting nonsense.
**Kill test.** No gain in generation metrics, and BPB regresses.
`Cost: M · Serves: quality`

### T059 — Percolation analysis of information flow
**Core.** Model the SWA/global layer stack as a percolation network and compute the critical connectivity for information to traverse 32k tokens.
**Better because.** Gives a *derived* answer to how many global layers are needed, and where, instead of the current guess.
**Kill test.** The predicted critical threshold does not match measured needle accuracy as global layers are removed.
`Cost: S · Serves: long`

### T060 — MERA-style hierarchical context compression
**Core.** A multi-scale entanglement renormalization ansatz over the context: alternating disentangling and coarse-graining layers forming a logarithmic-depth tree.
**Better because.** MERA represents scale-invariant correlations with logarithmic resources — and natural language correlations are approximately power-law, which is exactly the structure MERA is built for.
**Kill test.** No better long-range BPB than hierarchical block attention (T002) at equal cost.
`Cost: L · Serves: long, light`
