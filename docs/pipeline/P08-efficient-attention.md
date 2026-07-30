# P08 — Efficient attention

> **Stage:** 8 of 19 · **Estimate:** 3 days · **GPU time:** ~8 h
> **Precondition:** [P07](P07-scaling-microlaws.md) `PASS`
> **Gate:** KV cache ≤50 MB at 32k; BPB regression ≤0.5% versus full attention.

---

## 1. Why this stage exists

Full attention at 32,768 tokens is arithmetically hostile on 8 GB:

| Quantity at 32k, full attention | Value |
|---|---:|
| Attention matrix entries per head per layer | 1.07 × 10⁹ |
| Materialized as bf16 (one head, one layer) | 2.1 GB |
| Attention FLOPs per token, all 12 layers | 6.4 × 10⁹ |
| KV cache with 8 KV heads | 805 MB |

The KV cache alone would consume 10% of VRAM, and attention compute would
dominate everything else. This stage makes 32k affordable **before** the context
is extended at [P09](P09-long-context-extension.md), so the extension never has
to fight memory.

**Law at risk: R1** — efficiency that costs BPB is not efficiency. Every mechanism here is measured against a full-attention control.

---

## 2. The three levers, and what each buys

| Lever | Memory effect | Compute effect | Quality risk |
|---|---|---|---|
| **GQA** (`n_kv_heads = 2`) | KV cache ÷4 | negligible | very low — well established |
| **Sliding window** (`w = 1024`) | KV per SWA layer capped at `w` | `O(n·w)` instead of `O(n²)` | **moderate — the real risk** |
| **Flash/SDPA** | no `n×n` materialization | 2–4× faster | none — exact |

### The combined budget at 32,768 tokens

KV per token per layer = `2 × n_kv_heads(2) × head_dim(64) × 2 B` = **512 B**

| Configuration | KV @32k | vs baseline |
|---|---:|---:|
| MHA, all layers global | 805 MB | 1.0× |
| GQA only, all global | 201 MB | 4.0× |
| GQA + SWA on 10 of 12 layers | **38.7 MB** | **20.8×** |

Attention FLOPs per generated token likewise drop from 6.4 × 10⁹ to
**5.6 × 10⁸**, an 11× reduction, because 10 layers attend to 1,024 positions
instead of 32,768.

---

## 3. The quality question this stage must answer

Sliding-window attention is the one lever with real risk. A token at position
30,000 in an SWA layer cannot see position 100 *directly*. Information reaches it
through two routes:

1. **Global layers (5 and 11)** — direct full-context access, twice.
2. **Receptive-field stacking** — each SWA layer extends reach by `w`, so 10 SWA layers give an indirect receptive field of ~10,240 tokens, and the global layers cover the remainder.

The theoretical receptive field of the stack is
`10 × 1024 + 2 × 32768 = full context`. **Whether information actually survives
the hops is an empirical question**, and it is what this stage measures.

### Ablation grid (each run 400M tokens, ~3.5 GPU-h)

| Run | Configuration | Purpose |
|---|---|---|
| **E0** | Full attention, MHA | Control. The quality ceiling. |
| E1 | Full attention, GQA-2 | Isolates the GQA cost |
| E2 | SWA-1024, no global layers | Shows what global layers are worth |
| E3 | SWA-1024, global every 6 (**`N32-base`**) | The candidate |
| E4 | SWA-1024, global every 4 (3 global layers) | More global — worth the KV? |
| E5 | SWA-512, global every 6 | Cheaper window |
| E6 | SWA-2048, global every 6 | Wider window |

**Prediction:** E1 ≈ E0 (within 0.3%). E2 is clearly worse on long-context
metrics but similar on short-context BPB — **which is exactly why short-context
BPB alone cannot decide this stage.** E3 lands within 0.5% of E0. E4 gains little
over E3 for 17 MB more cache.

**Every run is evaluated on both short-context BPB and the [P10](P10-long-context-evaluation.md)
positional BPB curve.** A configuration that matches E0 at 2k and collapses at
16k is a failure that short-context evaluation cannot see.

---

## 4. Steps

### 4.1 Implement the attention path

`n32/model/attention.py`. Non-negotiables:

