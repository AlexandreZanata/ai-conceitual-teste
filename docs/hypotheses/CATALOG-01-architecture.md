# Catalogue 01 — Attention, memory, context (T001–T020)

> Format and rules: [README](README.md). Triage: [P14](../pipeline/P14-theoretical-model-triage.md).
> This family is the most relevant to objective 3 (32k context) and objective 1 (light).

---

### T001 — Register tokens
**Core.** Prepend `r` learnable tokens (r ≈ 8) that every layer attends to, acting as a global scratchpad independent of the input.
**Better because.** Transformers repurpose semantically meaningless tokens as attention dumps, corrupting their representations. Dedicated registers give that traffic somewhere to go, and give sliding-window layers a channel that survives the window.
**Kill test.** No improvement in positional BPB beyond 8k, and no reduction in attention entropy on punctuation tokens.
`Cost: S · Serves: long, quality`

### T002 — Hierarchical block attention
**Core.** Two-level attention: tokens attend within 512-token blocks, and one summary vector per block attends across all blocks.
**Better because.** Gives `O(n·b + (n/b)²)` cost with genuinely global reach, rather than the SWA compromise of local reach plus a few global layers.
**Kill test.** Worse positional BPB at 32k than the SWA/global hybrid at equal FLOPs.
`Cost: M · Serves: long, fast`

### T003 — Hybrid SSM–attention
**Core.** Replace 8 of 12 attention layers with Mamba-style selective state-space blocks, keeping 4 attention layers for precise recall.
**Better because.** SSM layers have **constant** memory per token, so the 32k KV cache drops from 38.7 MB toward ~10 MB, and decode gets faster. Attention layers retain the exact-retrieval ability that pure SSMs lack.
**Kill test.** Needle accuracy at 32k falls below 90%, or BPB regresses more than 1%.
`Cost: M · Serves: long, fast, light`

### T004 — Compressive memory
**Core.** When the sliding window slides, compress the evicted KV entries into a fixed-size associative memory matrix rather than discarding them.
**Better because.** Turns bounded memory into unbounded context: information beyond the window degrades gracefully instead of vanishing.
**Kill test.** Retrieval from compressed memory is no better than chance at 16k+ distance.
`Cost: L · Serves: long, light`

### T005 — kNN-augmented attention
**Core.** Augment the final attention layer with a k-nearest-neighbour lookup over a datastore of cached hidden-state→token pairs, interpolating with the model distribution.
**Better because.** Adds effectively unlimited memory with no parameters, which matters disproportionately at 42M where parametric knowledge is scarce.
**Kill test.** BPB gain <0.02 when the datastore holds 100M entries, or lookup latency exceeds 30% of decode time.
`Cost: M · Serves: quality`

### T006 — Multi-resolution context
**Core.** Recent 2k tokens at full resolution; 2k–8k mean-pooled in pairs; beyond 8k pooled in groups of 8.
**Better because.** Matches the information-theoretic reality that distant context matters in aggregate, not token by token. Costs a fraction of full attention for most of the benefit.
**Kill test.** Needle retrieval at pooled depths falls below 70%, showing pooling destroys retrievable detail.
`Cost: M · Serves: long, fast`

### T007 — Learned KV eviction
**Core.** Score cached keys by accumulated attention mass and evict the lowest-scoring, keeping a fixed budget of `k` entries regardless of sequence length.
**Better because.** Attention is empirically concentrated on a small "heavy hitter" set; storing the rest is waste. Gives constant memory at arbitrary context length.
**Kill test.** At a 4k-entry budget over 32k of context, needle accuracy drops more than 5 points versus a full cache.
`Cost: M · Serves: long, light`

### T008 — Cross-layer KV sharing
**Core.** Layers 6–11 reuse the KV tensors computed by layers 0–5 instead of computing their own.
**Better because.** Halves the KV cache — 38.7 MB to 19.4 MB at 32k — and removes half the K/V projections, on the observation that adjacent layers' attention patterns are highly correlated.
**Kill test.** BPB regression exceeds 1%, or needle accuracy drops more than 3 points.
`Cost: S · Serves: light, fast`

### T009 — Latent (low-rank) attention
**Core.** Project KV into a shared low-rank latent of dimension 64, cache only the latent, and reconstruct per-head K and V on the fly.
**Better because.** Decouples cache size from head count entirely; can beat GQA's compression ratio without GQA's loss of head diversity.
**Kill test.** At equal cache size, worse BPB than GQA with `n_kv_heads=2`.
`Cost: M · Serves: light, long`

