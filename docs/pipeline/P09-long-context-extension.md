# P09 — Long-context extension

> **Stage:** 9 of 19 · **Estimate:** 4 days · **GPU time:** ~10 h
> **Precondition:** [P08](P08-efficient-attention.md) `PASS`
> **Gate:** BPB non-increasing out to position 32,768.

---

## 1. Why this stage exists

The model from [P05](P05-training-harness.md) was trained at 2,048 tokens. Simply
running it at 32,768 produces garbage: RoPE frequencies at unseen positions map
to rotation angles the model has never encountered, and attention logits blow up.

This stage extends 2,048 → 32,768 for **~10 GPU-hours**, versus the ~200 hours
that training at 32k from scratch would cost. That ratio is the entire reason
progressive extension is the standard approach.

**This stage delivers objective 3.** It is where the project's differentiating
claim is either earned or lost.

**Law at risk: R7** — if the positional BPB curve rises, the stage has failed, regardless of how good the needle test looks.

---

## 2. Why RoPE breaks, precisely

RoPE encodes position `m` by rotating each dimension pair by `m · θ_i`, where

\[
\theta_i = \text{base}^{-2i/d}, \quad \text{base} = 10{,}000
\]

The lowest-frequency dimension has wavelength ≈ `2π · base` ≈ 62,832 positions.
Trained to 2,048, the model has only ever seen **3.3%** of that wavelength — a
nearly linear ramp. At position 32,768 the rotation enters territory that, from
the model's perspective, is not "far away" but *unmapped*.

### The three repairs

| Method | Mechanism | Cost | Verdict |
|---|---|---|---|
| **Position interpolation (PI)** | Compress positions: `m → m · (L_train / L_target)` | Cheap fine-tune | Works; degrades short-context resolution |
| **NTK-aware / base scaling (ABF)** | Raise the base: `10,000 → 1,000,000` | Cheap fine-tune | **Chosen.** Preserves high-frequency (local) detail while extending the low-frequency range. |
| **YaRN** | Per-dimension: interpolate low frequencies, leave high frequencies, plus attention temperature | Cheap fine-tune | Best published results; use as fallback if ABF underperforms |

**ABF is the primary approach.** Raising the base to 10⁶ makes the longest
wavelength ≈ 6.28 × 10⁶ positions, so 32,768 sits at 0.5% of it — comfortably
inside a smooth region — while high-frequency dimensions, which carry local
word-order information, are essentially unchanged.

The single hyperparameter is the base. Sweep it: **{10⁴ (control), 10⁵, 5×10⁵, 10⁶, 5×10⁶}**.

---

## 3. The extension curriculum

Three phases, each starting from the previous checkpoint.

| Phase | Context | Tokens | Base `θ` | LR | Est. |
|---|---:|---:|---:|---:|---:|
| **Base** (from [P05](P05-training-harness.md)) | 2,048 | 4.0 B | 10⁴ | — | done |
| **X1** | 8,192 | 200 M | 10⁶ | 6e-5 | ~3 h |
| **X2** | 32,768 | 100 M | 10⁶ | 3e-5 | ~5 h |
| **X3** (anneal) | 32,768 | 20 M | 10⁶ | 1e-5 | ~2 h |

Design rules, each of which is a known failure if violated:

- **LR is 10% of pretraining peak.** Higher LR erases pretrained knowledge; this is the most common way long-context fine-tuning destroys a model.
- **The base changes at X1 and never again.** Changing it at X2 forces the model to re-learn positions twice.
- **Constant LR within each phase**, with a short 200-step warmup. Cosine decay inside a 200M-token phase is unnecessary complexity.
- **X3 anneals on the highest-quality long documents only** — the standard final-anneal trick, and cheap.

### The data problem, and the honest way to solve it

Most documents are short. Training at 32,768 tokens requires genuinely long
sequences, or the model learns nothing about long-range dependency.

| Strategy | Description | Use |
|---|---|---|
| **Natural long documents** | Books, long code files, full RFCs, arXiv papers | **Preferred.** Target ≥60% of X2/X3 tokens. |
| **Repository packing** | Concatenate files from the same repository in dependency order | Genuine long-range structure — imports really do refer backwards |
| **Topic-clustered packing** | Group related documents by embedding similarity | Acceptable; creates weak but real long-range signal |
| **Random concatenation** | Glue unrelated documents together | **Harmful.** Teaches the model that distant context is noise, which is the opposite of the objective. |

Random packing is the reason many long-context models score well on needle tests
and poorly on real documents: they learn to retrieve isolated facts while
learning to ignore distant context for prediction. Measure both
([P10](P10-long-context-evaluation.md)) precisely to catch this.

Build the long-document set at [P02](P02-data-foundation.md); if it yields fewer
than 200M tokens of naturally long text, add repository packing before falling
back to topic clustering.

---

## 4. Steps

### 4.1 Make RoPE base a runtime parameter

