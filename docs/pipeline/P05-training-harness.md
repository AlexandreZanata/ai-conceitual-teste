# P05 — Training harness

> **Stage:** 5 of 19 · **Estimate:** 2 days build + ~32 h training · **GPU time:** ~35 h
> **Precondition:** [P04](P04-baseline-architecture.md) `PASS`
> **Gate:** bit-exact resume, ≥25% MFU, and a completed 4B-token run.

---

## 1. Why this stage exists

The previous programme ran **one training job of ~120 optimizer steps** and never
persisted a loss curve. This stage builds a harness that can run for 35 hours on
a laptop that will sleep, thermally throttle, and occasionally crash — and prove
afterwards that the run was what it claims to be.

**Laws at risk: R2** (every run emits a committed artifact), **R5** (this is the stage that actually spends the FLOPs).

---

## 2. Training configuration

| Setting | Value | Reasoning |
|---|---|---|
| Optimizer | AdamW, `β = (0.9, 0.95)`, `eps = 1e-8` | `β₂ = 0.95` is standard for LM pretraining; 0.999 adapts too slowly |
| Weight decay | 0.1, **excluding** norms and embeddings | Decaying embeddings at small vocab hurts rare tokens |
| Peak LR | **6e-4** | Roughly `0.003 / ln(N_nonembed)`; verify with the [P07](P07-scaling-microlaws.md) sweep |
| Schedule | Linear warmup 2,000 steps → cosine decay to **10%** of peak | Decaying to zero wastes the final tokens; 10% floor is measurably better |
| Grad clip | 1.0 global norm | Non-negotiable at this scale |
| Precision | **bf16** autocast, fp32 master weights | bf16 needs no loss scaling; fp16 will diverge |
| Sequence length | 2,048 (extended at [P09](P09-long-context-extension.md)) | Training long from scratch is wasteful — >90% of tokens do not need it |
| Micro-batch | 16 × 2,048 = 32,768 tokens | Largest that fits with checkpointing; confirm against [P00](P00-charter-and-hardware-envelope.md) |
| Grad accumulation | 16 | → **524,288 tokens per optimizer step** |
| Total steps | **≈ 7,630** | 4.0 B ÷ 524,288 |
| Epochs | **1** | 4B unique tokens; repetition is strictly worse than fresh data |

### Why a 524k-token batch

Large batches with few steps suit a machine that may be interrupted: fewer
optimizer states to checkpoint, more work per step, and better GPU utilization.
The critical batch size for a 42M model is well above 500k tokens, so there is no
convergence penalty.

---

## 3. Memory budget (8 GB, must be checked before launch)

| Item | Bytes | Size |
|---|---|---:|
| Params (bf16) | 42.2 M × 2 | 84 MB |
| Master weights (fp32) | 42.2 M × 4 | 169 MB |
| AdamW `m` + `v` (fp32) | 42.2 M × 8 | 338 MB |
| Gradients (fp32) | 42.2 M × 4 | 169 MB |
| **Model state total** | | **760 MB** |
| Activations, 16 × 2048, with checkpointing | ~12 layers × recompute | ~3.2 GB |
| Attention workspace (flash/SDPA) | | ~0.4 GB |
| Fragmentation and allocator slack | | ~0.6 GB |
| **Peak** | | **≈ 5.0 GB** |

**Headroom: ~2.4 GB of the ~7.4 GB usable.** If measured peak exceeds 6.5 GB,
reduce micro-batch to 8 and raise accumulation to 32 — token count per step is
unchanged.

---

## 4. Steps

### 4.1 Dataloader

`n32/train/data.py`. Requirements, all of which matter for a 35-hour run:

- Memory-map `uint16` shards; **never** load a shard into RAM.
- Deterministic shuffling from `(seed, epoch)` — the exact sample order must be reconstructible.
- Document packing to fixed 2,048-token sequences with `<|endoftext|>` separators.
- **Cross-document attention masking** — sequences packed from different documents must not attend across the boundary. Skipping this is a small but free quality loss.
- 4 worker processes with `pin_memory`; more will contend with the 16-thread CPU.
- Prefetch depth 2. If the loader starves the GPU, MFU collapses and the run silently doubles in length.

### 4.2 Training loop

`n32/train/loop.py`:

```bash
npm run train -- --config configs/n32-base.yaml --out runs/n32-base-001
```

Mandatory features:

| Feature | Requirement |
|---|---|
| `torch.compile` | `mode="max-autotune"`; expect a 3–5 min first-step cost and 20–40% throughput gain |
| Activation checkpointing | Every layer; mandatory within 8 GB |
| Fused AdamW | `fused=True` |
| Checkpoint cadence | Every 250 steps **and** on SIGTERM/SIGINT |
| Checkpoint contents | model, optimizer, scheduler, dataloader position, RNG states (Python, NumPy, torch CPU, torch CUDA), step, config hash, git hash |
| Checkpoint retention | Last 3 + every 1,000 steps, to bound disk use |
| Logging | JSONL every 10 steps |
| Held-out eval | Every 250 steps on 2M tokens; **BPB, not loss** |
| Throughput log | tokens/s, MFU, peak VRAM, GPU temperature |
| NaN guard | On non-finite loss, dump batch and state, then halt |

