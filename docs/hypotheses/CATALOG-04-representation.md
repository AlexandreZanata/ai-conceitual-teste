# Catalogue 04 — Representation and inference-time compute (T061–T080)

> Format and rules: [README](README.md). Triage: [P14](../pipeline/P14-theoretical-model-triage.md).
> This family is where a small model buys capability with **compute at inference time** rather than parameters — the most promising route to punching above 42M.

---

### T061 — Multi-token prediction
**Core.** Add 3 auxiliary heads predicting tokens `t+2`, `t+3`, `t+4`; discard them at inference.
**Better because.** Forces representations to encode information about the future beyond one step, which is a denser training signal per token. The heads are **discarded at deployment**, so quality improves at zero inference cost.
**Kill test.** No BPB gain on the primary head after removing the auxiliary heads.
`Cost: S · Serves: quality, fast`

### T062 — Self-speculative decoding via early exit
**Core.** Use the model's own layers 0–3 with a shared output head as the draft model for speculative decoding.
**Better because.** No separate draft model to train or store, and the draft shares the target's tokenizer and RoPE base by construction — removing the usual source of low acceptance.
**Kill test.** Acceptance rate below 40%, making it slower than plain decoding.
`Cost: S · Serves: fast`

### T063 — Adaptive computation time
**Core.** A halting head decides per token how many layers to run, exiting early on easy tokens.
**Better because.** Most tokens are trivially predictable (whitespace, common bigrams) and do not need 12 layers. Compute should follow difficulty.
**Kill test.** Early exit degrades BPB more than the proportional compute saved.
`Cost: M · Serves: fast`

### T064 — Mixture of depths
**Core.** A router selects the top 50% of tokens to process at each layer; the rest bypass via the residual connection.
**Better because.** Halves FLOPs with a learned rather than heuristic allocation, and unlike T063 the compute budget is static and predictable — which matters for latency guarantees.
**Kill test.** BPB regression exceeds the FLOP savings compared to a uniformly smaller model.
`Cost: M · Serves: fast, light`

### T065 — Latent chain-of-thought
**Core.** Before emitting a token, loop the final hidden state through the last block `k` times without producing output.
**Better because.** Gives extra computation per token without extra parameters and without spending context on reasoning text — reasoning in latent space rather than in tokens.
**Kill test.** No gain on multi-hop variable tracking from [P10](../pipeline/P10-long-context-evaluation.md) as `k` increases.
`Cost: M · Serves: quality`

### T066 — Pause tokens
**Core.** Insert learnable `<pause>` tokens before answer positions, giving the model extra forward passes to compute with.
**Better because.** Trivially simple, and the mechanism is known to help small models on reasoning tasks by decoupling computation depth from output length.
**Kill test.** No accuracy gain on context-QA as the pause count increases.
`Cost: S · Serves: quality`

### T067 — Self-consistency voting
**Core.** Sample `k=8` answers at temperature 0.7 and return the plurality.
**Better because.** Trades inference compute for accuracy — which is exactly the right trade when the model is 42M and decoding is already ≥100 tok/s.
**Kill test.** Voting does not beat greedy decoding on extraction and QA tasks.
`Cost: S · Serves: quality`

### T068 — Depth recurrence with shared weights
**Core.** A 4-layer block applied 3 times with tied weights, in place of 12 distinct layers.
**Better because.** Cuts non-embedding parameters from 33.8M to 11.3M at identical FLOPs — a 3× reduction in model size for whatever quality it retains.
**Kill test.** BPB regression exceeds that of a 4-layer model of equal parameter count, showing recurrence adds nothing.
`Cost: M · Serves: light`

### T069 — Layer-skip distillation
**Core.** Train the model so that any prefix of its layers produces a usable output, via layer dropout plus per-depth distillation.
**Better because.** One checkpoint deploys as many models — 4, 8, or 12 layers depending on the device's latency budget.
**Kill test.** The full-depth model regresses more than 2% to gain the sub-model property.
`Cost: M · Serves: fast, light`

### T070 — Learned sequence-dimension token merging
**Core.** Merge similar adjacent token representations in middle layers, reducing sequence length, then unmerge before output.
**Better because.** At 32k context, many adjacent tokens are near-duplicates in representation space; processing them separately is waste.
**Kill test.** Merging destroys retrievable detail — needle accuracy drops more than 5 points.
`Cost: M · Serves: fast, long`

