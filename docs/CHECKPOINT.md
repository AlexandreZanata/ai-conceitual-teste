# Paper checkpoint

> **What this is:** the single place where paper material accumulates, one stage at a time.
> **What to do with it:** every time a gate passes, tick the stage and fill in the measured number. When the stop condition in §1 is met, **stop the pipeline and write the paper from this file alone.**
>
> **Why it exists:** the previous programme wrote 789 documents and, at the end, could not assemble a paper — 251 reports cited a `formal.json` that never existed. Collecting evidence at the end does not work. It is collected here as it is produced, or it is not collected.

---

## 1. Stop conditions

There are two. **Checkpoint A** is a real, publishable systems paper. **Checkpoint B** is the full paper. Do not skip A — if the project stalls after A, you still have a publication.

| | Reached when | Paper it supports | Claim |
|---|---|---|---|
| **Checkpoint A** | P00–P12 all `PASS` | *A 32k-context language model trained end to end on one consumer laptop* | Systems and efficiency. No capability claims. |
| **Checkpoint B** | P00–P17 all `PASS` | The above, plus external benchmarks, behaviour, and the research tracks | Capability relative to named baselines |

P18 is release mechanics — packaging, licences, third-party reproduction. It is not required to write, only to publish.

**When a checkpoint is reached: stop opening stages.** Writing the paper is the next task, not P13.

---

## 2. Stage progress

Tick only when `docs/pipeline/results/PXX.md` exists. Nothing else counts as done.

### Foundation
| ✓ | Stage | Gate | Measured |
|:-:|---|---|---|
| ☑ | [P00](pipeline/P00-charter-and-hardware-envelope.md) Hardware envelope | Reproducible profile committed | sustained TFLOP/s: **24.577** · usable VRAM: **7174 MB** · feasible: **true** (45.8 h) |
| ☑ | [P01](pipeline/P01-ground-truth-reset.md) Ground-truth reset | ≤40 scripts, verify green, ≥1 failing-capable test | scripts: **39** · tests: **7** · train entries: **1** |
| ☑ | [P02](pipeline/P02-data-foundation.md) Data foundation | ≥4B deduplicated tokens, licence-clean | tokens: **4.417 B** · exact removed: **1.88%** · near residual: **0.018%** |
| ☐ | [P03](pipeline/P03-tokenizer.md) Tokenizer | ≤3.6 bytes/token at vocab 16,384 | bytes/token: `___` |

### Core
| ✓ | Stage | Gate | Measured |
|:-:|---|---|---|
| ☐ | [P04](pipeline/P04-baseline-architecture.md) Baseline architecture | Param count exact; parity tests pass | non-emb: `___` M · emb: `___` M |
| ☐ | [P05](pipeline/P05-training-harness.md) Training harness | Bit-exact resume; ≥25% MFU | MFU: `___`% |
| ☐ | [P06](pipeline/P06-evaluation-harness.md) Evaluation harness | Held-out BPB reproducible to ±0.001 | BPB variance: `___` |
| ☐ | [P07](pipeline/P07-scaling-microlaws.md) Scaling micro-laws | Fitted law predicts held-out loss within 3% | prediction error: `___`% |

### Long context — the differentiator
| ✓ | Stage | Gate | Measured |
|:-:|---|---|---|
| ☐ | [P08](pipeline/P08-efficient-attention.md) Efficient attention | KV ≤50 MB @32k; BPB regression ≤0.5% | KV: `___` MB · ΔBPB: `___`% |
| ☐ | [P09](pipeline/P09-long-context-extension.md) Context extension | BPB non-increasing to position 32,768 | BPB @32k: `___` |
| ☐ | [P10](pipeline/P10-long-context-evaluation.md) Long-context evaluation | ≥90% needle retrieval at 32k, all depths | retrieval: `___`% |

### Systems
| ✓ | Stage | Gate | Measured |
|:-:|---|---|---|
| ☐ | [P11](pipeline/P11-throughput-engineering.md) Throughput | ≥100 tok/s @8k; TTFT ≤400 ms | tok/s: `___` · TTFT p99: `___` ms |
| ☐ | [P12](pipeline/P12-quantization-and-runtime.md) Quantization | ≤120 MB int8; ≤1% BPB loss; ≥15 tok/s CPU | size: `___` MB · CPU: `___` tok/s |

> **↑ CHECKPOINT A — stop here and write the systems paper.**

### Research tracks and capability
| ✓ | Stage | Gate | Measured |
|:-:|---|---|---|
| ☐ | [P13](pipeline/P13-quantum-inspired-training-lab.md) Quantum-inspired lab | ≥8 hypotheses resolved with artifacts | promoted: `___` · falsified: `___` |
| ☐ | [P14](pipeline/P14-theoretical-model-triage.md) Theoretical triage | 100 catalogued, top-10 costed, ≥3 tested | tested: `___` · promoted: `___` |
| ☐ | [P15](pipeline/P15-instruction-and-behavior.md) Instruction and behaviour | Instruction gain, no BPB regression | Δ instruct: `___` · ΔBPB: `___` |
| ☐ | [P16](pipeline/P16-grounding-and-retrieval.md) Grounding and retrieval | Generation and retrieval scored separately | gen: `___` · retrieval: `___` |
| ☐ | [P17](pipeline/P17-external-benchmarking.md) External benchmarking | Public numbers vs named baselines | see §4 |

> **↑ CHECKPOINT B — stop here and write the full paper.**

