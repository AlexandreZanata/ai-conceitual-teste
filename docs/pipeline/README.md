# N32 — research pipeline

> **Programme codename:** `N32`
> **Opened:** 2026-07-30, replacing the wave protocol (waves W–BH, retired permanently).
> **Rationale:** [`docs/ASSESSMENT-2026-07-30.md`](../ASSESSMENT-2026-07-30.md)
> **Read [P19](P19-agent-operating-protocol.md) before doing anything.** It defines how an agent is allowed to work here.

---

## 1. The objective, stated so it can be falsified

> Train a causal language model with **≤60M non-embedding parameters** and a **32,768-token context window** that achieves **held-out bits-per-byte competitive with models ~10× larger**, sustains **≥100 tokens/s at 8k context on an RTX 4060 Mobile**, and is trained **end to end on one laptop in under 72 hours**.

Three properties, in priority order. If they conflict, the earlier one wins.

| # | Property | Target | Measured by |
|---|---|---|---|
| 1 | **Light** | ≤60M non-embedding params; ≤120 MB on disk at int8 | [P04](P04-baseline-architecture.md), [P12](P12-quantization-and-runtime.md) |
| 2 | **Fast** | ≥100 tok/s @ 8k ctx (GPU); ≥15 tok/s (CPU only); TTFT ≤400 ms @ 8k | [P11](P11-throughput-engineering.md) |
| 3 | **Long context** | 32,768 tokens, with **measured** retrieval ≥90% at full depth | [P09](P09-long-context-extension.md), [P10](P10-long-context-evaluation.md) |

Two secondary research tracks run alongside, and may **never** block the primary objective:

| Track | Content | Home |
|---|---|---|
| **Q** | Quantum-inspired training hypotheses, tested classically on this GPU | [P13](P13-quantum-inspired-training-lab.md) |
| **T** | Catalogue of 100 theoretical architectures, triaged by cost and falsifiability | [P14](P14-theoretical-model-triage.md) · [`docs/hypotheses/`](../hypotheses/README.md) |

---

## 2. The reference design (`N32-base`)

Not a suggestion — this is the concrete configuration the pipeline builds and
measures against. [P07](P07-scaling-microlaws.md) is permitted to change these
numbers, but only with a measured scaling study behind it.

| Parameter | Value | Justification |
|---|---:|---|
| `d_model` | 512 | Largest width that keeps 12 layers inside 8 GB with activation checkpointing |
| `n_layers` | 12 | Depth beats width for reasoning at fixed budget |
| `n_heads` | 8 | `head_dim = 64`, the tensor-core sweet spot |
| `n_kv_heads` | **2** (GQA) | Shrinks the KV cache 4× — this is what makes 32k affordable |
| `ffn_hidden` | 1408 | SwiGLU, ≈2.75×`d_model`, multiple of 128 |
| `vocab_size` | **16,384** | See §3. The single most important fix. |
| Norm | RMSNorm, pre-norm, no biases | Cheaper, stabler |
| Activation | SwiGLU | Standard, well-measured gain |
| Position | RoPE, `θ=10,000` → `θ=1,000,000` after extension | [P09](P09-long-context-extension.md) |
| Attention | **Sliding window 1024**, with a **global layer every 6th** (layers 5, 11) | §4 |
| Embeddings | Tied input/output | Saves 8.4M params |

### Parameter budget

| Component | Params |
|---|---:|
| Per layer — attention (Q 512², K/V 512×128, O 512²) | 655,360 |
| Per layer — SwiGLU FFN (3 × 512 × 1408) | 2,162,688 |
| Per layer — norms | 1,024 |
| **Per layer total** | **2,819,072** |
| × 12 layers | **33,828,864** ← non-embedding |
| Tied embeddings (16,384 × 512) | 8,388,608 |
| **Total** | **≈ 42.2 M** |

**33.8M non-embedding**, comfortably under the 60M cap, with headroom for [P07](P07-scaling-microlaws.md) to grow depth if the scaling study says so.

---

## 3. Why the vocabulary is the headline change

