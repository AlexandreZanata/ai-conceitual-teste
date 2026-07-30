# P04 — Baseline architecture

> **Stage:** 4 of 19 · **Estimate:** 2 days · **GPU time:** ~1 h
> **Precondition:** [P03](P03-tokenizer.md) `PASS`
> **Gate:** parameter count matches config arithmetic exactly; all correctness contracts pass.

---

## 1. Why this stage exists

The previous model was a HuggingFace `GPTNeoConfig` with `hidden=64`, accepted
without a parameter-budget analysis, and never revisited across 37 waves. This
stage writes the model **from scratch, in one readable file**, so that every
parameter is accounted for and every design choice is defensible.

Writing it directly is not reinvention for its own sake: [P08](P08-efficient-attention.md)
requires a custom sliding-window/global hybrid, and [P09](P09-long-context-extension.md)
requires surgery on RoPE. Both are fights against a framework abstraction and
trivial in owned code.

**Law at risk: R4** — embedding and non-embedding parameters reported separately, always.

---

## 2. Specification — `N32-base`

```python
@dataclass(frozen=True)
class N32Config:
    vocab_size:    int   = 16384
    d_model:       int   = 512
    n_layers:      int   = 12
    n_heads:       int   = 8      # head_dim = 64
    n_kv_heads:    int   = 2      # GQA, 4:1 ratio
    ffn_hidden:    int   = 1408   # SwiGLU, ~2.75x, multiple of 128
    max_seq_len:   int   = 32768
    rope_theta:    float = 10000.0   # -> 1e6 at P09
    window_size:   int   = 1024      # sliding window
    global_every:  int   = 6         # layers 5 and 11 are global
    norm_eps:      float = 1e-5
    tie_embeddings: bool = True
    dropout:       float = 0.0       # not used: single epoch on 4B tokens
```

### Component choices and why

| Choice | Alternative rejected | Reason |
|---|---|---|
| **RMSNorm** | LayerNorm | Same quality, ~10% faster, no mean subtraction |
| **Pre-norm** | Post-norm | Post-norm needs careful warmup; pre-norm trains stably without it |
| **SwiGLU** | GELU MLP | Consistent gain at equal parameters; costs a third matrix, hence the 2.75× rather than 4× hidden |
| **No biases** | Biases everywhere | Free parameter saving, no measured loss |
| **RoPE** | Learned / ALiBi | Only option that extends cleanly to 32k ([P09](P09-long-context-extension.md)) |
| **GQA `n_kv_heads=2`** | MHA (8 KV heads) | **4× smaller KV cache** — the decision that makes 32k fit in 8 GB |
| **Tied embeddings** | Separate output head | Saves 8.4M params; at 16k vocab the quality cost is negligible |
| **QK-norm** | Nothing | RMSNorm on Q and K before attention; prevents the logit blow-ups that kill small-model runs at long context |
| **`dropout = 0`** | 0.1 | Single epoch over 4B unique tokens — there is nothing to overfit |

### Layer schedule

Layers are 0-indexed. Layer `i` is **global** when `(i + 1) % 6 == 0`.

| Layer | 0 | 1 | 2 | 3 | 4 | **5** | 6 | 7 | 8 | 9 | 10 | **11** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Type | SWA | SWA | SWA | SWA | SWA | **GLB** | SWA | SWA | SWA | SWA | SWA | **GLB** |

Rationale: local layers build phrase- and block-level representations cheaply;
the two global layers propagate information across the full window. Placing a
global layer **last** matters — the final layer must see the whole context to
answer questions about its beginning.

---

## 3. Parameter accounting (must match exactly)

| Component | Formula | Params |
|---|---|---:|
| Token embedding | `V × d` = 16384 × 512 | 8,388,608 |
| Per layer: `W_q` | `d × d` | 262,144 |
| Per layer: `W_k` | `d × (n_kv × head_dim)` = 512 × 128 | 65,536 |
| Per layer: `W_v` | same | 65,536 |
| Per layer: `W_o` | `d × d` | 262,144 |
| Per layer: SwiGLU `W_gate, W_up, W_down` | `3 × d × h` = 3 × 512 × 1408 | 2,162,688 |
| Per layer: 2 × RMSNorm | `2 × d` | 1,024 |
| Per layer: QK-norm | `2 × head_dim` | 128 |
| **Per layer total** | | **2,819,200** |
| × 12 layers | | **33,830,400** |
| Final RMSNorm | `d` | 512 |
| Output head | tied | 0 |
| **Non-embedding total** | | **33,830,912** |
| **Grand total** | | **42,219,520** |

`test_model_param_count` computes this from the config and asserts equality with
`sum(p.numel() for p in model.parameters())`. **A mismatch of even one parameter
is a `FAIL`** — it means the architecture in code differs from the architecture
in the document, which is how the previous programme lost track of where its
parameters went.

---

## 4. Steps

### 4.1 Implement

