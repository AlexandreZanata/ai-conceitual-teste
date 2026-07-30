# P13 — Quantum-inspired training lab

> **Stage:** 13 of 19 · **Estimate:** ongoing, parallel to P15–P18 · **GPU time:** ~2 h per hypothesis
> **Precondition:** [P10](P10-long-context-evaluation.md) `PASS` — a validated baseline must exist before anything is compared to it
> **Gate:** ≥8 hypotheses resolved (promoted or falsified) with committed artifacts.

---

## 1. The honesty preamble — read before anything else

**There is no quantum computer attached to this machine.** There will not be one.
Every method in this stage is a **classical algorithm inspired by quantum
mechanics**, running on an RTX 4060.

This distinction is not pedantry. It is the difference between real work and the
most common failure mode in this area: attaching quantum vocabulary to an
ordinary technique and reporting the rename as a discovery. The previous
programme did exactly this with `NANOGEN` — see
[assessment §2.6](../ASSESSMENT-2026-07-30.md#26-the-generative-goal-was-never-approached).

### The anti-quantum-washing rule

> **A hypothesis is admissible only if it names the classical technique it most
> resembles, and is benchmarked against that technique as the control.**

If "quantum-inspired optimizer Q3" turns out to be SGD with noise, then SGD with
noise is the baseline, and Q3 must beat it. If it does not, Q3 is **falsified**,
and its quantum framing was decoration.

This rule is what makes the track scientific. Apply it without exception.

### What quantum mechanics genuinely offers a classical ML researcher

Three real things, none of which require a QPU:

| Idea | Physical origin | Classical value |
|---|---|---|
| **Tensor networks** | Efficient representation of entangled many-body states (DMRG, MPS) | Principled low-rank structure with a *tunable, theoretically motivated* capacity knob (bond dimension) |
| **Unitary evolution** | Quantum dynamics preserves the norm | Exactly-preserved gradient norms over very long sequences — directly relevant to 32k context |
| **Amplitudes and interference** | Probability is \|ψ\|², so contributions can cancel | A representation where evidence can *destructively* cancel, which softmax over real logits cannot express |

Everything below derives from one of these three. Anything that derives from none
of them is probably decoration.

---

## 2. Protocol

Every hypothesis follows the same six steps. No exceptions, no shortcuts.

| Step | Requirement |
|---|---|
| 1. **State** | One paragraph: mechanism, and *why* it should help. A hypothesis that cannot say why is a guess. |
| 2. **Name the control** | The nearest classical technique. This is the baseline, not vanilla `N32-base`. |
| 3. **Predict** | Commit a numeric prediction to git **before** running. |
| 4. **Run** | Two 200M-token runs (treatment and control) at identical seed and data order. ~4 GPU-h. |
| 5. **Score** | BPB primary; plus params, tok/s, and VRAM. Bootstrap confidence intervals. |
| 6. **Resolve** | `PROMOTE` / `FALSIFY` / `INCONCLUSIVE`. Write to [`docs/negative_results.md`](../negative_results.md) either way. |

**`INCONCLUSIVE` may be used at most twice per hypothesis.** After that it
resolves to `FALSIFY`. This prevents the indefinite `HOLD` / `DEFER` limbo that
consumed NANOGEN 1–18 without ever producing a verdict.

### Promotion criterion

> BPB improvement **≥0.01** over the *named control* at equal or lower parameter
> count and equal or better throughput, with non-overlapping 95% confidence
> intervals.

0.01 BPB is roughly the noise floor of the [P06](P06-evaluation-harness.md)
harness. Below that, nothing has been demonstrated.

---

## 3. The hypothesis set

Twelve hypotheses. Eight must be resolved to close the gate. Ordered by expected
value, which is *not* the same as expected success — Q1 and Q7 are the most
likely to work, Q4 and Q10 are the most interesting if they do.

---

### Q1 — Tensor-train FFN (MPS weight factorization)

| | |
|---|---|
| **Origin** | Matrix Product States; DMRG represents a \(2^n\)-dimensional quantum state in \(O(n\chi^2)\) parameters |
| **Mechanism** | Reshape each FFN matrix `[512, 1408]` into a high-order tensor and factor it as a tensor train with bond dimension χ. Parameters scale as `O(d · χ²)` rather than `O(d²)`. |
| **Why it should help** | Weight matrices are empirically low-rank-ish. A tensor train captures *multiplicative* structure that a plain low-rank factorization `UV^T` cannot. |
| **Control** | **Low-rank factorization at equal parameter count.** Also compare against the dense baseline. |
| **Prediction** | At χ=32, matches dense BPB with ~40% fewer FFN parameters; beats low-rank by 0.01–0.03 BPB. |
| **Falsified if** | Does not beat plain low-rank at equal parameters. |
| **Cost** | 4 GPU-h · **Difficulty: medium** |
| **Payoff if true** | Directly serves objective 1 — same quality, smaller model. Highest expected value in the set. |

---

### Q2 — Entanglement entropy as a context diagnostic

| | |
|---|---|
| **Origin** | Entanglement entropy across a bipartition measures information shared between two halves of a quantum system |
| **Mechanism** | Treat the residual stream at a position as a state vector. Cut the context at position `k`, compute the von Neumann entropy of the singular-value spectrum of the cross-block attention matrix. Track it across depth and position. |
| **Why it should help** | It is a *measurement*, not a method. It should reveal **where** the 32k context bottleneck is: which layer stops transmitting long-range information. |
| **Control** | Attention entropy and mutual-information probes. |
| **Prediction** | Entropy peaks at the global layers (5, 11) and is near zero in SWA layers beyond the window — quantifying exactly how much the two global layers carry. |
| **Falsified if** | It provides no information beyond attention-weight inspection. |
| **Cost** | 1 GPU-h · **Difficulty: low** |
| **Payoff if true** | A principled tool for placing global layers in [P08](P08-efficient-attention.md), instead of the current "every 6th" guess. |

---

### Q3 — Transverse-field annealing schedule

| | |
|---|---|
| **Origin** | Quantum annealing: a transverse field allows tunnelling through energy barriers, and is decayed to zero |
| **Mechanism** | Add parameter noise \(\sigma(t) = \sigma_0 (1 - t/T)^p\) to gradients, analogous to the transverse-field strength, decaying to zero over training. |
| **Why it should help** | Barrier tunnelling, unlike thermal hopping, is sensitive to barrier *width* rather than only height — the analogy suggests a different, possibly better, noise schedule. |
| **Control** | **SGD with Gaussian noise on a linear decay schedule.** This control is essential — the mechanisms are extremely close. |
| **Prediction** | Honest prior: **≤0.005 BPB difference**, i.e. probably falsified. Run it early to establish that the track kills its own weak ideas. |
| **Falsified if** | Indistinguishable from the noise-schedule control. |
| **Cost** | 4 GPU-h · **Difficulty: low** |
| **Payoff if true** | Modest. Run it for the methodological value of a clean early falsification. |

---

### Q4 — Born-rule output layer

| | |
|---|---|
| **Origin** | Born rule: \(P(x) = \|\psi(x)\|^2 / Z\) |
| **Mechanism** | The output head emits a real amplitude vector ψ; token probability is \(\psi_i^2 / \sum_j \psi_j^2\) instead of `softmax(logits)`. |
| **Why it should help** | Softmax cannot express cancellation: every contribution to a logit is additive in log-space and strictly increases probability. With **signed amplitudes**, two pieces of evidence can destructively interfere, letting the model actively *suppress* a token that two separate pathways each partially support. This is a genuine representational difference, not a reparameterization. |
| **Control** | Standard softmax at identical parameter count. |
| **Prediction** | Comparable BPB overall, but **measurably better calibration** (lower expected calibration error) and fewer high-confidence errors. |
| **Falsified if** | Worse BPB **and** no calibration gain. |
| **Cost** | 4 GPU-h · **Difficulty: low** (a ~20-line change) |
| **Payoff if true** | High. Better calibration at small scale would be a genuinely publishable result, and it feeds the abstention work in [P16](P16-grounding-and-retrieval.md). |
| **Watch out** | Gradient of \(\psi^2\) vanishes at ψ=0. Initialize away from zero and monitor for dead units. |

---

### Q5 — Amplitude-amplification-shaped speculative decoding

| | |
|---|---|
| **Origin** | Grover's algorithm amplifies marked-state amplitude in \(O(\sqrt{N})\) iterations |
| **Mechanism** | Iteratively reweight a candidate-continuation pool toward high-likelihood sequences using a Grover-shaped update (reflect about the mean, then about the target). |
| **Why it should help** | Possibly a better exploration schedule for the draft pool in [P11](P11-throughput-engineering.md) speculation. |
| **Control** | **Standard speculative decoding with a top-k draft pool.** |
| **Prediction** | **No speedup.** Grover's quadratic advantage requires quantum superposition; classically, reflection operators are just reweighting. Stated in advance so the negative result is not a surprise. |
| **Falsified if** | Acceptance rate does not exceed the control. |
| **Cost** | 2 GPU-h · **Difficulty: low** |
| **Payoff if true** | Low. Included because it is the clearest example of the anti-quantum-washing rule: the honest prediction is failure, and running it proves the track reports what it finds. |

---

### Q6 — Simulated variational quantum circuit as a mixing layer

| | |
|---|---|
| **Origin** | Variational quantum circuits: parameterized unitaries as trainable layers |
| **Mechanism** | Replace one FFN with a classically simulated `n`-qubit circuit (n ≤ 14, so \(2^{14}=16{,}384\) amplitudes are tractable): parameterized single-qubit rotations plus a fixed entangling pattern. Parameter count is `O(n · depth)` — extremely small. |
| **Why it should help** | Extreme parameter efficiency: a 14-qubit, 20-layer circuit has ~840 parameters yet acts on a 16,384-dimensional space. |
| **Control** | **A random orthogonal matrix with the same parameter budget** (e.g. Givens-rotation parameterization). This control is the crux — Givens rotations are essentially the same object without the vocabulary. |
| **Prediction** | Matches the Givens control almost exactly, because it *is* a structured Givens parameterization. Likely `INCONCLUSIVE` or `FALSIFY`. |
| **Falsified if** | Indistinguishable from the orthogonal-matrix control. |
| **Cost** | 6 GPU-h · **Difficulty: high** |
| **Payoff if true** | Medium. Even a falsification is worth publishing, since VQC-as-a-layer is widely proposed and rarely controlled properly. |

---

### Q7 — Unitary recurrent memory for long context

| | |
|---|---|
| **Origin** | Quantum time evolution \(U = e^{-iHt}\) is unitary and exactly norm-preserving |
| **Mechanism** | Add a recurrent state updated by a learned unitary (parameterized via Householder reflections or the Cayley transform) running alongside the sliding-window attention, carrying information past the window without a KV cache. |
| **Why it should help** | A unitary map has all singular values equal to 1, so gradients neither vanish nor explode **over arbitrary sequence length** — exactly the failure mode that limits recurrence at 32k. |
| **Control** | **A diagonal-complex SSM (Mamba/S4-style) at equal parameter count.** These already use near-unitary dynamics; the question is whether *exact* unitarity helps. |
| **Prediction** | Improves positional BPB in the 16k–32k range by 0.01–0.02 with ~0.5M extra parameters and **no KV growth**. |
| **Falsified if** | Does not beat the diagonal SSM control on positional BPB. |
| **Cost** | 8 GPU-h · **Difficulty: high** |
| **Payoff if true** | **Highest in the set.** Constant-memory long-range channel serves objectives 1, 2, and 3 simultaneously. |

---

### Q8 — Dequantized low-rank embedding compression

| | |
|---|---|
| **Origin** | Tang's dequantization results: quantum recommendation-system speedups are matched classically given sampling access |
| **Mechanism** | Apply length-squared importance sampling to compress the 16,384 × 512 embedding matrix into a sampled low-rank sketch. |
| **Why it should help** | Embeddings are 8.4M of 42.2M parameters ([P04](P04-baseline-architecture.md)). A 2× compression frees 4M parameters for depth. |
| **Control** | **Truncated SVD at the same rank.** |
| **Prediction** | Matches SVD; both cost 0.02–0.04 BPB on rare tokens. Probably not worth it. |
| **Falsified if** | Worse than truncated SVD, or the BPB cost exceeds 0.02. |
| **Cost** | 3 GPU-h · **Difficulty: medium** |

---

### Q9 — Interference routing for mixture-of-experts

| | |
|---|---|
| **Origin** | Superposition with complex phases; paths interfere constructively or destructively |
| **Mechanism** | Instead of top-k hard gating, compute complex-valued expert weights \(a_j e^{i\phi_j}\) and combine as \(\|\sum_j a_j e^{i\phi_j} E_j(x)\|\). |
| **Why it should help** | Phase gives the router a way to express *conflict* between experts, not just relative preference — experts that disagree can cancel rather than average into mush. |
| **Control** | **Soft top-k gating with learned temperature.** |
| **Prediction** | Slightly better than soft gating on heterogeneous data (code + prose), where expert conflict is real. |
| **Falsified if** | No gain over soft gating, or training becomes unstable. |
| **Cost** | 6 GPU-h · **Difficulty: high** |
| **Note** | Requires an MoE baseline, which `N32-base` does not have. Depends on [T021–T030](../hypotheses/CATALOG-01-architecture.md). Schedule late. |

---

### Q10 — Density-matrix attention with purity-based abstention

| | |
|---|---|
| **Origin** | Mixed quantum states are density matrices ρ; purity \(\mathrm{Tr}(\rho^2)\) measures how "definite" a state is |
| **Mechanism** | Represent the attended context as \(\rho = \sum_i p_i \|v_i\rangle\langle v_i\|\) using attention weights \(p_i\). Compute purity as a scalar uncertainty signal. |
| **Why it should help** | Purity is a **principled, architecture-native uncertainty measure**: attention spread thinly over many positions gives low purity, meaning the model has not localized the evidence. This is a much better abstention signal than an output-entropy threshold, because it reads uncertainty from *where the model looked* rather than from what it concluded. |
| **Control** | Attention entropy and max-logit thresholds as abstention signals. |
| **Prediction** | Purity beats output entropy at predicting errors — AUROC gain ≥0.05 on the [P16](P16-grounding-and-retrieval.md) abstention task. |
| **Falsified if** | No AUROC gain over the entropy baseline. |
| **Cost** | 3 GPU-h · **Difficulty: medium** |
| **Payoff if true** | High, and it connects the quantum track to the one thing the previous programme did care about — knowing when to refuse — but with a measurable, non-hand-coded signal. |

---

### Q11 — Imaginary-time evolution as a learning-rate schedule

| | |
|---|---|
| **Origin** | Wick rotation \(t \to -i\tau\) turns the Schrödinger equation into a diffusion equation whose evolution projects onto the ground state |
| **Mechanism** | Gradient descent *is* discretized imaginary-time evolution. The physics prescribes a step size from the spectral gap: \(\Delta\tau \sim 1/(E_1 - E_0)\), estimated online from the Hessian's top eigenvalues via Hutchinson probes. |
| **Why it should help** | Gives a **derived** learning-rate schedule rather than a tuned cosine curve, adapting to local curvature with a physical justification. |
| **Control** | **Cosine schedule tuned by the [P07](P07-scaling-microlaws.md) sweep** — a strong control. |
| **Prediction** | Matches cosine within 0.005 BPB. Cosine is very hard to beat. |
| **Falsified if** | Worse than tuned cosine, or the Hessian probes cost more than 5% throughput. |
| **Cost** | 5 GPU-h · **Difficulty: high** |

---

### Q12 — Path-integral multi-trajectory decoding

| | |
|---|---|
| **Origin** | Feynman path integral: amplitudes over all trajectories are summed, and most cancel |
| **Mechanism** | Maintain `k` decoding trajectories with complex weights; at each step, combine trajectories that reconverge to the same prefix by **summing amplitudes** rather than taking a max as beam search does. |
| **Why it should help** | Beam search discards a token supported by many mediocre paths in favour of one strong path. Amplitude summation lets many weak paths reinforce — which is closer to what marginal likelihood actually asks for. |
| **Control** | **Beam search at equal beam width**, and ancestral sampling. |
| **Prediction** | Better sequence-level likelihood than beam search at equal width; more diverse than beam, less random than sampling. |
| **Falsified if** | No improvement in sequence log-likelihood or [P06](P06-evaluation-harness.md) generation metrics. |
| **Cost** | 2 GPU-h · **Difficulty: medium** |
| **Note** | Inference-only, no training required — cheapest hypothesis in the set. **Run it first.** |

---

## 4. Schedule

| Order | Hypothesis | Reason |
|---|---|---|
| 1 | Q12 | Inference-only, 2 GPU-h, immediate signal |
| 2 | Q2 | Diagnostic; informs [P08](P08-efficient-attention.md) global-layer placement |
| 3 | Q4 | 20-line change, high potential payoff |
| 4 | Q3 | Cheap; expected falsification establishes the track's credibility |
| 5 | Q10 | Feeds [P16](P16-grounding-and-retrieval.md) |
| 6 | Q1 | Highest expected value, medium cost |
| 7 | Q5 | Cheap, predicted negative |
| 8 | Q7 | Highest payoff, highest cost |
| 9–12 | Q8, Q11, Q6, Q9 | As time allows |

**Total for the first eight: ~26 GPU-hours.**

---

## 5. Deliverables

| Artifact | Path |
|---|---|
| Implementations | `n32/research/quantum/q{01..12}.py` |
| Committed predictions | `results/quantum/predictions/q{NN}.json` |
| Run results | `results/quantum/q{NN}_result.json` |
| Verdict ledger | `docs/QUANTUM-LEDGER.md` |
| Falsifications | appended to [`docs/negative_results.md`](../negative_results.md) |
| Public result | `docs/pipeline/results/P13.md` |

`docs/QUANTUM-LEDGER.md` is a single table: hypothesis, control, prediction,
measured, verdict, artifact path. One row each. **No narrative.** It must be
readable in thirty seconds, and it must show the falsifications as prominently as
the promotions.

---

## 6. Gate

| Metric | Threshold |
|---|---|
| Hypotheses resolved | **≥8** |
| Each with a prediction committed **before** the run | verifiable in git history |
| Each benchmarked against a **named classical control** | 100% |
| Falsifications recorded | **all** |
| Promotions with non-overlapping 95% CI | required for any `PROMOTE` |
| `INCONCLUSIVE` verdicts | **≤3 of 8** |

**A gate that passes with 8 falsifications and 0 promotions is a full `PASS`.**
The stage measures whether the questions were answered, not whether the answers
were flattering. This is the correction to the failure mode described in
[assessment §4, C4](../ASSESSMENT-2026-07-30.md#c4--retrieval-used-to-hide-the-models-failure).

---

## 7. Do not

- Do not use quantum vocabulary for a technique that has a classical name. Call it by the classical name and cite the quantum inspiration.
- Do not claim quantum speedup. There is no QPU. Classical simulation of quantum algorithms is, at best, as fast as the best classical algorithm.
- Do not promote a hypothesis that beats `N32-base` but not its named control.
- Do not let a hypothesis sit in `HOLD`. NANOGEN 1–18 did that for 34 waves and produced no verdicts.
- Do not run a hypothesis without committing its prediction first.
- Do not let this stage delay P15–P18. It is a parallel track and may never become the critical path.

---

**Next:** [P14 — Theoretical model triage](P14-theoretical-model-triage.md)
