# P11 — Throughput engineering

> **Stage:** 11 of 19 · **Estimate:** 3 days · **GPU time:** ~6 h
> **Precondition:** [P10](P10-long-context-evaluation.md) `PASS`
> **Gate:** ≥100 tok/s at 8k context on GPU; time to first token ≤400 ms at 8k.

---

## 1. Why this stage exists

Objective 2 is **fast**. Until now the project has optimized quality; this stage
optimizes the thing a user experiences. It comes after [P10](P10-long-context-evaluation.md)
deliberately: optimizing a model whose quality is unproven wastes the effort, and
optimization that silently changes outputs is only detectable against an
established quality baseline.

**Law at risk: R1** — every optimization here must be output-equivalent or measured against BPB. A speedup that changes the model is a different model.

---

## 2. Where the time actually goes

Autoregressive decoding of a 42M model is **memory-bandwidth bound, not compute
bound**. This is the single most important fact for this stage.

Per generated token:

| Work | Bytes moved | FLOPs |
|---|---:|---:|
| Read all weights (bf16) | 84 MB | — |
| Read KV cache @8k | ~10 MB | — |
| Compute | — | ~84 MFLOP |

At ~200 GB/s effective bandwidth, reading 94 MB takes **~0.47 ms**, giving a
theoretical ceiling of **~2,100 tok/s**. The 84 MFLOP of compute takes ~0.01 ms
at 8 TFLOP/s.

**The model is 45× more bandwidth-bound than compute-bound.** Therefore:

- Reducing weight bytes (quantization, [P12](P12-quantization-and-runtime.md)) directly increases speed.
- Reducing kernel launches (fusion, CUDA graphs) matters enormously — launch overhead can exceed the work.
- Adding FLOPs is nearly free; adding memory traffic is not.
- **Batching is close to free** — the weight read is amortized. Batch 8 should be barely slower per token than batch 1.

The last point is the highest-leverage optimization available and is frequently
overlooked.

---

## 3. Optimization ladder

Applied in order, each measured independently. Percentages are expected gains.

| # | Optimization | Gain | Risk |
|---|---|---:|---|
| 1 | **CUDA graphs** for the decode step | 25–40% | None — eliminates launch overhead |
| 2 | **`torch.compile`** with `mode="reduce-overhead"` | 15–30% | Recompilation on shape change |
| 3 | **Fused RMSNorm + residual** | 5–10% | Low |
| 4 | **Fused QKV projection** (one GEMM, not three) | 5–8% | Low |
| 5 | **Preallocated KV cache**, no reallocation | 10–20% | Low |
| 6 | **SWA ring buffer** (from [P08](P08-efficient-attention.md)) | already counted | — |
| 7 | **Chunked prefill** (2,048-token chunks) | TTFT only | Low |
| 8 | **Speculative decoding** with a 2-layer draft | 1.5–2.5× | Medium — must verify output equivalence |
| 9 | **int8 weights** ([P12](P12-quantization-and-runtime.md)) | ~1.8× | Quality cost, measured there |

Items 1–7 are **exactly output-preserving** and must be verified as such.
Item 8 is output-preserving *in distribution* when implemented correctly, which
must be proven, not assumed.

### CUDA graphs deserve emphasis

At 42M parameters, a single decode step launches ~150 kernels, each with ~5 µs of
launch overhead — **~0.75 ms of pure overhead against ~0.5 ms of actual work**.
CUDA graphs capture the whole step as one launch. On small models this is
routinely the largest single win available, and it is often skipped because it
sounds exotic.

---

## 4. Speculative decoding, done honestly

Draft model: layers 0–1 of the trained model, reused with no extra training.

```
1. Draft proposes k=4 tokens autoregressively (4 cheap forward passes)
2. Target verifies all 4 in ONE forward pass (batched over positions)
3. Accept the longest prefix matching the target's sampling decision
4. Expected acceptance at k=4: 2.0-2.8 tokens per target pass
```

**The correctness requirement:** with modified rejection sampling, speculative
decoding produces **exactly the target model's output distribution**. Prove it:

```
test_speculative_distribution_equivalence:
  Fix seed. Generate 10,000 tokens with speculation and without.
  Assert the token-frequency distributions match within chi-square p > 0.05.
```

If this test fails, the implementation is approximating the model and the speedup
is not free. Report it as a quality trade-off rather than a pure win.

---

## 5. Steps

### 5.1 Establish the baseline

