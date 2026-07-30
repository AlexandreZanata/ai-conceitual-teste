# Catalogue 05 — Systems, grounding, continual learning (T081–T100)

> Format and rules: [README](README.md). Triage: [P14](../pipeline/P14-theoretical-model-triage.md).
> This family is where "runs on your hardware" becomes a capability rather than a constraint.

---

### T081 — On-device continual pretraining
**Core.** Continuously fine-tune on the user's own documents, on their machine, using a low learning rate and a replay buffer against forgetting.
**Better because.** A 42M model trains fast enough that personalization is practical on a laptop — something no frontier model can offer. This turns the size limitation into the product.
**Kill test.** Catastrophic forgetting — general BPB regresses more than 3% after 100M personal tokens.
`Cost: M · Serves: quality`

### T082 — Hot-swappable domain adapters
**Core.** Train rank-16 LoRA adapters per domain (code, medical, legal); load one at inference for ~0.5 MB each.
**Better because.** Domain specialization at negligible storage cost — one 42 MB base model plus a library of adapters beats a single generalist at this scale.
**Kill test.** Adapters give less than 0.03 BPB in-domain gain over the base model.
`Cost: S · Serves: quality, light`

### T083 — Byte-level entropy patching
**Core.** Segment bytes into variable-length patches at points where a small byte-level model's predictive entropy spikes, then run the transformer over patches.
**Better because.** Allocates compute by information content rather than by a fixed tokenizer vocabulary — high-entropy regions get fine granularity, boilerplate gets coarse. Removes the tokenizer entirely.
**Kill test.** Bytes-per-FLOP is worse than 16k BPE from [P03](../pipeline/P03-tokenizer.md).
`Cost: L · Serves: quality, light`

### T084 — Streaming infinite context
**Core.** Fixed memory budget with continuous eviction, enabling unbounded input length at constant VRAM.
**Better because.** Turns a 32k limit into a soft horizon: the model can process a 1M-token document with graceful degradation instead of a hard error.
**Kill test.** Quality past 32k falls below a truncate-to-last-32k baseline — i.e. streaming is worse than just not streaming.
`Cost: M · Serves: long, light`

### T085 — KV cache offload to CPU RAM
**Core.** Keep the recent 8k of KV in VRAM and page older entries to the 31 GB of system RAM, prefetching by predicted attention.
**Better because.** Effective context becomes bounded by system RAM rather than by 8 GB of VRAM — potentially millions of tokens on this machine.
**Kill test.** PCIe transfer latency dominates, dropping throughput below 20 tok/s.
`Cost: M · Serves: long`

### T086 — Ternary weights (1.58-bit)
**Core.** Constrain weights to {−1, 0, +1} with per-channel scales, trained from scratch with quantization in the loop.
**Better because.** 10× smaller than bf16 and replaces matrix multiplication with addition — the largest single reduction in the bandwidth-bound decode cost identified in [P11](../pipeline/P11-throughput-engineering.md).
**Kill test.** BPB cost exceeds 5%, which is worse than simply using a smaller fp16 model.
`Cost: L · Serves: light, fast`

### T087 — Quantization-aware pretraining
**Core.** Simulate int8 quantization during the entire pretraining run, not as a post-hoc conversion.
**Better because.** The model learns weights that are natively quantization-friendly, typically eliminating the post-training quality gap from [P12](../pipeline/P12-quantization-and-runtime.md) entirely.
**Kill test.** No reduction in the int8 quality gap versus post-training quantization.
`Cost: M · Serves: light, fast`

### T088 — 2:4 structured sparsity
**Core.** Prune to 2 non-zero weights in every group of 4, exploiting Ampere-and-later tensor-core sparse acceleration.
**Better because.** Hardware-supported 2× speedup on this exact GPU — a rare case of a free architectural win tied to available silicon.
**Kill test.** BPB regression exceeds 2%, or the RTX 4060 does not deliver the theoretical sparse speedup in practice.
`Cost: M · Serves: fast, light`

### T089 — Speculative retrieval
**Core.** While decoding token `t`, asynchronously prefetch the retrieval chunks likely needed for token `t+k`.
**Better because.** Hides retrieval latency entirely behind generation, making [P16](../pipeline/P16-grounding-and-retrieval.md) RAG effectively free at inference.
**Kill test.** Prefetch accuracy below 50%, so the wasted bandwidth outweighs the hidden latency.
`Cost: S · Serves: fast`