- Use `F.scaled_dot_product_attention` with the flash backend. Do not hand-roll.
- For SWA, pass `is_causal=True` plus a window, or use FlexAttention's block mask. **Never construct a dense `[n, n]` mask** — at 32k that is 1.07 × 10⁹ elements.
- GQA via `expand` on the KV heads, not `repeat`. `expand` is a view; `repeat` copies and quadruples memory.
- KV cache as a **ring buffer** for SWA layers: fixed `w`-sized allocation, overwritten in place. A growing cache for a windowed layer wastes exactly the memory the window was meant to save.
- Global layers use a standard growing cache, preallocated to `max_seq_len`.

### 4.2 Verify correctness before measuring speed

| Contract | Test |
|---|---|
| SWA equals full attention when `w ≥ n` | `test_swa_degenerates_to_full` |
| GQA equals MHA when `n_kv_heads == n_heads` | `test_gqa_degenerates_to_mha` |
| Ring buffer matches a naive windowed cache | `test_ring_buffer_equivalence` |
| Incremental decode matches a full forward | `test_cache_matches_full` at 8k |
| Window boundary is exact | `test_window_boundary` — position `t-w` has exactly zero influence |

`test_ring_buffer_equivalence` is where the bugs live. A ring buffer with an
off-by-one wrap produces plausible text and a silently broken model.

### 4.3 Measure

```bash
npm run bench:memory -- --model configs/n32-final.yaml \
  --seq-lens 1024,4096,8192,16384,32768 --out results/attention/memory.json

npm run bench:throughput -- --model configs/n32-final.yaml \
  --seq-lens 1024,4096,8192,16384,32768 --out results/attention/throughput.json
```

Report, per sequence length: KV bytes, peak VRAM, prefill tok/s, decode tok/s,
and time to first token.

### 4.4 Choose, then justify

Select the configuration minimizing KV memory **subject to** BPB within 0.5% of
E0 **and** the [P10](P10-long-context-evaluation.md) positional curve remaining
flat. Record all seven runs, including the losers — [P07](P07-scaling-microlaws.md)
and this stage are the project's evidence that its design was chosen rather than
assumed.

---

## 5. Deliverables

| Artifact | Path |
|---|---|
| Attention implementation | `n32/model/attention.py` |
| Ablation results, all 7 runs | `results/attention/ablation.json` |
| Memory scaling | `results/attention/memory.json` |
| Throughput scaling | `results/attention/throughput.json` |
| Decision record | `docs/adr/ADR-001-attention.md` |
| Public result | `docs/pipeline/results/P08.md` |

---

## 6. Gate

| Metric | Threshold |
|---|---|
| KV cache at 32,768 | **≤50 MB** (expected 38.7 MB) |
| BPB vs full-attention control (E0) | **≤+0.5%** |
| Peak VRAM, inference at 32k | **≤4 GB** |
| Ablation runs completed | **≥7** |
| All correctness contracts | pass |
| Prefill throughput at 32k | **≥5,000 tok/s** |
| No dense `[n,n]` mask anywhere | verified by code review |

---

## 7. Failure modes

| Symptom | Cause | Action |
|---|---|---|
| SWA loses >2% BPB | Window too small, or too few global layers | Try E6 (`w=2048`) or E4 (global every 4); accept more KV if needed |
| OOM at 32k despite the budget | Dense mask, or `repeat` instead of `expand` | Grep for `torch.ones(n, n)` and `.repeat(` |
| Ring buffer test fails at the wrap | Off-by-one in the modulo index | Position `t` writes to slot `t % w`; reads span `[t-w+1, t]` |
| Throughput does not improve with SWA | Flash backend not selected | Check `torch.backends.cuda.sdp_kernel`; head_dim must be 64 or 128 |
| E2 (no global) matches E3 on all metrics | Long-context eval is not exercising long dependencies | The eval is broken, not the model. Fix [P10](P10-long-context-evaluation.md) first. |

The last row is important: if removing all global attention costs nothing, the
evaluation is not measuring long-range dependency. **Fix the measurement before
believing the result.**

---

## 8. Do not

- Do not accept a BPB regression >0.5% for memory savings. Objective 1 does not outrank objective 3.
- Do not evaluate this stage on short-context BPB alone. That is the specific blind spot SWA exploits.
- Do not implement custom CUDA kernels. PyTorch SDPA is within 10% of hand-written flash attention and is correct.
- Do not skip the E0 control to save 3.5 hours. Without it there is no baseline and no claim.
- Do not use `torch.repeat_interleave` on KV heads in the hot path.

---

**Next:** [P09 — Long-context extension](P09-long-context-extension.md)