```bash
npm run bench:latency -- --model artifacts/models/n32-32k.pt \
  --contexts 512,2048,8192,16384,32768 --batch 1,4,8 \
  --gen-tokens 256 --warmup 3 --repeats 10 \
  --out results/perf/baseline.json
```

Report **p50 and p99**, never the mean. Report cold and warm separately. A warm
number presented as the user-facing latency is the vanity metric this project has
already been burned by.

### 5.2 Apply and measure one at a time

Each optimization gets its own commit and its own entry in
`results/perf/ladder.json`, with before/after p50, p99, and an output-equivalence
check. **Applying three at once and reporting the total makes it impossible to
know which one mattered** — or which one broke correctness.

### 5.3 Verify output equivalence after every step

```
test_optimization_preserves_output:
  Fix seed and prompt.
  Assert optimized greedy output == baseline greedy output, token for token.
```

For items 1–7 this must be **exact**. Any divergence is a bug, not a
floating-point nuance — greedy decoding with identical weights is deterministic.

### 5.4 Report the full matrix

| Context | Batch | TTFT p50 | Decode tok/s | Peak VRAM |
|---|---|---|---|---|
| 512 | 1 | | | |
| 2,048 | 1 | | | |
| 8,192 | 1 | | | |
| 8,192 | 8 | | | |
| 32,768 | 1 | | | |

---

## 6. Deliverables

| Artifact | Path |
|---|---|
| Inference engine | `n32/serve/engine.py` |
| CUDA graph capture | `n32/serve/graph.py` |
| Speculative decoding | `n32/serve/speculative.py` |
| Baseline measurements | `results/perf/baseline.json` |
| Per-optimization ladder | `results/perf/ladder.json` |
| Final matrix | `results/perf/matrix.json` |
| Equivalence tests | `n32/serve/test_equivalence.py` |
| Public result | `docs/pipeline/results/P11.md` |

---

## 7. Gate

| Metric | Threshold |
|---|---|
| Decode throughput @8k, batch 1 | **≥100 tok/s** |
| Decode throughput @32k, batch 1 | **≥40 tok/s** |
| TTFT @8k | **≤400 ms** |
| TTFT @32k | **≤2,000 ms** |
| Throughput @8k, batch 8 | **≥400 tok/s** aggregate |
| Output equivalence, items 1–7 | **exact**, token for token |
| Speculative distribution equivalence | chi-square **p > 0.05** |
| Peak VRAM @32k inference | **≤4 GB** |
| p99 / p50 ratio | **≤2.0** (predictable latency) |

---

## 8. Expected results

| Configuration | Predicted | Notes |
|---|---:|---|
| Baseline @8k, batch 1 | 60–90 tok/s | Launch-overhead dominated |
| + CUDA graphs | 90–130 tok/s | The big one |
| + compile + fusion | 110–160 tok/s | |
| + speculation (k=4) | 200–350 tok/s | Acceptance-rate dependent |
| + int8 ([P12](P12-quantization-and-runtime.md)) | 350–600 tok/s | |
| Batch 8 @8k, aggregate | 500–900 tok/s | Bandwidth amortized |
| TTFT @8k | 150–300 ms | Prefill is compute-bound |
| TTFT @32k | 800–1,500 ms | Use chunked prefill |

If the baseline already exceeds 150 tok/s, the model may be smaller than
specified — verify the parameter count before celebrating.

---

## 9. Failure modes

| Symptom | Cause | Action |
|---|---|---|
| CUDA graphs give no gain | Graph not actually replaying | Verify capture; check for dynamic shapes in the step |
| Speedup but different output | Non-deterministic kernels or a real bug | Set deterministic algorithms; bisect the ladder |
| p99 ≫ p50 | Allocator churn or a GC pause | Preallocate everything; run with a fixed allocator pool |
| Throughput falls with batch size | Recomputing per-sequence masks | Batch the mask construction |
| Speculation slower than baseline | Acceptance too low | Lower `k` to 2; check the draft shares the target's tokenizer and RoPE base |
| TTFT @32k >5 s | Prefill not chunked | Chunk at 2,048 and reuse the cache |

---

## 10. Do not

- Do not report mean latency. p50 and p99 only.
- Do not report warm-cache numbers as user-facing latency.
- Do not apply multiple optimizations before measuring each.
- Do not accept any output change from items 1–7.
- Do not optimize before [P10](P10-long-context-evaluation.md) passes. Speed on a broken model is worthless.
- Do not hand-write CUDA. PyTorch plus CUDA graphs reaches within ~15% of hand-tuned, at a fraction of the risk.

---

**Next:** [P12 — Quantization and runtime](P12-quantization-and-runtime.md)