### T090 — Confidence-gated cascade
**Core.** `N32` answers directly; when its calibrated confidence is low, escalate to a larger model.
**Better because.** Most queries are easy. If `N32` handles 80% at 100× lower cost, average cost collapses while worst-case quality is preserved.
**Kill test.** Calibration is too poor to route — escalating on low confidence performs no better than escalating at random.
`Cost: S · Serves: fast, quality`

### T091 — Tool calls as a token action space
**Core.** Reserve special tokens that trigger external tools (calculator, search, code execution) whose results are injected back into the context.
**Better because.** A 42M model cannot do arithmetic or recall facts, but it can plausibly learn *when to ask*. Offloads exactly the capabilities the scale cannot support.
**Kill test.** Tool-invocation precision below 70% — the model calls tools at the wrong times.
`Cost: M · Serves: quality`

### T092 — Retrieval-augmented pretraining
**Core.** During pretraining, prepend nearest-neighbour chunks retrieved from the corpus to each training document.
**Better because.** Teaches the model to *use* retrieved context as a first-class skill rather than bolting retrieval on afterwards — which is how [P16](../pipeline/P16-grounding-and-retrieval.md)'s condition-B ceiling gets raised.
**Kill test.** No improvement in the gold-context condition versus a model trained without retrieval.
`Cost: L · Serves: quality`

### T093 — Nonparametric lifelong memory
**Core.** An external growing key–value store written during inference and read by a dedicated attention head.
**Better because.** Knowledge accumulates without weight updates and without forgetting — separating what the model *knows* from what it has *learned to do*.
**Kill test.** Retrieval from the store does not improve accuracy on previously seen facts.
`Cost: L · Serves: quality`

### T094 — Learned context compression tokens
**Core.** Train the model to compress a 512-token span into 16 summary tokens that preserve the information needed for downstream prediction.
**Better because.** 32× compression means a 32k window holds the equivalent of 1M raw tokens of context, learned end to end rather than by a fixed pooling rule.
**Kill test.** Compressed context loses more than 10% of needle retrieval accuracy.
`Cost: L · Serves: long, light`

### T095 — Coreference index for long documents
**Core.** Precompute an entity-mention index over the input and expose it as additional attention keys.
**Better because.** Long-document understanding is dominated by tracking entities across distance, which is precisely what SWA layers cannot do.
**Kill test.** No improvement on multi-hop variable tracking from [P10](../pipeline/P10-long-context-evaluation.md).
`Cost: M · Serves: long, quality`

### T096 — Self-verification head
**Core.** A second head scores whether the generated answer is supported by the provided context; low scores trigger regeneration or abstention.
**Better because.** Verification is a strictly easier task than generation, so a small model can plausibly verify outputs it could not reliably produce.
**Kill test.** Verifier AUROC below 0.7 — it cannot distinguish good answers from bad.
`Cost: M · Serves: quality`

### T097 — Constrained decoding via logit masking
**Core.** Mask logits at decode time to enforce a grammar — valid JSON, valid Python syntax, a fixed schema.
**Better because.** Guarantees structural validity regardless of model quality, which is exactly what makes a small extraction model usable in production.
**Kill test.** Constraints degrade content quality — semantic accuracy falls while syntactic validity rises.
`Cost: S · Serves: quality`

### T098 — Post-hoc calibration head
**Core.** After pretraining, train a small head on frozen features to predict answer correctness, using it as the abstention signal for [P15](../pipeline/P15-instruction-and-behavior.md).
**Better because.** Calibration is a separate skill from generation and learns better when trained separately, on the actual error distribution.
**Kill test.** Calibration AUROC does not exceed the raw output-entropy baseline.
`Cost: S · Serves: quality`

### T099 — Federated micro-updates
**Core.** Many users each fine-tune locally and share gradient sketches; a central process aggregates them into base-model updates.
**Better because.** A 42M model is small enough that consumer hardware can genuinely participate in training — a distributed research programme that frontier-scale models cannot support.
**Kill test.** Aggregated updates do not improve the base model beyond centralized training on the same data.
`Cost: XL · Serves: quality`

### T100 — Hardware-aware architecture search
**Core.** Search the space of layer types, widths, and window sizes with **measured** latency and VRAM on this RTX 4060 as explicit constraints, not proxies.
**Better because.** Optimizes the architecture for the actual deployment target instead of for FLOP counts, which correlate poorly with real latency on a bandwidth-bound model.
**Kill test.** The searched architecture does not beat the hand-designed `N32-base` on the BPB-versus-latency frontier.
`Cost: XL · Serves: fast, light`
