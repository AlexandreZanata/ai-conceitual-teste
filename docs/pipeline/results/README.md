# Stage results — the scoreboard

> One file per completed stage. **If a stage is not here, it did not happen.**

This directory is the project's only record of progress. A stage result is
written **after** its gate passes — never before, and never as a progress update.

## Status

| Stage | Title | Status |
|---|---|---|
| [P00](../P00-charter-and-hardware-envelope.md) | Charter and hardware envelope | not started |
| [P01](../P01-ground-truth-reset.md) | Ground-truth reset | not started |
| [P02](../P02-data-foundation.md) | Data foundation | not started |
| [P03](../P03-tokenizer.md) | Tokenizer | not started |
| [P04](../P04-baseline-architecture.md) | Baseline architecture | not started |
| [P05](../P05-training-harness.md) | Training harness | not started |
| [P06](../P06-evaluation-harness.md) | Evaluation harness | not started |
| [P07](../P07-scaling-microlaws.md) | Scaling micro-laws | not started |
| [P08](../P08-efficient-attention.md) | Efficient attention | not started |
| [P09](../P09-long-context-extension.md) | Long-context extension | not started |
| [P10](../P10-long-context-evaluation.md) | Long-context evaluation | not started |
| [P11](../P11-throughput-engineering.md) | Throughput engineering | not started |
| [P12](../P12-quantization-and-runtime.md) | Quantization and runtime | not started |
| [P13](../P13-quantum-inspired-training-lab.md) | Quantum-inspired training lab | not started |
| [P14](../P14-theoretical-model-triage.md) | Theoretical model triage | not started |
| [P15](../P15-instruction-and-behavior.md) | Instruction and behaviour | not started |
| [P16](../P16-grounding-and-retrieval.md) | Grounding and retrieval | not started |
| [P17](../P17-external-benchmarking.md) | External benchmarking | not started |
| [P18](../P18-release-and-publication.md) | Release and publication | not started |

Update the status row in the same commit that adds the result file.

## Format

Fixed by [P19 §7](../P19-agent-operating-protocol.md#7-writing-a-stage-result).
Maximum one page: gate table, artifacts with hashes, what was learned, what was
surprising, and one sentence for the next stage.

## Rules

1. A file here means the gate **passed**, with committed artifacts.
2. A failed gate produces no file here — it produces an entry in [`docs/negative_results.md`](../../negative_results.md).
3. Results are **append-only**. Corrections are new files (`P07-revision-1.md`), never edits.
4. Every number here points at a file under `results/` with a SHA-256.