The previous model spent **96% of its parameters** on a 50,257-entry GPT-2 embedding table, leaving **132K parameters** of actual transformer. See [assessment §2.4](../ASSESSMENT-2026-07-30.md#24-the-parameter-budget-was-spent-on-the-wrong-thing).

| | Old | `N32-base` |
|---|---:|---:|
| Vocab | 50,257 | 16,384 |
| `d_model` | 64 | 512 |
| Embedding params | 3,216,448 | 8,388,608 |
| **Non-embedding params** | **~132,000** | **33,828,864** |
| Embedding share | **96.0%** | 19.9% |
| **Ratio of real model** | **1×** | **256×** |

Same order of total parameters. **256× more actual model.** This is free, and it was available on day one.

---

## 4. Why 32k context is affordable on 8 GB

The naive objection is that 32k context needs a huge KV cache. With GQA plus a
sliding-window/global hybrid, it does not.

KV bytes per token per layer = `2 (K,V) × n_kv_heads(2) × head_dim(64) × 2 bytes (bf16)` = **512 B**

| Layer type | Count | Cached tokens | KV memory |
|---|---:|---:|---:|
| Global (full 32k attention) | 2 | 32,768 | 33.5 MB |
| Sliding window (1024) | 10 | 1,024 | 5.2 MB |
| **Total at 32,768 context** | 12 | — | **≈ 38.7 MB** |

For comparison, full attention on all 12 layers with 8 KV heads would need
**805 MB** — a 21× penalty that would make 32k impossible alongside the model
and activations. The hybrid is not a compromise; it is the enabling decision.

**Compute** matters as much as memory: sliding-window layers cost `O(n · w)`
rather than `O(n²)`. At 32k with `w=1024`, that is a **32× reduction** in
attention FLOPs on 10 of 12 layers.

---

## 5. Compute budget — the whole point

Using \(C \approx 6ND\) with \(N = 4.2\times10^{7}\) and \(D = 4\times10^{9}\) tokens:

\[
C \approx 6 \times 4.2{\times}10^{7} \times 4{\times}10^{9} = 1.01 \times 10^{18}\ \text{FLOPs}
\]

At a sustained \(7.5\times10^{12}\) FLOP/s (bf16, ~25% MFU on an RTX 4060 Mobile):

\[
t = \frac{1.01\times10^{18}}{7.5\times10^{12}} \approx 1.35\times10^{5}\ \text{s} \approx \mathbf{37.4\ hours}
\]

| Phase | Tokens | Context | Est. wall |
|---|---:|---:|---:|
| Main pretrain | 3.6 B | 2,048 | ~32 h |
| Context extension | 0.3 B | 8,192 | ~4 h |
| Long-context anneal | 0.1 B | 32,768 | ~3 h |
| **Total** | **4.0 B** | — | **≈ 39 h** |

Under the 72-hour budget with ~45% slack for restarts. **The compute exists. It has simply never been spent.**

---

## 6. Stage index

Stages run in order. A stage opens only when the previous stage's gate is `PASS`
with a committed artifact. There are no parallel stages and no optional stages.

### Foundation — make measurement possible

| Stage | Title | Gate | Est. |
|---|---|---|---|
| [P00](P00-charter-and-hardware-envelope.md) | Charter and hardware envelope | Reproducible hardware profile committed | 2 h |
| [P01](P01-ground-truth-reset.md) | Ground-truth reset | ≤40 npm scripts; legacy quarantined; `verify` green | 1 d |
| [P02](P02-data-foundation.md) | Data foundation | ≥4B deduplicated tokens, licence-clean, on disk | 3 d |
| [P03](P03-tokenizer.md) | Tokenizer | ≤3.6 bytes/token at vocab 16,384 on held-out | 1 d |

### Core — build and train the thing

| Stage | Title | Gate | Est. |
|---|---|---|---|
| [P04](P04-baseline-architecture.md) | Baseline architecture | Param count exact; forward/backward parity tests pass | 2 d |
| [P05](P05-training-harness.md) | Training harness | Bit-reproducible resume; ≥25% MFU | 2 d |
| [P06](P06-evaluation-harness.md) | Evaluation harness | Held-out BPB reproducible to ±0.001 | 2 d |
| [P07](P07-scaling-microlaws.md) | Scaling micro-laws | Fitted law predicts held-out loss within 3% | 3 d |

### Long context — the differentiator

| Stage | Title | Gate | Est. |
|---|---|---|---|
| [P08](P08-efficient-attention.md) | Efficient attention | KV ≤50 MB @32k; no BPB regression >0.5% | 3 d |
| [P09](P09-long-context-extension.md) | Long-context extension | BPB non-increasing to position 32,768 | 4 d |
| [P10](P10-long-context-evaluation.md) | Long-context evaluation | ≥90% needle retrieval at 32k, all depths | 2 d |

### Systems — make it fast and shippable

| Stage | Title | Gate | Est. |
|---|---|---|---|
| [P11](P11-throughput-engineering.md) | Throughput engineering | ≥100 tok/s @8k GPU; TTFT ≤400 ms | 3 d |
| [P12](P12-quantization-and-runtime.md) | Quantization and runtime | ≤120 MB int8; ≤1% BPB loss; ≥15 tok/s CPU | 3 d |

### Research tracks — run only after P10 passes

| Stage | Title | Gate | Est. |
|---|---|---|---|
| [P13](P13-quantum-inspired-training-lab.md) | Quantum-inspired training lab | ≥8 hypotheses falsified or promoted with artifacts | ongoing |
| [P14](P14-theoretical-model-triage.md) | Theoretical model triage | 100 catalogued; top-10 costed; ≥3 tested | ongoing |

### Capability and release

| Stage | Title | Gate | Est. |
|---|---|---|---|
| [P15](P15-instruction-and-behavior.md) | Instruction and behaviour | Instruction-following gain with no BPB regression | 4 d |
| [P16](P16-grounding-and-retrieval.md) | Grounding and retrieval | Generation and retrieval scored separately, always | 3 d |
| [P17](P17-external-benchmarking.md) | External benchmarking | Public-benchmark numbers vs named baselines | 3 d |
| [P18](P18-release-and-publication.md) | Release and publication | Third party reproduces from a clean clone | 5 d |

### Governance

| Stage | Title | Applies |
|---|---|---|
| [P19](P19-agent-operating-protocol.md) | Agent operating protocol | **Always. Read first.** |

**Critical path to a working 32k model: P00 → P12, ≈ 32 working days plus ~39 h of GPU time.**

---

## 7. The seven laws

Carried over from [assessment §7](../ASSESSMENT-2026-07-30.md#7-non-negotiable-rules-going-forward). Every stage spec restates the ones it is most at risk of violating.

| # | Law |
|---|---|
| **R1** | Held-out bits-per-byte is the primary metric. Every stage reports it. |
| **R2** | No claim without a committed artifact carrying git hash, config hash, seed, and wall time. Markdown is never evidence. |
| **R3** | Retrieval and generation are measured separately, always. |
| **R4** | Embedding and non-embedding parameters are always reported separately. |
| **R5** | A stage that costs no FLOPs is not a research stage. |
| **R6** | One pipeline. No waves, no letters, no forever packs. |
| **R7** | A failed gate stops the pipeline. Gates are never weakened to pass. |

---

## 8. Results

Public stage results are written to [`results/`](results/README.md), one file per
stage, only after the gate passes. That directory is the project's scoreboard —
if a stage is not there, it did not happen.
