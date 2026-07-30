# P00 — Charter and hardware envelope

> **Stage:** 0 of 19 · **Estimate:** 2 hours · **GPU time:** ~15 min
> **Precondition:** none. This is the entry point.
> **Gate:** a committed, reproducible hardware profile with measured (not datasheet) throughput.

---

## 1. Why this stage exists

The previous programme designed a model without ever measuring what the machine
could do, then concluded the machine was the constraint. It was not: the GPU sat
at 31 MB of 8,188 MB used. Every budget in this pipeline is derived from measured
throughput, so that measurement must be taken first and must be re-takeable.

**Law at risk: R2** — the hardware numbers in [`README.md`](README.md#5-compute-budget--the-whole-point) are currently *estimates*. This stage replaces them with measurements.

---

## 2. Reference hardware (audited 2026-07-30)

| Component | Specification |
|---|---|
| GPU | NVIDIA GeForce RTX 4060 Max-Q / Mobile (AD107M), **8,188 MB VRAM** |
| Driver / CUDA | 580.173.02 / **CUDA 13.0** |
| CPU | Intel i7-13620H — 10 cores (6P+4E), 16 threads, 4.9 GHz boost |
| Cache | L2 9.5 MB, L3 24 MB |
| RAM | 31 GB, ~10 GB available under normal desktop load |
| Swap | 19 GB |
| Disk | 460 GB total, **214 GB free** |
| OS | Linux 7.0.11-76070011-generic |
| Python | 3.12.2 |
| PyTorch | 2.12.1+cu130, `cuda.is_available() == True` |
| Node | v26.3.1 |

### Binding constraints, in order

1. **8 GB VRAM** — determines batch size, `d_model`, and whether activation checkpointing is mandatory (it is).
2. **~10 GB free RAM** — determines dataloader worker count and shard size. Do not memory-map a 14 GB corpus into RAM.
3. **Laptop thermals** — sustained load will throttle. Budgets assume **sustained**, not burst, clocks. Measure after 10 minutes of load, never at second 30.
4. **Single GPU** — no data or model parallelism. Every design must fit one device.

---

## 3. Steps

### 3.1 Create the profiler

Create `bench/hw_profile.py`. It must measure, not report datasheet values.

| Measurement | Method | Why |
|---|---|---|
| Peak bf16 matmul TFLOP/s | 4096³ `torch.matmul`, 50 iters after 10 warmup, median | Upper bound on training speed |
| **Sustained** bf16 TFLOP/s | same loop run for **10 minutes**, report final-minute median | Thermal reality |
| HBM bandwidth | large `copy_` of 1 GB tensors | Bounds memory-bound ops |
| Usable VRAM | allocate until OOM, back off 5% | Real budget, not 8,188 MB |
| Host↔device bandwidth | pinned-memory transfer, 1 GB | Dataloader ceiling |
| Disk sequential read | 4 GB read from the data volume | Determines if the loader starves the GPU |
| CPU bf16 GEMM | `torch.matmul` on CPU, 16 threads | CPU inference fallback budget ([P12](P12-quantization-and-runtime.md)) |

**Required CLI contract:**

```bash
python bench/hw_profile.py --out results/hw/profile.json --sustained-minutes 10
```

### 3.2 Derive the compute budget

Create `bench/compute_budget.py`, which reads `profile.json` and emits the
project's real budget rather than the estimate in the pipeline README.

```bash
python bench/compute_budget.py \
  --profile results/hw/profile.json \
  --params 42200000 --tokens 4e9 --mfu 0.25 \
  --out results/hw/budget.json
```

It must print, and commit to JSON:

- Predicted wall-clock hours for the full 4B-token run
- Maximum tokens trainable in 72 hours at measured throughput
- Maximum model size trainable in 72 hours at 4B tokens
- **A `feasible: true|false` flag** against the 72-hour cap

### 3.3 Confront the result

If `feasible == false`, **do not proceed and do not quietly shrink the target.**
Open [P07](P07-scaling-microlaws.md) early and re-derive the design point from
measured throughput. Record the change in `docs/pipeline/results/P00.md` with the
measured numbers that forced it.

---

## 4. Deliverables

| Artifact | Path |
|---|---|
| Hardware profile | `results/hw/profile.json` |
| Compute budget | `results/hw/budget.json` |
| Profiler source | `bench/hw_profile.py` |
| Budget calculator | `bench/compute_budget.py` |
| Public result | `docs/pipeline/results/P00.md` |

`profile.json` must contain `git_hash`, `timestamp`, `driver_version`,
`torch_version`, and every measurement above. **R2 applies from this stage onward.**

---

## 5. Gate

| Metric | Threshold |
|---|---|
| Sustained bf16 throughput measured over ≥10 min | recorded, non-zero |
| Usable VRAM measured empirically | recorded, ≥7,000 MB |
| Re-running the profiler reproduces TFLOP/s | within **±10%** |
| `budget.json` emits an explicit `feasible` flag | present |

**PASS** = all four. **FAIL** = stop; the machine is not what this pipeline assumes, and every downstream budget is wrong.

---

## 6. Expected values (predictions to check against)

State predictions before measuring — a spec that cannot be wrong teaches nothing.

| Measurement | Prediction | If far off, suspect |
|---|---|---|
| Peak bf16 matmul | 25–35 TFLOP/s | Tensor cores not engaged; check dtype and shape alignment |
| Sustained (10 min) | 15–25 TFLOP/s | Thermal throttling — expected and acceptable |
| Realistic training MFU | 20–30% | Small models are memory-bound; <15% means the loader is starving the GPU |
| Usable VRAM | 7,400–7,900 MB | Desktop compositor holds ~30 MB |
| Disk sequential read | >1 GB/s (NVMe) | If <300 MB/s, shard the corpus and prefetch aggressively |

---

## 7. Failure modes

| Symptom | Cause | Action |
|---|---|---|
| TFLOP/s varies >20% between runs | Thermal state or background load | Always profile from cold; close the browser; record ambient conditions |
| OOM well below 8 GB | Fragmentation, or compositor holding memory | Set `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`; report usable, not total |
| Sustained ≈ peak | Ran too short | The 10-minute window is not optional |
| CPU GEMM near GPU speed | GPU never engaged | Verify `.cuda()` and check `nvidia-smi` during the run |

---

## 8. Do not

- Do not copy datasheet TFLOP/s into any document. Only measured numbers.
- Do not profile with other GPU applications running.
- Do not proceed to [P01](P01-ground-truth-reset.md) with `feasible: false` unmodified.
- Do not tune the model design here. This stage measures the machine; [P07](P07-scaling-microlaws.md) designs the model.

---

**Next:** [P01 — Ground-truth reset](P01-ground-truth-reset.md)
