# Metrics — the single definition source

> **A metric is defined here or it does not exist.** Established by [P06](pipeline/P06-evaluation-harness.md).
>
> The previous programme defined `teacher_lp`, `true_continue`, `L_eff`, and `content_ok` in several places each; the definitions drifted, and comparisons across waves became meaningless. One definition, one location, no exceptions.

---

## Primary

### Bits per byte (BPB) — law R1

\[
\text{BPB} = \frac{1}{B}\sum_{i=1}^{T} -\log_2 P(t_i \mid t_{<i})
\]

where \(T\) is the token count and \(B\) the **byte** length of the same text.

| Rule | Value |
|---|---|
| Accumulation precision | fp32, even when the model runs bf16 |
| Stability | `logsumexp`, never `log(sum(exp(·)))` |
| Byte counting | bytes of the **decoded** text (UTF-8 aware) |
| Special tokens | excluded from numerator and denominator |
| Eval stride | **half the context window**, stated in every report |
| Required alongside | token count, byte count, document count, bootstrap 95% CI |

**Why not perplexity:** perplexity is not comparable across tokenizers. A larger vocabulary predicts fewer, harder tokens and can show lower perplexity while being a worse model. BPB measures compression of the underlying bytes and is tokenization-invariant.

**Reference points on held-out web text:**

| BPB | Interpretation |
|---:|---|
| ~1.20 | Strong 1B-parameter model |
| ~1.00 | Strong 7B-parameter model |
| **≤1.35** | **`N32` success target** |

---

## Model size — law R4

| Metric | Definition |
|---|---|
| **Non-embedding parameters** | All parameters excluding token embeddings and any untied output head |
| **Embedding parameters** | Token embedding matrix (counted once when tied) |
| **Total parameters** | `sum(p.numel() for p in model.parameters())`, tied weights counted once |

All three are always reported together. A single "parameter count" is not admissible.

---

## Long context

| Metric | Definition | Reported as |
|---|---|---|
| **Positional BPB** | BPB per 1,024-token bucket by position | Curve, not a scalar |
| **Needle accuracy** | Exact retrieval of an inserted synthetic fact | **Minimum over depths**, never the mean |
| **Context gain** | `BPB(no context) − BPB(full context)` | With the C3→C4 increment |
| **Variable tracking** | Multi-hop synthetic reference resolution | By hop count and distance |

Defined by [P10](pipeline/P10-long-context-evaluation.md). These three measure different capabilities and are **never aggregated**.

---

## Performance

| Metric | Definition | Rule |
|---|---|---|
| **Decode throughput** | Tokens/second, steady state, batch 1 unless stated | Report the context length |
| **TTFT** | Time from request to first token | Includes prefill |
| **Latency** | **p50 and p99**, never the mean | Cold and warm reported separately |
| **Peak VRAM** | `torch.cuda.max_memory_allocated()` | Per context length |
| **MFU** | Achieved FLOP/s ÷ measured peak from [P00](pipeline/P00-charter-and-hardware-envelope.md) | Against measured, not datasheet |

---

## Generation quality

| Metric | Definition | Fail threshold |
|---|---|---|
| Distinct-2 / distinct-3 | Unique n-gram ratio over 200 samples | <0.5 |
| Repetition rate | Repeated 4-grams within a sample | >0.15 |
| **Degeneration rate** | Samples collapsing to a repeated token | **>0.01** |
| Self-BLEU | Cross-sample diversity | >0.4 |

The degeneration detector exists because the previous model's characteristic failure was emitting `........`. An automatic detector for a known failure mode is mandatory.

---

## Abstention — law R3

Reported as **four cells**, never one number:

| | Model answers | Model abstains |
|---|---|---|
| **Answer in context** | correct / wrong | **over-refusal** |
| **Answer not in context** | hallucination | correct abstention |

Primary scalar: **AUROC of the abstention signal against actual correctness**. It cannot be gamed by refusing more or less often. Over-refusal rate is always reported beside it.

---

## Retrieval — law R3

Four conditions, always all four ([P16](pipeline/P16-grounding-and-retrieval.md)):

| Condition | Context |
|---|---|
| A — closed book | none |
| B — gold | correct document supplied |
| C — retrieved | retriever output |
| D — distractor | plausible wrong document |

Derived: `retrieval contribution = C − A` · `retrieval quality = (C − A)/(B − A)` · `distractor robustness = D − A`.

A single retrieval-augmented accuracy number is not admissible.

---

## Retired metrics — do not use

| Metric | Why retired |
|---|---|
| `teacher_lp` | No committed artifacts; not comparable across tokenizers |
| `true_continue` | Value was 0 in every artifact ever produced; superseded by generation metrics |
| `L_eff` | Could only report good news; no relationship to measured context use |
| `content_ok` | Defined in multiple places, never consistently |
| Perplexity | Not tokenizer-invariant |
| Forever-pack pass rate | Measured string matching, not capability |

---

## Adding a metric

1. Define it here, with its formula and its failure threshold.
2. State how it can report **bad** news. A metric that cannot fail is not a metric.
3. Implement it in `n32/eval/`, with a test proving it fails on deliberately damaged input.
4. Add it to the [P06](pipeline/P06-evaluation-harness.md) regression harness.
