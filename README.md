# N32 — a 32k-context language model that fits on a laptop

> **Objective:** train a causal language model with **≤60M non-embedding parameters** and a **32,768-token context window** that reaches **held-out bits-per-byte competitive with models ~10× larger**, runs at **≥100 tok/s on an RTX 4060**, and is trained **end to end on one machine in under 72 hours**.

**Status:** redirected 2026-07-30. The previous research programme (waves W–BH) is frozen. Read [`docs/ASSESSMENT-2026-07-30.md`](docs/ASSESSMENT-2026-07-30.md) for why, in full and without softening.

---

## Start here

| You are | Read |
|---|---|
| **An agent picking up this work** | [`docs/pipeline/P19-agent-operating-protocol.md`](docs/pipeline/P19-agent-operating-protocol.md) — **first, always** |
| Evaluating the project | [`docs/ASSESSMENT-2026-07-30.md`](docs/ASSESSMENT-2026-07-30.md) |
| Looking for the plan | [`docs/pipeline/README.md`](docs/pipeline/README.md) |
| Looking for progress | [`docs/pipeline/results/`](docs/pipeline/results/README.md) |

```bash
ls docs/pipeline/results/    # highest-numbered file = last completed stage
```

That command is the entire status report. If a stage is not there, it did not happen.

---

## The design in one table

| Property | Value | Why |
|---|---:|---|
| Non-embedding parameters | **33.8 M** | The real model |
| Embedding parameters | 8.4 M | 16,384-token domain vocabulary |
| Layers × width | 12 × 512 | Depth beats width at fixed budget |
| Attention | Sliding window 1024, global every 6th | 32k context in **38.7 MB** of KV cache |
| Grouped-query attention | 2 KV heads of 8 | 4× cache reduction |
| Context | **32,768 tokens** ≈ 115 KB of text | Progressive extension, RoPE base 10⁶ |
| Training | 4.0 B tokens, ~39 GPU-hours | One RTX 4060 Mobile |
| Target quality | **BPB ≤1.35** | Competitive with ~150M-parameter models |

Full specification: [`docs/pipeline/README.md §2`](docs/pipeline/README.md#2-the-reference-design-n32-base).

### The change that makes this work

The previous model spent **96% of its parameters on a 50,257-entry GPT-2 embedding table**, leaving **132K parameters** of actual transformer. Dropping to a 16,384-token domain vocabulary at `d_model=512` yields **33.8M** parameters of real model at the same total size — **256× more model**, for one day of work.

---

## Hardware

Every budget in this project is derived from measurements on this machine, not from datasheets.

| Component | Specification |
|---|---|
| GPU | NVIDIA RTX 4060 Mobile, **8 GB VRAM**, CUDA 13.0 |
| CPU | Intel i7-13620H, 10 cores / 16 threads |
| RAM | 31 GB |
| Disk | 214 GB free |
| PyTorch | 2.12.1+cu130 |

---

## The pipeline

Nineteen stages, run in order. A stage opens only when the previous gate passes with a committed artifact. **One file per stage**, each containing its objective, exact steps, numeric gate, predicted results, and failure modes.

| Phase | Stages | Delivers |
|---|---|---|
| **Foundation** | [P00](docs/pipeline/P00-charter-and-hardware-envelope.md)–[P03](docs/pipeline/P03-tokenizer.md) | Measured hardware envelope, 4B-token corpus, domain tokenizer |
| **Core** | [P04](docs/pipeline/P04-baseline-architecture.md)–[P07](docs/pipeline/P07-scaling-microlaws.md) | Trained model, evaluation harness, measured scaling laws |
| **Long context** | [P08](docs/pipeline/P08-efficient-attention.md)–[P10](docs/pipeline/P10-long-context-evaluation.md) | 32k context that is measurably used, not just accepted |
| **Systems** | [P11](docs/pipeline/P11-throughput-engineering.md)–[P12](docs/pipeline/P12-quantization-and-runtime.md) | ≥100 tok/s GPU, ≥15 tok/s CPU-only, ≤120 MB |
| **Research** | [P13](docs/pipeline/P13-quantum-inspired-training-lab.md)–[P14](docs/pipeline/P14-theoretical-model-triage.md) | Quantum-inspired training hypotheses, 100-architecture catalogue |
| **Release** | [P15](docs/pipeline/P15-instruction-and-behavior.md)–[P18](docs/pipeline/P18-release-and-publication.md) | Instruction tuning, honest benchmarks, reproducible release |
| **Governance** | [P19](docs/pipeline/P19-agent-operating-protocol.md) | How to work here |

---

## Research tracks

Two parallel tracks that may never block the main objective:

- **[Quantum-inspired training](docs/pipeline/P13-quantum-inspired-training-lab.md)** — 12 hypotheses drawn from tensor networks, unitary evolution, and amplitude interference. No quantum hardware, no quantum claims: each is a classical algorithm benchmarked against the classical technique it most resembles. Falsifications count as full passes.
- **[100 theoretical architectures](docs/hypotheses/README.md)** — a fixed-size catalogue, ~80 words each, triaged by impact and falsifiability. An idea earns depth by surviving triage, and depth means a training run.

---

## The seven laws

Derived from the documented failure. Every stage restates the ones it is most at risk of violating.

| # | Law |
|---|---|
| R1 | Held-out bits-per-byte is the primary metric. Every stage reports it. |
| R2 | No claim without a committed artifact carrying git hash, config hash, seed, and wall time. **Markdown is never evidence.** |
| R3 | Retrieval and generation are measured separately, always. |
| R4 | Embedding and non-embedding parameters are always reported separately. |
| R5 | A stage that costs no FLOPs is not a research stage. |
| R6 | One pipeline. No waves, no letters, no forever packs. |
| R7 | A failed gate stops the pipeline. **Gates are never weakened to pass.** |

---

## Quality gates

```bash
npm run verify    # hygiene · cyclomatic ≤10 · lint 0/0 · tests — required before every commit
```

| Gate | Cap |
|---|---|
| Repository hygiene | no binaries, no secrets, no file >1 MB, ≤400 tracked files, ≤40 npm scripts |
| Cyclomatic complexity | ≤10 per function |
| Lint | 0 errors, 0 warnings |
| Tests | all pass |

Enforced by Lefthook on every commit and push. **What may and may not enter git:** [`docs/REPO-HYGIENE.md`](docs/REPO-HYGIENE.md).

---

## Frozen history

The previous programme's tree — 1,523 source files, 573 wave reports, the EvoGen C++ PoC, and the old rules harness — was **deleted** on 2026-07-30. It survives, byte-identical, in one git tag:

```bash
git checkout legacy/waves-w-bh              # the whole tree as it stood
git show legacy/waves-w-bh:path/to/file     # one file
```

A tag is a better archive than a directory: perfectly recoverable, but invisible to search, impossible to import, and impossible to extend by accident. It exists so [`docs/ASSESSMENT-2026-07-30.md`](docs/ASSESSMENT-2026-07-30.md) stays independently checkable. **That is its only purpose — do not check it out to look for reusable code.** [P01](docs/pipeline/P01-ground-truth-reset.md) §2.2 lists what was salvaged and why the rest was not.