### 4.3 Bit-exact resume

The contract that makes a 35-hour run trustworthy:

```
test_resume_bitexact:
  A = train 10 steps from seed S      -> record loss[0..9], final params
  B = train 5 steps, checkpoint, resume, train 5 more
  assert allclose(A.params, B.params, atol=0)   # exact, not approximate
  assert A.loss == B.loss                        # elementwise exact
```

If this fails, the RNG or dataloader position is not being restored, and every
resumed run is scientifically worthless because its data order is unknown.

### 4.4 Smoke before committing 35 hours

```bash
npm run train:smoke -- --steps 100 --config configs/n32-base.yaml
```

Must confirm, in order:

1. Loss falls from ≈ `ln(16384) = 9.70` to **<7.0** within 100 steps.
2. Measured MFU ≥20%.
3. Peak VRAM <6.5 GB.
4. No NaN, no gradient-norm spikes above 10.
5. Extrapolated wall clock within 20% of [P00](P00-charter-and-hardware-envelope.md)'s `budget.json`.

**A loss that does not leave 9.70 means the model is not learning at all** —
almost always a label-shift bug (predicting position `t` from position `t`).

### 4.5 The full run

```bash
nohup npm run train -- --config configs/n32-base.yaml --out runs/n32-base-001 &
```

Practical laptop discipline:

- Disable sleep and suspend: `systemd-inhibit --what=idle:sleep`.
- Expect thermal throttling; measure the plateau, not the first hour.
- Monitor with `nvidia-smi dmon`; log the temperature to the run JSONL.
- Check the loss curve at 500 / 2,000 / 5,000 steps against §6 predictions.
- Losing power is survivable — that is what §4.3 is for.

---

## 5. Deliverables

| Artifact | Path |
|---|---|
| Training loop | `n32/train/*.py` |
| Run config | `configs/n32-base.yaml` |
| Metrics stream | `runs/n32-base-001/metrics.jsonl` |
| Checkpoints | `runs/n32-base-001/ckpt_*.pt` (gitignored) |
| Final model | `artifacts/models/n32-base.pt` |
| Loss curve | `results/train/loss_curve.json` + `.svg` |
| Run manifest | `results/train/run_manifest.json` |
| Public result | `docs/pipeline/results/P05.md` |

`run_manifest.json` carries git hash, config hash, data manifest hash, seed,
total tokens, wall time, mean MFU, final BPB, and the count of interruptions.
**This is the artifact that makes the run a fact rather than a claim.**

---

## 6. Gate

| Metric | Threshold |
|---|---|
| `test_resume_bitexact` | **passes exactly** |
| Sustained MFU | **≥25%** |
| Tokens trained | **≥4.0 × 10⁹** |
| Held-out BPB at completion | **≤1.45** (P05 bar; ≤1.35 is the programme target after [P09](P09-long-context-extension.md)) |
| Loss curve | monotone decreasing over any 500-step window |
| NaN or divergence events | **0** |
| Peak VRAM | **<7.0 GB** |

### Predicted trajectory — check against these

| Step | Tokens | Expected train loss | Expected BPB |
|---:|---:|---:|---:|
| 0 | 0 | 9.70 | — |
| 100 | 52 M | ~6.5 | — |
| 500 | 262 M | ~4.6 | ~1.95 |
| 2,000 | 1.05 B | ~3.9 | ~1.65 |
| 5,000 | 2.62 B | ~3.5 | ~1.48 |
| 7,630 | 4.00 B | **~3.3** | **~1.40** |

Deviating by more than ~15% at step 2,000 means something is wrong. **Stop and
diagnose rather than waiting 30 hours to find out.**

---

## 7. Failure modes

| Symptom | Cause | Action |
|---|---|---|
| Loss stuck at 9.70 | Label shift bug | Assert `logits[:, :-1]` predicts `tokens[:, 1:]` |
| Loss → NaN around step 500 | LR too high, or fp16 instead of bf16 | Lower peak LR to 3e-4; confirm bf16; check QK-norm is active |
| MFU <15% | Dataloader starvation | Raise workers to 6, prefetch to 4; verify disk read from [P00](P00-charter-and-hardware-envelope.md) |
| Throughput drops 30% after 1 h | Thermal throttling | Expected. Re-baseline the budget from the plateau. |
| Loss spikes then recovers | Bad data shard | Log the offending batch; if repeated, re-run [P02](P02-data-foundation.md) cleaning |
| Resume changes the loss | RNG or loader position not restored | Fix before any long run; do not "accept the small difference" |
| `torch.compile` recompiles constantly | Variable shapes | Pad to fixed shapes; set `dynamic=False` |

---

## 8. Do not

- Do not train for more than one epoch. Fetch more data instead.
- Do not use fp16. bf16 or fp32 only.
- Do not skip the 100-step smoke test to save 10 minutes before a 35-hour run.
- Do not tune hyperparameters mid-run. Kill it, fix the config, restart, and record why.
- Do not report loss where BPB is available.
- Do not delete `metrics.jsonl`. It is the only record that the run happened.

---

**Next:** [P06 — Evaluation harness](P06-evaluation-harness.md)