| ☐ | [P18](pipeline/P18-release-and-publication.md) Release | Third party reproduces from a clean clone | — |

---

## 3. Headline numbers

The five numbers the paper is built around. Each needs a JSON artifact behind it, or it does not go in the paper.

| # | Claim | Target | Measured | Artifact | SHA-256 verified |
|---|---|---|---|---|:---:|
| 1 | Non-embedding parameters | ≤60 M | `___` | | ☐ |
| 2 | Context window with measured retrieval | 32,768 @ ≥90% | `___` | | ☐ |
| 3 | Held-out bits-per-byte | competitive with ~10× larger | `___` | | ☐ |
| 4 | Throughput at 8k context | ≥100 tok/s | `___` | | ☐ |
| 5 | Total training wall time | <72 h on one RTX 4060 | `___` | | ☐ |

---

## 4. Baseline comparison table

Filled by [P17](pipeline/P17-external-benchmarking.md). Every competitor must be run **on this hardware, by us**, or the number must be cited to its source with a link. Never mix the two silently.

| Model | Non-emb params | Context | Held-out BPB | tok/s @8k | Source |
|---|---:|---:|---:|---:|---|
| **N32-base (ours)** | | 32,768 | | | this work |
| | | | | | |

---

## 5. Paper skeleton

One row per section. Write nothing until the "evidence ready" column is fully ticked.

| Section | Content | Comes from | Evidence ready |
|---|---|---|:---:|
| Abstract | The five numbers in §3 | §3 | ☐ |
| 1. Introduction | Small models are parameter-misallocated, not capacity-limited | [assessment §2.4](ASSESSMENT-2026-07-30.md#24-the-parameter-budget-was-spent-on-the-wrong-thing) | ☐ |
| 2. Hardware envelope | What one consumer laptop actually sustains | P00 | ☑ |
| 3. Data | Corpus, dedup, decontamination, licences | P02 · [DATA-PROVENANCE](DATA-PROVENANCE.md) | ☑ |
| 4. Vocabulary as budget | 16,384 vocab → 256× more transformer at equal total params | P03 · [pipeline §3](pipeline/README.md#3-why-the-vocabulary-is-the-headline-change) | ☐ |
| 5. Architecture | GQA + sliding-window/global hybrid; 38.7 MB KV at 32k | P04 · P08 | ☐ |
| 6. Training | Progressive context extension, MFU, cost | P05 · P09 | ☐ |
| 7. Scaling | Fitted micro-law and its prediction error | P07 | ☐ |
| 8. Long-context evaluation | Positional BPB, needle, ablations, tracking | P10 | ☐ |
| 9. Systems | Throughput, latency distribution, int8 runtime | P11 · P12 | ☐ |
| 10. Research tracks | Quantum-inspired and theoretical results — **including the falsifications** | P13 · P14 · ledgers | ☐ |
| 11. Negative results | Everything that was killed, and why | [negative_results](negative_results.md) | ☐ |
| 12. Limitations | §7 below, unedited | §7 | ☐ |
| Reproduction | Clean-clone instructions | P18 · [REPO-HYGIENE](REPO-HYGIENE.md) | ☐ |

**Section 11 is not optional and does not go in an appendix.** The failure ledger is the most credible part of this project's history, and burying it is how the previous programme talked itself into believing its own numbers.

---

## 6. Verification before writing a single word

Run this. Every line must be clean. The previous programme skipped exactly this step.

```bash
# 1. Every stage claimed complete has a result file
ls docs/pipeline/results/

# 2. Every artifact cited in this file exists
#    (no citation to a file that was never written — this is what went wrong before)

# 3. Every artifact carries provenance
#    each JSON must contain: git_hash, config_hash, seed, wall_seconds

# 4. The headline numbers are reproducible from a clean clone
npm run verify && npm run eval:all
```

| Check | Rule |
|---|---|
| Numbers in the paper | Must appear verbatim in a committed JSON artifact |
| Numbers in §3 and §4 | Must have the SHA-256 box ticked |
| Any comparison | Must carry a confidence interval |
| Any retrieval-assisted result | Must be reported separately from generation |
| Any hypothesis mentioned | Must be `PROMOTE` or `FALSIFY` — never `HOLD` |

---

## 7. What may and may not be claimed

Write this section of the paper first, while the temptation is smallest.

| May claim, if measured | May never claim |
|---|---|
| Trained on one consumer GPU in N hours | "Efficient" without the FLOP count |
| 32k context with X% measured retrieval | 32k context on architecture alone, unmeasured |
| BPB of X vs baseline Y on the same held-out set | Better than a model evaluated on a different set |
| Retrieval-augmented accuracy of X, retrieval reported separately | A combined score that hides which component answered |
| Hypothesis H falsified, with its classical control named | A quantum-inspired gain without the classical control it beat |
| N of 100 catalogue entries tested | 100 architectures "explored" |

**On the quantum track specifically:** there is no quantum hardware here. Every entry is a classical algorithm. A result is admissible only if it names the classical technique it most resembles and beats it. See [P13](pipeline/P13-quantum-inspired-training-lab.md).

---

## 8. When a checkpoint is reached

1. Stop opening stages. Do not start P13 because P12 passed.
2. Run §6 in full. Fix every unticked box before writing.
3. Write the paper into `paper/`, sourcing **only** from this file and the artifacts it cites.
4. Any number that cannot be traced to a committed artifact is **removed from the paper**, not softened.
5. If removing untraceable numbers empties a section, that section describes work that was not actually done. Say so in §12 Limitations.
