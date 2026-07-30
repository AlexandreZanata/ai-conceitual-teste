# P12 — Quantization and runtime

> **Stage:** 12 of 19 · **Estimate:** 3 days · **GPU time:** ~4 h
> **Precondition:** [P11](P11-throughput-engineering.md) `PASS`
> **Gate:** ≤120 MB at int8 with ≤1% BPB loss, and ≥15 tok/s on CPU alone.

---

## 1. Why this stage exists

Objective 1 is **light**. A 42M-parameter model at bf16 is 84 MB — already small,
but quantization makes it *deployable anywhere* and, because decoding is
bandwidth-bound ([P11 §2](P11-throughput-engineering.md#2-where-the-time-actually-goes)),
**directly faster in proportion to the bytes saved.**

This is also the stage that makes the project's claim concrete: a model that runs
usefully on a CPU-only laptop with 32k context is a genuinely different artifact
from one that needs a GPU.

The existing `qt_quant.py` from the previous programme is real, working int8
weight-only quantization and is the starting point — one of four things worth
keeping from the old tree.

**Law at risk: R1** — every quantization level is reported with its measured BPB cost. No "negligible" without a number.

---

## 2. The quantization ladder

| Format | Size | Expected BPB cost | Use |
|---|---:|---:|---|
| bf16 (reference) | 84 MB | 0.000 | Quality baseline |
| **int8 weight-only, per-channel** | **42 MB** | **+0.005** | **Default ship format** |
| int8 + int8 KV cache | 42 MB + half KV | +0.010 | Long-context memory relief |
| int4 group-wise (g=128) | 24 MB | +0.03 – 0.06 | Extreme edge |
| int4 + AWQ/GPTQ calibration | 24 MB | +0.015 – 0.03 | Best int4 |

**Weight-only quantization is the right choice** for a bandwidth-bound model:
weights are stored int8 and dequantized to bf16 inside the kernel. Activations
stay bf16, so no activation calibration is needed and no accuracy cliff appears
on outlier activations.

### Why per-channel, not per-tensor

Per-tensor int8 uses one scale for the whole matrix, so a single outlier channel
compresses the dynamic range for every other channel. Per-channel (one scale per
output channel) costs `4 × d_out` bytes per matrix — about 25 KB total across the
model — and typically recovers most of the quality gap. **Always per-channel.**

### KV cache quantization matters more at 32k

At 32k context the KV cache is 38.7 MB, comparable to the int8 weights. int8 KV
halves it to 19.4 MB. Keep the most recent 128 positions in bf16 (recent tokens
matter most for the next prediction) and quantize the rest — the standard
compromise, and cheap to implement.

---

## 3. The CPU target

A 42M model at int8 is 42 MB, comfortably inside the 24 MB L3 cache plus RAM
bandwidth of the i7-13620H.

| Estimate | Value |
|---|---:|
| DDR5 effective bandwidth | ~60 GB/s |
| Bytes per token (int8 weights + KV) | ~50 MB |
| Theoretical ceiling | ~1,200 tok/s |
| Realistic with overhead | **20–60 tok/s** |

**15 tok/s is faster than most people read**, so the CPU target is a real
usability claim, not a curiosity. Achieving it requires AVX2/AVX-VNNI int8 GEMM
— use an existing runtime rather than writing kernels.

### Export path

| Runtime | Purpose | Priority |
|---|---|---|
| **GGUF / llama.cpp** | Best CPU int8/int4 kernels; huge ecosystem | **Primary** |
| ONNX Runtime | Portability, mobile | Secondary |
| PyTorch int8 | Reference correctness | Always |

llama.cpp requires the architecture to be expressible in its graph. `N32-base` is
Llama-shaped (RMSNorm, SwiGLU, RoPE, GQA) **except** for sliding-window attention
and QK-norm — both of which llama.cpp supports (SWA via the Mistral/Gemma path).
This compatibility was a deliberate reason for the [P04](P04-baseline-architecture.md)
choices; do not break it casually.

---

## 4. Steps

### 4.1 int8 weight-only

```bash
npm run export:int8 -- --model artifacts/models/n32-32k.pt \
  --scheme per-channel-symmetric --out artifacts/models/n32-32k-int8.pt
```

Rules:

- Quantize `W_q, W_k, W_v, W_o, W_gate, W_up, W_down` only.
- **Never quantize** embeddings, norms, or the output head. Embeddings are 8.4M parameters, so quantizing them saves 8.4 MB and disproportionately harms rare tokens; norms are tiny and sensitive.
- Symmetric, per-output-channel scales, stored fp16.

### 4.2 Measure the cost honestly

```bash
npm run eval:all -- --model artifacts/models/n32-32k-int8.pt \
  --baseline results/eval/baseline.json --out results/quant/int8_eval.json
```

Run the **full** [P06](P06-evaluation-harness.md) suite plus the
[P10](P10-long-context-evaluation.md) long-context suite. Quantization damage
often appears first at long context, where small per-token errors accumulate over
32k positions — short-context BPB can look untouched while needle retrieval
degrades.

### 4.3 KV cache quantization

```bash
npm run export:int8 -- --model ... --kv-quant int8 --kv-keep-recent 128 \
  --out artifacts/models/n32-32k-int8-kv8.pt
```

Re-run the needle test. If accuracy at 32k drops by more than 2 points, raise
`--kv-keep-recent` to 512 before abandoning the approach.

### 4.4 int4 exploration

int4 is exploratory, not required by the gate. Try group-wise (g=128) with GPTQ
calibration on 128 sequences from the held-out set. **If the BPB cost exceeds
0.05, do not ship it** — a 24 MB model that is measurably worse is not a better
product than a 42 MB model that is not.

### 4.5 GGUF export and verification

```bash
npm run export:gguf -- --model artifacts/models/n32-32k-int8.pt \
  --out artifacts/models/n32-32k-Q8_0.gguf
```

Verify with a cross-runtime equivalence test:

```
test_gguf_matches_pytorch:
  Same prompt, greedy decoding, 100 tokens, both runtimes.
  Assert token sequences are identical.
```

A mismatch means the export is wrong — usually RoPE base, SWA window, or QK-norm
not carried across. This test catches the class of bug that otherwise ships a
subtly different model to users.

### 4.6 CPU benchmark

```bash
npm run bench:latency -- --model artifacts/models/n32-32k-Q8_0.gguf \
  --device cpu --threads 10 --contexts 512,2048,8192,32768 \
  --out results/quant/cpu_perf.json
```

Use **10 threads, not 16** — the i7-13620H has 6 performance cores and 4 efficiency
cores; oversubscribing across hybrid cores usually loses throughput. Measure
6/8/10/12/16 and report the curve.

---

## 5. Deliverables

| Artifact | Path |
|---|---|
| Quantization implementation | `n32/serve/quantize.py` |
| int8 model | `artifacts/models/n32-32k-int8.pt` |
| GGUF export | `artifacts/models/n32-32k-Q8_0.gguf` |
| Quality-vs-size table | `results/quant/ladder.json` |
| CPU performance | `results/quant/cpu_perf.json` |
| Cross-runtime equivalence | `results/quant/runtime_parity.json` |
| Public result | `docs/pipeline/results/P12.md` |

---

## 6. Gate

| Metric | Threshold |
|---|---|
| int8 model size on disk | **≤120 MB** (expected ~50 MB with embeddings in fp16) |
| BPB cost of int8 vs bf16 | **≤1%** (≈ +0.013 at BPB 1.32) |
| Needle @32k after int8 | **within 2 points** of bf16 |
| CPU throughput @2k context, 10 threads | **≥15 tok/s** |
| CPU throughput @8k context | ≥8 tok/s |
| GPU throughput @8k after int8 | **≥180 tok/s** |
| GGUF vs PyTorch, greedy | **identical** token sequences |
| Peak RAM, CPU inference @32k | **≤2 GB** |

---

## 7. Failure modes

| Symptom | Cause | Action |
|---|---|---|
| int8 BPB cost >2% | Per-tensor instead of per-channel | Switch to per-channel; check for outlier channels in `W_down` |
| Long-context degrades, short-context fine | Error accumulation over positions | Keep `W_o` and `W_down` in bf16; re-measure |
| CPU under 5 tok/s | Scalar fallback, no AVX-VNNI | Verify llama.cpp built with the right flags; check `lscpu` for `avx_vnni` (present on this CPU) |
| GGUF output differs | SWA or RoPE base not exported | Compare layer-by-layer activations to localize |
| int4 collapses | Group size too large | Use g=64; if still bad, abandon int4 and report the negative result |
| More threads, less speed | Hybrid P/E core contention | Pin to the 6 performance cores |

---

## 8. Do not

- Do not quantize embeddings or norms.
- Do not report quantized quality on short context only.
- Do not ship int4 without calibration.
- Do not claim a speedup without the BPB cost beside it.
- Do not skip cross-runtime equivalence. Shipping a GGUF that behaves differently from the evaluated model invalidates every number in the model card.
- Do not use per-tensor scales.

---

**Next:** [P13 — Quantum-inspired training lab](P13-quantum-inspired-training-lab.md)
