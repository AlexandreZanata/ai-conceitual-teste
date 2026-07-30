# Catalogue 02 — Optimization and learning rules (T021–T040)

> Format and rules: [README](README.md). Triage: [P14](../pipeline/P14-theoretical-model-triage.md).
> This family targets **quality per GPU-hour** — the axis where a 39-hour budget can genuinely compete.

---

### T021 — muP learning-rate transfer
**Core.** Reparameterize initialization and per-layer learning rates so the optimal LR is invariant to width, then tune LR on a tiny model and transfer it.
**Better because.** Removes LR tuning from the expensive runs entirely — tune at `d_model=64`, apply at 512. Directly multiplies the value of the [P07](../pipeline/P07-scaling-microlaws.md) sweep budget.
**Kill test.** The optimal LR found at small width is not optimal at 512, i.e. transfer fails.
`Cost: S · Serves: quality`

### T022 — Sharpness-aware minimization
**Core.** Two-step update: perturb weights toward the local gradient maximum, then step from that perturbed point.
**Better because.** Flat minima generalize better, and small models trained on limited data are exactly where the generalization gap bites hardest.
**Kill test.** No BPB gain that survives doubling the baseline's training tokens — SAM costs 2× compute, so it must beat simply training twice as long.
`Cost: M · Serves: quality`

### T023 — Gradient-noise-scale batch scheduling
**Core.** Measure the gradient noise scale online and grow the batch size to track it, starting small and ending large.
**Better because.** Early training is noise-dominated and wastes large batches; late training is curvature-dominated and needs them. A fixed batch size is wrong at both ends.
**Kill test.** No wall-clock reduction to the same BPB versus a fixed 524k-token batch.
`Cost: M · Serves: quality, fast`

### T024 — Difficulty curriculum from per-token loss
**Core.** Run a cheap 12M-parameter model over the corpus, record per-document loss, and order training from low to high difficulty.
**Better because.** Learning easy structure first gives a better-conditioned starting point for hard examples — and at 4B tokens with a single epoch, ordering is one of the few free levers available.
**Kill test.** No BPB gain over a random ordering at equal tokens.
`Cost: M · Serves: quality`

### T025 — Online data-mixture reweighting
**Core.** Adjust the sampling weights of the six corpus sources during training to maximize measured improvement per source on held-out data.
**Better because.** The [P02](../pipeline/P02-data-foundation.md) mixture is a static guess. The optimal mixture almost certainly changes between early and late training.
**Kill test.** The learned mixture does not beat the static mixture by more than 0.01 BPB.
`Cost: M · Serves: quality`

### T026 — Self-distillation from checkpoint ensembles
**Core.** Average predictions from checkpoints at 50%, 75%, and 100% of training, and distil that ensemble into the final model.
**Better because.** Checkpoint ensembles reliably beat any single checkpoint; distillation captures the gain at zero inference cost.
**Kill test.** The distilled model does not beat the final checkpoint by 0.01 BPB.
`Cost: M · Serves: quality`

### T027 — Trajectory weight averaging
**Core.** Maintain an exponential moving average of weights during training and ship the average rather than the final point.
**Better because.** Nearly free, and it consistently lands in a flatter region of the loss surface than the SGD iterate.
**Kill test.** The EMA does not beat the final checkpoint. (Prior: it almost always does — run it early.)
`Cost: S · Serves: quality`

### T028 — Progressive depth growth
**Core.** Train 4 layers, then duplicate to 8, then to 12, warm-starting each stage from the previous.
**Better because.** Early training does not need full depth. Growing saves an estimated 20–30% of total FLOPs to reach the same loss — directly relevant to a 39-hour budget.
**Kill test.** Final BPB is worse than training at full depth throughout, at equal total FLOPs.
`Cost: M · Serves: quality, fast`

### T029 — Progressive width growth
**Core.** Start at `d_model=256`, widen to 512 mid-training using function-preserving Net2Net expansion.
**Better because.** Same logic as T028 on the other axis, and width growth is function-preserving, so no capability is lost at the transition.
**Kill test.** The widening transient does not recover — loss after growth stays above the always-wide control.
`Cost: M · Serves: quality, fast`