`n32/model/rope.py` must support changing the base and recomputing the frequency
table **without touching any learned weight**. Add `test_rope_base_swap`: with
`base=10⁴` and sequence length ≤2,048, outputs must be bit-identical to the
pre-change implementation.

### 4.2 Sweep the base before committing to X2

Five short runs, 20M tokens each at 8,192 context (~20 min apiece). Evaluate each
on positional BPB at 2k / 4k / 8k. Pick the base that keeps short-context BPB
intact **and** produces the best 8k BPB.

**Prediction:** 10⁴ (control) degrades sharply past 4k; 10⁵ and 10⁶ both work;
5×10⁶ slightly harms short-context quality.

### 4.3 Run the curriculum

```bash
npm run train:extend -- --from artifacts/models/n32-base.pt \
  --ctx 8192 --rope-base 1e6 --tokens 2e8 --lr 6e-5 --out runs/n32-x1

npm run train:extend -- --from runs/n32-x1/final.pt \
  --ctx 32768 --rope-base 1e6 --tokens 1e8 --lr 3e-5 --out runs/n32-x2

npm run train:extend -- --from runs/n32-x2/final.pt \
  --ctx 32768 --rope-base 1e6 --tokens 2e7 --lr 1e-5 \
  --data data/tokens/long_quality/ --out runs/n32-x3
```

**Evaluate short-context BPB after every phase.** The failure mode of long-context
extension is quietly trading short-context quality for long-context capability.
A model that is better at 32k and worse at 2k is worse overall for almost every
real use.

### 4.4 Memory at 32k training

At 32,768 context, activations dominate. Micro-batch will drop to **1**, with
gradient accumulation raised to keep tokens-per-step constant.

| Item | Estimate |
|---|---:|
| Model state | 760 MB |
| Activations, batch 1 × 32,768, checkpointed | ~3.5 GB |
| Attention workspace | ~0.5 GB |
| **Peak** | **≈ 4.8 GB** |

If this OOMs, use sequence-parallel gradient accumulation: split the 32k sequence
into 4 chunks of 8,192, carrying the KV cache forward and accumulating gradients
across chunks.

---

## 5. Deliverables

| Artifact | Path |
|---|---|
| RoPE base sweep | `results/longctx/rope_sweep.json` |
| Phase checkpoints | `runs/n32-x{1,2,3}/final.pt` |
| Final long-context model | `artifacts/models/n32-32k.pt` |
| Positional BPB curve | `results/longctx/bpb_by_position.json` + `.svg` |
| Short-context regression check | `results/longctx/short_ctx_check.json` |
| Public result | `docs/pipeline/results/P09.md` |

---

## 6. Gate

| Metric | Threshold |
|---|---|
| BPB at position 32,768 | **≤ BPB at position 2,048** (context must help, never hurt) |
| Positional BPB curve | **monotone non-increasing** across 1k → 32k |
| Short-context BPB regression vs [P05](P05-training-harness.md) | **≤+1%** |
| Max context without NaN | **≥32,768** |
| Peak VRAM, 32k inference | **≤4 GB** |
| RoPE base sweep artifact | present, all 5 values |

### The positional BPB curve is the real test

| Position | Expected BPB | Interpretation |
|---:|---:|---|
| 0–1,024 | ~1.55 | Little context available yet |
| 1,024–4,096 | ~1.40 | Context beginning to help |
| 4,096–16,384 | ~1.34 | Long-range structure exploited |
| 16,384–32,768 | **~1.32** | **Must not rise** |

A rising tail means the model is *not* using the far context — it is tolerating
it. That is the difference between a 32k model and a model with a 32k input
buffer, and it is the distinction most long-context claims quietly fail.

---

## 7. Failure modes

| Symptom | Cause | Action |
|---|---|---|
| BPB explodes past 8k | RoPE base not applied at inference | The base must match between training and eval; store it in the checkpoint |
| Short-context BPB degrades >3% | LR too high in X1/X2 | Drop to 3e-5; restart from the base checkpoint |
| Positional curve flat, not decreasing | Randomly packed data | Rebuild X2/X3 data with natural long documents |
| NaN at 32k | Attention logit overflow | Confirm QK-norm is active; consider YaRN's attention temperature `1/sqrt(t)` |
| Needle test passes, BPB curve rises | Retrieval learned, prediction not | **Both must pass.** See [P10](P10-long-context-evaluation.md). |
| OOM in X2 | Activations at 32k | Micro-batch 1 + sequence-chunked accumulation |

---

## 8. Do not

- Do not train at 32k from scratch. It costs ~200 GPU-hours for no measured gain.
- Do not change the RoPE base more than once.
- Do not use randomly concatenated documents for long-context training.
- Do not accept a needle-test pass as evidence of long-context capability. **R3** applies: retrieval is not prediction.
- Do not skip the short-context regression check.
- Do not report "32k context" if the positional BPB curve rises after 16k. That claim would be false.

---

**Next:** [P10 — Long-context evaluation](P10-long-context-evaluation.md)