### T071 — Hierarchical byte→word→sentence encoding
**Core.** Three stacked levels: byte encoder, word-level transformer, sentence-level transformer, each operating at a coarser rate.
**Better because.** Sentence-level layers see 32k tokens as ~1,500 sentence units, making global attention cheap at the level where long-range structure actually lives.
**Kill test.** Hierarchy loses fine detail — worse BPB than a flat model at equal FLOPs.
`Cost: L · Serves: long, fast`

### T072 — Tokenizer-free byte model with downsampling
**Core.** Operate on raw bytes with a strided convolutional patcher reducing the sequence 4×, then a transformer, then upsampling.
**Better because.** No tokenizer means no vocabulary parameters at all (freeing 8.4M), no out-of-vocabulary behaviour, and no tokenization bias against non-English text or unusual code.
**Kill test.** Bytes-per-parameter efficiency is worse than the 16k BPE baseline from [P03](../pipeline/P03-tokenizer.md).
`Cost: L · Serves: light, quality`

### T073 — Learned positional interpolation
**Core.** Train a small network mapping raw position to a RoPE scaling factor, learned jointly during context extension.
**Better because.** Replaces the hand-chosen YaRN/ABF schedule from [P09](../pipeline/P09-long-context-extension.md) with a learned one, potentially extending beyond 32k for free.
**Kill test.** Does not beat fixed ABF base scaling on positional BPB.
`Cost: M · Serves: long`

### T074 — Cross-turn embedding recycling
**Core.** Cache and reuse hidden states from earlier turns of a conversation instead of recomputing the prefix.
**Better because.** Eliminates prefill cost on multi-turn interactions, which dominates latency at long context.
**Kill test.** Recycled states diverge from freshly computed ones enough to change outputs.
`Cost: S · Serves: fast`

### T075 — Two-stage output factorization
**Core.** Predict a token cluster (256 clusters) first, then the token within it.
**Better because.** Turns a 16,384-way softmax into two ~128-way decisions, cutting output-layer compute ~8× — meaningful when the output head is tied to 8.4M parameters.
**Kill test.** Cluster errors compound — BPB regresses more than 1%.
`Cost: M · Serves: fast, light`

### T076 — Frequency-adaptive softmax
**Core.** Full-dimension embeddings for the 2,048 most frequent tokens, reduced-dimension for the tail.
**Better because.** Zipf's law means most probability mass sits on few tokens; spending equal capacity on every vocabulary entry is misallocation.
**Kill test.** Rare-token BPB regresses more than 5%.
`Cost: S · Serves: light`

### T077 — Embedding–first-layer weight sharing
**Core.** Reuse the embedding matrix as the first layer's value projection.
**Better because.** Saves parameters and imposes a sensible inductive bias — the first layer's value space is naturally the embedding space.
**Kill test.** BPB regresses more than 0.5%.
`Cost: S · Serves: light`

### T078 — Sparse-autoencoder auxiliary objective
**Core.** Train a sparse autoencoder on the residual stream and add its reconstruction loss as an auxiliary training signal.
**Better because.** Pressures representations toward monosemantic, disentangled features, which may improve both generalization and interpretability at once.
**Kill test.** No BPB gain, and features are no more monosemantic than the baseline's.
`Cost: M · Serves: quality`

### T079 — Concept-level prediction
**Core.** Predict the next *sentence embedding*, then decode it to tokens with a small decoder.
**Better because.** Plans at the semantic level rather than token by token, which could substantially improve long-range coherence — the weakest property of small models.
**Kill test.** Decoded output has worse BPB than direct token prediction.
`Cost: L · Serves: quality`

### T080 — Entropy-adaptive sampling
**Core.** Set sampling temperature per token from the model's own predictive entropy: low entropy → near-greedy, high entropy → more exploration.
**Better because.** A fixed temperature is wrong in both regimes; this is a free inference-time change requiring no retraining.
**Kill test.** No improvement in the [P06](../pipeline/P06-evaluation-harness.md) generation metrics over a tuned fixed temperature.
`Cost: S · Serves: quality`