### T030 — Reverse-KL distillation from a larger teacher
**Core.** Distil from a 1B model using reverse KL (mode-seeking) rather than forward KL (mode-covering).
**Better because.** A 42M student cannot represent a 1B teacher's full distribution. Forward KL forces it to spread mass over modes it cannot capture; reverse KL lets it commit to the modes it can.
**Kill test.** No BPB or generation-quality gain over forward KL at equal compute.
`Cost: L · Serves: quality`

### T031 — Muon / spectral-norm optimizer
**Core.** For 2D weight matrices, orthogonalize the momentum update via Newton–Schulz iteration before applying it.
**Better because.** Reported 1.3–2× speedups to target loss on small models, with the strongest evidence in exactly this parameter regime. Cheapest large win available in this family.
**Kill test.** No wall-clock reduction to BPB 1.40 versus tuned AdamW.
`Cost: S · Serves: quality, fast`

### T032 — Shampoo / SOAP preconditioning
**Core.** Second-order preconditioning using Kronecker-factored curvature estimates.
**Better because.** Better-conditioned steps mean fewer of them, and at 42M parameters the preconditioner is small enough to be affordable.
**Kill test.** The per-step overhead exceeds the step-count reduction — no net wall-clock gain.
`Cost: M · Serves: quality`

### T033 — Evolutionary tuning of the final layer
**Core.** After pretraining, optimize the output head with an evolutionary strategy instead of gradients.
**Better because.** Escapes the gradient's local basin for a small parameter subset, at low cost. Also connects to the repository's frozen EvoGen work.
**Kill test.** No BPB gain over continued gradient training of the same layer at equal compute.
`Cost: S · Serves: quality`

### T034 — Active example selection
**Core.** Skip training examples whose loss is already below a threshold, spending the saved compute on high-loss examples.
**Better because.** Late in training most tokens are already predicted well and contribute almost no gradient signal. Skipping them is pure savings.
**Kill test.** Skipping causes forgetting — BPB on easy held-out data regresses.
`Cost: S · Serves: fast, quality`

### T035 — Contrastive next-token objective
**Core.** Add an auxiliary loss pushing the model's distribution away from that of a weak 12M model on the same context.
**Better because.** Explicitly teaches what distinguishes a good model from a bad one, rather than only what is likely — a sharper training signal per token.
**Kill test.** No BPB gain, or degeneration metrics from [P06](../pipeline/P06-evaluation-harness.md) worsen.
`Cost: M · Serves: quality`

### T036 — Fill-in-the-middle objective
**Core.** For 30% of code documents, reorder as prefix–suffix–middle so the model learns bidirectional infilling.
**Better because.** Real code editing is infilling, not continuation. Costs nothing at training time and adds a genuinely distinct capability.
**Kill test.** Left-to-right BPB regresses more than 0.5%.
`Cost: S · Serves: quality`

### T037 — Span-corruption auxiliary loss
**Core.** Add a masked-span reconstruction loss alongside the causal objective, on 10% of batches.
**Better because.** Bidirectional signal improves representation quality; the causal head still handles generation.
**Kill test.** No BPB gain, and the extra loss slows convergence.
`Cost: S · Serves: quality`

### T038 — Loss-spike recovery protocol
**Core.** Detect loss spikes, rewind to the previous checkpoint, and skip the offending data shard.
**Better because.** A single bad shard can waste hours of a 39-hour run. Automated recovery makes long unattended training on a laptop actually viable.
**Kill test.** No spikes occur, or rewinding does not help when they do.
`Cost: S · Serves: quality`

### T039 — Batch-size warmup
**Core.** Start at a 64k-token batch and grow to 524k over the first 1,000 steps.
**Better because.** Small batches early give more optimizer steps per token when the model is far from any minimum and each step is cheap in information terms.
**Kill test.** No improvement in loss at step 2,000 versus a fixed batch size.
`Cost: S · Serves: quality, fast`

### T040 — Rare-token replay buffer
**Core.** Maintain a buffer of documents containing rare tokens and oversample them 3×.
**Better because.** With a 16k vocabulary the tail is short but still power-law distributed; rare tokens receive too few gradient updates to be learned at all.
**Kill test.** No BPB improvement on the rare-token subset, or common-token BPB regresses.
`Cost: S · Serves: quality`
