# Architecture — N32

> Target design. Built and measured by [P04](pipeline/P04-baseline-architecture.md), [P08](pipeline/P08-efficient-attention.md), and [P09](pipeline/P09-long-context-extension.md).
> Revisable **only** by [P07](pipeline/P07-scaling-microlaws.md), with a validated scaling study behind it.

---

## 1. The model

| Parameter | Value |
|---|---:|
| `vocab_size` | 16,384 |
| `d_model` | 512 |
| `n_layers` | 12 |
| `n_heads` | 8 (`head_dim` 64) |
| `n_kv_heads` | 2 (GQA) |
| `ffn_hidden` | 1,408 (SwiGLU) |
| `max_seq_len` | 32,768 |
| `window_size` | 1,024 |
| `global_every` | 6 (layers 5 and 11) |
| `rope_theta` | 10⁴ → 10⁶ after extension |

Norm: RMSNorm, pre-norm, no biases. Activation: SwiGLU. Position: RoPE with QK-norm. Embeddings tied.

### Parameter budget

| Component | Params | Share |
|---|---:|---:|
| Attention (per layer) | 655,360 | |
| SwiGLU FFN (per layer) | 2,162,688 | |
| Norms + QK-norm (per layer) | 1,152 | |
| **× 12 layers** | **33,830,400** | 80.1% |
| Tied embeddings | 8,388,608 | 19.9% |
| **Total** | **42,219,520** | 100% |

**Non-embedding: 33.8 M.** Reported separately from embeddings in every document — law R4.

---

## 2. Layer schedule

Layer `i` is global when `(i + 1) % 6 == 0`.

| Layer | 0 | 1 | 2 | 3 | 4 | **5** | 6 | 7 | 8 | 9 | 10 | **11** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Type | SWA | SWA | SWA | SWA | SWA | **GLB** | SWA | SWA | SWA | SWA | SWA | **GLB** |

Local layers build phrase- and block-level structure cheaply; the two global layers move information across the full window. The last layer is global by design — the final layer must see the whole context to answer questions about its beginning.

---

## 3. Why 32k fits in 8 GB

KV bytes per token per layer = `2 (K,V) × 2 KV heads × 64 head_dim × 2 bytes` = **512 B**.

| Configuration | KV @32k | Ratio |
|---|---:|---:|
| MHA, all layers global | 805 MB | 1.0× |
| GQA-2, all layers global | 201 MB | 4.0× |
| **GQA-2 + SWA on 10 of 12** | **38.7 MB** | **20.8×** |

Compute follows the same pattern: sliding-window layers cost `O(n·w)` instead of `O(n²)`, an 11× reduction in attention FLOPs per token at 32k.

**This is the enabling decision of the whole project.** Rationale and ablations: [P08](pipeline/P08-efficient-attention.md).

---

## 4. Training pipeline

| Phase | Context | Tokens | RoPE base | LR | Wall |
|---|---:|---:|---:|---:|---:|
| Pretrain | 2,048 | 3.6 B | 10⁴ | 6e-4 cosine | ~32 h |
| Extend X1 | 8,192 | 200 M | 10⁶ | 6e-5 | ~3 h |
| Extend X2 | 32,768 | 100 M | 10⁶ | 3e-5 | ~5 h |
| Anneal X3 | 32,768 | 20 M | 10⁶ | 1e-5 | ~2 h |

Total ≈ **4.0 B tokens in ~39 GPU-hours** on one RTX 4060 Mobile. Compute follows \(C \approx 6ND \approx 1.0 \times 10^{18}\) FLOPs at ~25% MFU.

Details: [P05](pipeline/P05-training-harness.md), [P09](pipeline/P09-long-context-extension.md).

---

## 5. Source layout

```
n32/
  data/        acquisition, cleaning, dedup, tokenization    P02
  tokenizer/   BPE training and evaluation                   P03
  model/       config, norm, rope, attention, ffn, block     P04, P08
  train/       loop, optimizer, schedule, checkpointing      P05, P09, P15
  eval/        BPB, long-context, benchmarks                 P06, P10, P17
  serve/       inference, KV cache, quantization, RAG        P11, P12, P16
  research/    quantum-inspired and theoretical probes       P13, P14
bench/         hardware and performance measurement          P00, P11
```

One module per concern. Cyclomatic complexity ≤10 per function.

---

## 6. Deployment targets

| Target | Format | Size | Throughput |
|---|---|---:|---:|
| RTX 4060 | bf16 | 84 MB | ≥100 tok/s @8k |
| RTX 4060 | int8 | ~50 MB | ≥180 tok/s @8k |
| CPU only | GGUF Q8_0 | ~50 MB | ≥15 tok/s @2k |

Details: [P11](pipeline/P11-throughput-engineering.md), [P12](pipeline/P12-quantization-and-runtime.md).

---

## 7. What this architecture is not

- **Not a chat assistant.** 42M parameters hold very little world knowledge. Intended use is in-context tasks over long documents: summarize, extract, continue, answer-from-context.
- **Not a retrieval system with a model attached.** Retrieval exists ([P16](pipeline/P16-grounding-and-retrieval.md)) and is always measured separately from generation — law R3.
- **Not novel for novelty's sake.** Every component is a well-measured standard technique. Novelty enters through [P13](pipeline/P13-quantum-inspired-training-lab.md) and [P14](pipeline/P14-theoretical-model-triage.md), measured against this baseline.

---

## 8. Superseded

The previous stack — a 2-layer, `hidden=64` GPT-Neo with a 50,257-token inherited vocabulary, 96% of its parameters in the embedding table — is described in [`ASSESSMENT-2026-07-30.md §2`](ASSESSMENT-2026-07-30.md#2-measured-ground-truth). Its code is quarantined in `legacy/`.
