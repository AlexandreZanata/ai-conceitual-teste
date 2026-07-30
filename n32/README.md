# `n32/` — source tree

Empty by design. Each module is built by the stage that owns it — read that stage's spec before writing in it.

| Module | Built by | Contents |
|---|---|---|
| `data/` | [P02](../docs/pipeline/P02-data-foundation.md) | Acquisition, cleaning, dedup, tokenization, decontamination |
| `tokenizer/` | [P03](../docs/pipeline/P03-tokenizer.md) | BPE training and evaluation |
| `model/` | [P04](../docs/pipeline/P04-baseline-architecture.md), [P08](../docs/pipeline/P08-efficient-attention.md), [P09](../docs/pipeline/P09-long-context-extension.md) | Config, attention, layers, RoPE |
| `train/` | [P05](../docs/pipeline/P05-training-harness.md), [P15](../docs/pipeline/P15-instruction-and-behavior.md) | Loop, optimizer, schedule, checkpointing, SFT |
| `eval/` | [P06](../docs/pipeline/P06-evaluation-harness.md), [P10](../docs/pipeline/P10-long-context-evaluation.md), [P17](../docs/pipeline/P17-external-benchmarking.md) | BPB, long-context probes, benchmarks |
| `serve/` | [P11](../docs/pipeline/P11-throughput-engineering.md), [P12](../docs/pipeline/P12-quantization-and-runtime.md), [P16](../docs/pipeline/P16-grounding-and-retrieval.md) | KV cache, quantized runtime, retrieval |
| `research/` | [P13](../docs/pipeline/P13-quantum-inspired-training-lab.md), [P14](../docs/pipeline/P14-theoretical-model-triage.md) | Quantum-inspired and theoretical probes |
| `../bench/` | [P00](../docs/pipeline/P00-charter-and-hardware-envelope.md), [P11](../docs/pipeline/P11-throughput-engineering.md) | Hardware profiling, throughput, latency, memory |

## Rules

- **Cyclomatic complexity ≤10 per function.** Line caps are waived. Extract rather than nest.
- **Exactly one training entry point:** `n32.train.loop`. Law R6.
- Tests live beside the code as `test_*.py` and assert behaviour, never document contents.
- Every module gets a CLI via `python3 -m n32.<module>.<entry>`, wired to an npm script that a stage references.
- Heavy output goes to `data/`, `runs/`, `artifacts/`, `results/` — all gitignored. See [`REPO-HYGIENE.md`](../docs/REPO-HYGIENE.md).
