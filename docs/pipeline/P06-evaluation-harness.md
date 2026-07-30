# P06 — Evaluation harness

> **Stage:** 6 of 19 · **Estimate:** 2 days · **GPU time:** ~2 h
> **Precondition:** [P05](P05-training-harness.md) `PASS` (may be built in parallel with P05; must exist before P05 completes)
> **Gate:** held-out BPB reproducible to ±0.001 across runs.

---

## 1. Why this stage exists

This is the stage whose absence destroyed the previous programme. Across 564
commits and 37 waves, **held-out perplexity was never computed once**. Without a
project-level quality metric, every decision was made on proxies that could be
satisfied by editing markdown — see
[assessment §4, C3](../ASSESSMENT-2026-07-30.md#c3--no-held-out-loss-metric-fatal-to-feedback).

The rule this stage enforces: **if a change does not move BPB, it did not improve
the model, regardless of how good the samples look.**

**Laws at risk: R1** (BPB is primary), **R3** (retrieval and generation are never mixed).

---

## 2. The metric hierarchy

Strictly ordered. A lower tier may never override a higher one.

| Tier | Metric | Role | Frequency |
|---|---|---|---|
| **1** | **Held-out BPB** | The truth. Every stage reports it. | Every 250 steps |
| **2** | Per-domain BPB | Where competence lives (code / prose / docs / math) | Every checkpoint |
| **3** | Long-context BPB by position | Does context actually help? ([P10](P10-long-context-evaluation.md)) | Every checkpoint after [P09](P09-long-context-extension.md) |
| **4** | Zero-shot task accuracy | External comparability ([P17](P17-external-benchmarking.md)) | Milestones |
| **5** | Generation quality | Human-visible behaviour | Milestones |
| **6** | Latency and memory | Deployability ([P11](P11-throughput-engineering.md), [P12](P12-quantization-and-runtime.md)) | Milestones |

**Tier 5 may never be used to justify a Tier 1 regression.** That inversion —
good-looking demo outputs overriding an unmeasured loss — is precisely what the
lookup-table product did.

---

## 3. Bits per byte, defined once

\[
\text{BPB} = \frac{1}{B}\sum_{i=1}^{T} -\log_2 P(t_i \mid t_{<i})
\]

where \(T\) is the token count and \(B\) the **byte** length of the same text.

Implementation requirements — each of these is a way the number silently becomes
wrong:

| Requirement | Why |
|---|---|
| Compute in fp32, even when the model runs bf16 | bf16 accumulation over millions of tokens loses ~0.01 BPB |
| Use `logsumexp`, never `log(sum(exp(·)))` | Numerical stability |
| Count bytes of the **decoded** text, not `len(str)` | Multi-byte UTF-8 |
| Exclude special tokens from both numerator and denominator | They are not text |
| Use non-overlapping strided windows with a documented stride | Overlapping windows inflate the score |
| Report the number of documents and bytes alongside the score | A BPB without \(n\) is not a measurement |

Fix the eval stride at **half the context window** and state it in every report.
Changing the stride changes BPB by 1–3% and is a favourite accidental way to
manufacture progress.

---

## 4. Evaluation sets

Held out at [P02](P02-data-foundation.md), decontaminated, **never** trained on.

| Set | Size | Purpose |
|---|---:|---|
| `heldout-web` | 2 M tokens | Primary BPB, matches the training mixture |
| `heldout-code` | 1 M tokens | Code competence |
| `heldout-docs` | 1 M tokens | Technical documentation register |
| `heldout-wiki` | 1 M tokens | Factual prose |
| `heldout-math` | 0.5 M tokens | Formal notation |
| `heldout-long` | 200 documents ≥32k tokens | Long-context BPB ([P10](P10-long-context-evaluation.md)) |
| `heldout-fresh` | 0.5 M tokens, **published after the data cutoff** | Contamination canary |

`heldout-fresh` is the honest project's insurance. If BPB on `heldout-fresh` is
much worse than on `heldout-web`, the training data is contaminated with the eval
sets and every other number is inflated.

---

## 5. Steps

### 5.1 Core evaluator

```bash
npm run eval:bpb -- --model artifacts/models/n32-base.pt \
  --sets heldout-web,heldout-code,heldout-docs,heldout-wiki,heldout-math \
  --stride 1024 --out results/eval/bpb_<step>.json
```

Output must include, per set: BPB, token count, byte count, document count,
wall time, model hash, eval-set hash, stride, and a bootstrap 95% confidence
interval over documents.

**The confidence interval is required.** A 0.005 BPB difference between two
checkpoints is usually noise, and without an interval the project will chase it.

### 5.2 Task evaluation

```bash
npm run eval:bench -- --model artifacts/models/n32-base.pt --out results/eval/tasks.json
```

Realistic zero-shot suite for a 42M-parameter model — chosen because they produce
signal above chance at this scale:

| Task | Metric | Chance | Realistic target |
|---|---|---:|---:|
| LAMBADA | last-word accuracy | ~0% | 15–25% |
| HellaSwag | length-normalized acc | 25% | 27–31% |
| ARC-Easy | acc | 25% | 30–38% |
| PIQA | acc | 50% | 58–64% |
| WinoGrande | acc | 50% | 50–53% |
| BLiMP | grammatical acc | 50% | 65–75% |
| HumanEval | pass@1 | 0% | 0–2% |

**Be honest about the scale.** A 42M-parameter model will score near chance on
most reasoning benchmarks. That is expected and is not a failure — the objective
is competitive **BPB at size**, not benchmark parity with 7B models. Reporting
near-chance numbers plainly is what distinguishes this from the previous
programme, which selected metrics it could make green.

**BLiMP and LAMBADA are the informative ones at this scale** — they measure
language modelling rather than world knowledge, and they move with real progress.

### 5.3 Generation quality — measured, not admired

```bash
npm run eval:gen -- --model artifacts/models/n32-base.pt --n 200 --out results/eval/gen.json
```

Automatic, reproducible metrics only:

| Metric | Definition | Fail threshold |
|---|---|---|
| Distinct-2 / distinct-3 | Unique bigram/trigram ratio over 200 samples | <0.5 → repetitive |
| Repetition rate | Fraction of 4-grams repeated within a sample | >0.15 |
| **Degeneration rate** | Fraction of samples collapsing to a repeated token | **>0.01 → FAIL** |
| Self-BLEU | Diversity across samples | >0.4 → mode collapse |
| Mean sample length | Tokens before EOS | <20 → early stopping |

The degeneration check exists because the previous model's characteristic failure
was emitting `........`. **An automatic detector for the known failure mode is
mandatory**, so it can never again be discovered by reading samples by hand.

### 5.4 The regression harness

```bash
npm run eval:all -- --model <path> --baseline results/eval/baseline.json
```

Runs every tier, compares against a stored baseline, and **exits non-zero on any
BPB regression above the confidence interval**. Wire this into `npm run verify`
for model changes. Under **R7**, a regression stops the pipeline.

---

## 6. Deliverables

| Artifact | Path |
|---|---|
| BPB evaluator | `n32/eval/bpb.py` |
| Task evaluator | `n32/eval/tasks.py` |
| Generation metrics | `n32/eval/generation.py` |
| Regression harness | `n32/eval/regression.py` |
| Baseline snapshot | `results/eval/baseline.json` |
| Metric definitions | `docs/METRICS.md` |
| Public result | `docs/pipeline/results/P06.md` |

`docs/METRICS.md` defines every metric once, with its formula, and is the only
place a metric may be defined. The previous programme's `teacher_lp`,
`true_continue`, `L_eff`, and `content_ok` were each defined in several places
and drifted.

---

## 7. Gate

| Metric | Threshold |
|---|---|
| BPB reproducibility across runs | **±0.001** |
| BPB on a known reference model (e.g. GPT-2 small) | within **2%** of published values |
| Confidence intervals | reported for every BPB number |
| Degeneration detector | triggers correctly on a synthetic `........` sample |
| `eval:all` on an unchanged model | exits **0** |
| `eval:all` on a deliberately damaged model | exits **non-zero** |
| Total eval wall time | **<15 min** — anything slower will be skipped in practice |

The reference-model check is the calibration step: it proves the harness measures
what it claims. Without it, a systematic bug shifts every number equally and
stays invisible forever.

---

## 8. Failure modes

| Symptom | Cause | Action |
|---|---|---|
| BPB varies between runs | Non-deterministic batching or dropout left on | Fix seeds; call `model.eval()` |
| BPB suspiciously low (<1.0) | Eval data contaminated, or byte count wrong | Check `heldout-fresh`; verify UTF-8 byte counting |
| GPT-2 reference off by >5% | Stride or special-token handling differs | Match the published protocol exactly before trusting anything |
| Tasks all exactly at chance | Prompt formatting or answer scoring broken | Verify against a known-good model first |
| Eval takes >1 h | Batch size 1, or recomputing the cache | Batch documents; reuse the KV cache across strides |

---

## 9. Do not

- Do not report perplexity. It is not comparable across tokenizers.
- Do not evaluate on training data. Verify the split by document hash, not by trust.
- Do not use a single BPB number without \(n\) and a confidence interval.
- Do not let a good-looking sample override a BPB regression.
- Do not add a metric without adding it to `docs/METRICS.md`.
- Do not build metrics that cannot report bad news. Every metric here must be able to fail.

---

**Next:** [P07 — Scaling micro-laws](P07-scaling-microlaws.md)