| File | Contents |
|---|---|
| `n32/model/config.py` | `N32Config`, `param_count()`, `kv_cache_bytes(seq_len)` |
| `n32/model/norm.py` | `RMSNorm` |
| `n32/model/rope.py` | RoPE precompute, apply, and `theta` rescaling hook |
| `n32/model/attention.py` | GQA attention, SWA and global paths, KV cache |
| `n32/model/ffn.py` | SwiGLU |
| `n32/model/block.py` | Pre-norm residual block |
| `n32/model/n32.py` | Full model, `forward`, `generate` |

Keep cyclomatic complexity ≤10 per function. If attention exceeds it, split the
mask construction into its own function rather than nesting.

### 4.2 Initialization

| Weight | Scheme |
|---|---|
| Embeddings | `N(0, 0.02)` |
| Linear layers | `N(0, 0.02)` |
| Output projections `W_o`, `W_down` | `N(0, 0.02 / sqrt(2 · n_layers))` |
| RMSNorm gains | `1.0` |

Scaling the residual-stream output projections by `1/sqrt(2L)` keeps the residual
stream variance from growing with depth. Skipping this is a common cause of small
models diverging in the first 1,000 steps.

### 4.3 Verify against a reference

Before trusting any custom kernel, prove equivalence:

1. Instantiate `N32-base` with `window_size = max_seq_len` (i.e. SWA disabled) and `n_kv_heads = n_heads` (GQA disabled).
2. Build an equivalent HuggingFace `LlamaForCausalLM` with the same config.
3. Copy weights across.
4. Assert logits agree within `1e-4` on 100 random sequences.

This one test catches essentially every silent attention bug. Perform it once,
keep it in the suite, and never delete it.

### 4.4 Correctness contracts

| Contract | Test |
|---|---|
| Param count matches arithmetic | `test_param_count_exact` |
| Causality | `test_causal_mask` — perturbing token `t+1` never changes the logits at `t` |
| SWA width | `test_swa_window` — token `t` is influenced by exactly `t-w+1 … t` |
| Global layers see everything | `test_global_layer_reach` — token 0 influences the final position |
| GQA head grouping | `test_gqa_grouping` — each KV head serves exactly 4 query heads |
| RoPE relative property | `test_rope_relative` — attention score depends on `(i-j)`, not on `i`, `j` |
| Reference parity | `test_llama_parity` — §4.3 |
| KV cache equivalence | `test_cache_matches_full` — incremental decode equals a full forward pass |
| No NaN at long context | `test_forward_32k_finite` — random 32,768-token input, all outputs finite |

`test_cache_matches_full` is the highest-value test in the suite: KV-cache bugs
produce output that is fluent and subtly wrong, which is the hardest failure
class to notice by reading samples.

---

## 5. Deliverables

| Artifact | Path |
|---|---|
| Model implementation | `n32/model/*.py` |
| Contract tests | `n32/model/test_*.py` |
| Parameter report | `results/model/param_report.json` |
| KV-cache scaling table | `results/model/kv_scaling.json` |
| Public result | `docs/pipeline/results/P04.md` |

`param_report.json` must break down embedding vs non-embedding, per-layer, and
per-component — **R4**.

---

## 6. Gate

| Metric | Threshold |
|---|---|
| Param count vs arithmetic | **exact match** |
| Non-embedding params | **≤60 M** (expected 33.83 M) |
| All contract tests | **pass** |
| HF reference parity | max logit delta **<1e-4** |
| Forward at 32,768 tokens | completes, all-finite, **<8 GB** VRAM |
| KV cache at 32k | **≤50 MB** (expected 38.7 MB) |
| `npm run verify` | green |

---

## 7. Failure modes

| Symptom | Cause | Action |
|---|---|---|
| Param count off by `V × d` | Embeddings not actually tied | Check that the output head is the same tensor, not a copy |
| Parity test fails at ~1e-2 | RoPE applied to V, or wrong dimension pairing | RoPE applies to Q and K only |
| SWA width test off by one | Inclusive/exclusive boundary | Window `w` at position `t` covers `[t-w+1, t]` |
| OOM at 32k forward | Materializing the full attention matrix | Use `F.scaled_dot_product_attention`; never build an `n×n` mask tensor at 32k |
| Loss diverges immediately (later, at P05) | Output projections not scaled by `1/sqrt(2L)` | §4.2 |

---

## 8. Do not

- Do not use `transformers` for the model. Use it only as the parity reference in §4.3.
- Do not add dropout, MoE, or any extra mechanism at this stage. This is the **baseline**; novelty enters through [P13](P13-quantum-inspired-training-lab.md) and [P14](P14-theoretical-model-triage.md), measured against this.
- Do not build an explicit `[n, n]` attention mask. At 32k that is 1.07 × 10⁹ entries.
- Do not change the config after [P05](P05-training-harness.md) starts, except through [P07](P07-scaling-microlaws.md) with a measured study.

---

**Next:** [P05 — Training harness](P05-training-harness.md)