### T010 — Content-adaptive window
**Core.** A tiny predictor head chooses each token's attention window from {256, 1024, 4096} based on its hidden state.
**Better because.** Most tokens need only local context; a few (pronouns, references, closing brackets) need much more. A fixed window pays for the worst case at every position.
**Kill test.** Learned windows do not beat a fixed window of equal average size.
`Cost: M · Serves: fast, long`

### T011 — Dilated attention
**Core.** Each layer attends to positions at exponentially increasing stride: layer `i` attends to every `2^i`-th token.
**Better because.** Logarithmic receptive-field growth reaches 32k in 15 layers with `O(n log n)` total cost, and needs no global layers at all.
**Kill test.** Information at non-sampled positions is provably lost — needle accuracy at unaligned offsets falls below 80%.
`Cost: M · Serves: long, fast`

### T012 — Attention sinks
**Core.** Always include the first 4 tokens in every sliding window, regardless of distance.
**Better because.** Softmax must put its mass somewhere; without a sink, evicting the initial tokens destabilizes the whole attention distribution. This is the known cause of streaming collapse and costs almost nothing to fix.
**Kill test.** No improvement in the depth-0% needle cell, and no change in perplexity stability past the window.
`Cost: S · Serves: long`

### T013 — Block-recurrent transformer
**Core.** Process the sequence in 512-token blocks, carrying a recurrent state vector between blocks via cross-attention.
**Better because.** Combines transformer parallelism inside blocks with RNN-style unbounded memory across them, at fixed memory cost.
**Kill test.** Cross-block gradient flow vanishes — no measurable dependency beyond 4 blocks.
`Cost: L · Serves: long, light`

### T014 — Two-speed context
**Core.** A fast stream updated every token plus a slow stream updated every 64 tokens, the slow stream carrying long-range state.
**Better because.** 98% of long-range computation is redundant at token granularity; updating it 64× less often is nearly free.
**Kill test.** The slow stream carries no information — ablating it does not change BPB.
`Cost: M · Serves: fast, long`

### T015 — Modern Hopfield memory layer
**Core.** Insert a layer implementing continuous Hopfield retrieval: a learned pattern matrix queried by the hidden state, converging in one update step.
**Better because.** Exponential storage capacity in the pattern dimension gives dense factual memory at far lower parameter cost than FFN memorization.
**Kill test.** No BPB gain over an FFN of equal parameter count.
`Cost: M · Serves: quality, light`

### T016 — Explicit working-memory slots
**Core.** `m` memory slots with learned read and write heads, written once per 128 tokens and readable at any distance.
**Better because.** Gives the model an addressable place to store intermediate results, which is what multi-hop reasoning requires and what a stateless transformer must re-derive.
**Kill test.** Variable-tracking accuracy at 3 hops does not improve over the baseline.
`Cost: L · Serves: long, quality`

### T017 — Structure-aware attention
**Core.** Bias attention using document structure — code AST edges, markdown heading hierarchy, function-call graphs — as an additive mask.
**Better because.** Long documents have explicit structure that positional encoding discards. A function body should attend to its signature regardless of distance.
**Kill test.** No BPB gain on structured documents (code, markdown) over a positional baseline.
`Cost: M · Serves: quality, long`

### T018 — Hybrid NoPE
**Core.** Remove positional encoding from the sliding-window layers, keeping RoPE only on the global layers.
**Better because.** Causal masking alone conveys order within a small window, and no-positional-encoding models extrapolate to unseen lengths far better. This isolates extrapolation to two layers.
**Kill test.** Short-context BPB regresses more than 1%, or local word-order errors increase.
`Cost: S · Serves: long`

### T019 — Chunked cross-attention to a compressed encoder
**Core.** A small bidirectional encoder compresses each 512-token chunk to 32 vectors; the decoder cross-attends to those instead of raw tokens.
**Better because.** 16× compression of distant context, with the encoder learning what is worth keeping rather than a fixed pooling rule.
**Kill test.** Compressed chunks lose retrievable facts — needle accuracy below 75%.
`Cost: L · Serves: long, light`

### T020 — Test-time KV compression by SVD
**Core.** Periodically factor the KV cache with a truncated SVD, keeping the top-`r` components; purely an inference-time operation.
**Better because.** No training change, no retraining cost, and it applies to any already-trained model. Free memory reduction if the cache is genuinely low-rank.
**Kill test.** At `r` giving 4× compression, needle accuracy drops more than 3 points.
`Cost: S · Serves: light, long`
