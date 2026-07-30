# P15 — Instruction and behaviour

> **Stage:** 15 of 19 · **Estimate:** 4 days · **GPU time:** ~6 h
> **Precondition:** [P12](P12-quantization-and-runtime.md) `PASS`
> **Gate:** measured instruction-following gain with **no** BPB regression.

---

## 1. Why this stage exists

A base language model completes text; it does not follow instructions. This stage
adds that behaviour — and it is the stage where the previous programme went
wrong, by replacing a broken generator with a lookup table and calling the result
a product.

The rule here is absolute: **the model generates the answer, or it abstains.** No
answer is ever served from a table. Retrieval is a separate, separately measured
capability, and it lives in [P16](P16-grounding-and-retrieval.md).

**Laws at risk: R3** (never mix retrieval into generation), **R1** (instruction tuning must not cost base quality).

---

## 2. Realistic expectations at 42M parameters

Set these before starting, so the results are not a disappointment measured
against a fantasy.

| Capability | 42M model | Honest description |
|---|---|---|
| Continue text in-domain | **Good** | The model's actual strength |
| Follow simple format instructions | **Fair** | "List three…", "Answer yes or no" |
| Short factual QA from context | **Fair** | With the context supplied |
| Short factual QA from memory | **Poor** | 42M parameters store very little world knowledge |
| Multi-step reasoning | **Poor** | Expect failure; do not train it away |
| Code generation | **Very poor** | Perhaps single-line completions |
| Open-ended chat | **Not a goal** | Do not claim it |

**The honest product framing:** a fast, tiny model for **in-context tasks over
long documents** — summarize, extract, continue, answer-from-context. Not an
assistant. Not a chatbot. The 32k context is the feature; parametric knowledge is
not.

Fixing this framing now prevents the failure of the previous programme, which
kept the vocabulary of a general assistant long after the evidence said otherwise.

---

## 3. Data

**Target: 500M tokens of instruction data**, which is ~12% of pretraining — a
sizeable share, because format-following must be learned thoroughly at this scale.

| Source | Share | Why |
|---|---:|---|
| **Context-grounded QA** (question + document + answer) | 40% | The core use case; matches the 32k strength |
| **Summarization** (long document → summary) | 20% | Directly exercises long context |
| **Extraction** (document → structured fields) | 15% | High value, low capability requirement |
| **Format-following** (short, explicit instructions) | 15% | Cheap and effective at small scale |
| **Refusal / abstention** | 10% | See §4 |

Prefer **synthetic data generated from the pretraining corpus**: take a document,
generate a question whose answer is in it, and train on `(instruction, document,
answer)`. This keeps the distribution close to pretraining, makes long-context
examples abundant, and avoids licensing complications. It is also the only way to
get 500M tokens of 32k-context instruction data on this budget.

### Format

Use the special tokens reserved at [P03](P03-tokenizer.md):

```
<|user|>Summarize the following document in three sentences.

{document}<|assistant|>{summary}<|endoftext|>
```

**Loss is computed only on the assistant span.** Training on the instruction and
document tokens teaches the model to generate questions, which is not the task.

---

## 4. Abstention, done the right way this time

The previous programme's abstention was **~1,900 lines of hand-coded string
traps** in `semwrap_ops.py`, and it over-refused so heavily that correct answers
were rejected. That is a rules engine, not a model capability.

Here, abstention is **learned and calibrated**:

| Requirement | Method |
|---|---|
| Learned, not hand-coded | 10% of instruction data is unanswerable questions with an abstention target |
| Calibrated | Abstention probability correlates with actual error rate |
| **Measured in both directions** | Over-refusal is a failure exactly as much as hallucination is |
| Architecture-native signal | Optionally use purity from [Q10](P13-quantum-inspired-training-lab.md#q10--density-matrix-attention-with-purity-based-abstention) |

### The abstention scorecard

| | Model answers | Model abstains |
|---|---|---|
| **Answer is in context** | ✅ correct / ❌ wrong answer | ❌ **over-refusal** |
| **Answer is not in context** | ❌ hallucination | ✅ correct abstention |

**All four cells are reported.** The previous programme reported only the bottom
right and called it a trust win. A model that abstains on everything scores
perfectly on hallucination and is useless — which is precisely what happened.

Primary metric: **AUROC of the abstention signal against actual correctness**.
That single number cannot be gamed by refusing more or less often.

---

## 5. Steps

### 5.1 Generate the data

```bash
npm run data:instruct -- --corpus data/dedup/ --n-tokens 5e8 \
  --mix qa:0.4,summary:0.2,extract:0.15,format:0.15,abstain:0.1 \
  --max-ctx 32768 --out data/instruct/
```

Hold out 5,000 examples per category, **never** trained on.

### 5.2 Fine-tune

```bash
npm run train:sft -- --from artifacts/models/n32-32k.pt \
  --data data/instruct/ --tokens 5e8 --lr 2e-5 --ctx 32768 \
  --out runs/n32-sft
```

| Setting | Value | Reason |
|---|---|---|
| LR | 2e-5 | ~3% of pretraining peak; higher erases base capability |
| Epochs | 1 | Repetition causes memorization and format overfitting |
| Loss mask | assistant span only | §3 |
| Context | 32,768 | Must exercise the full window, or SFT will shrink the usable context |

### 5.3 Verify the base model survived

```bash
npm run eval:all -- --model runs/n32-sft/final.pt --baseline results/eval/baseline.json
npm run eval:long -- --model runs/n32-sft/final.pt --set heldout-long
```

**The alignment-tax check.** Instruction tuning routinely costs base quality; at
42M parameters, where there is little slack, it can be severe. If BPB regresses
more than 2%, lower the LR or reduce the instruction-data share. Under **R7** a
regression stops the stage.

### 5.4 Measure instruction-following

| Metric | Definition | Target |
|---|---|---|
| Format compliance | Output matches the requested structure | ≥80% |
| Context-QA exact match | Answer is a correct span from the document | ≥45% |
| Summarization ROUGE-L | vs reference summaries | ≥0.25 |
| Extraction F1 | Structured field extraction | ≥0.55 |
| **Abstention AUROC** | Abstention signal vs correctness | **≥0.70** |
| Over-refusal rate | Abstains when the answer *is* present | **≤10%** |
| Hallucination rate | Answers when the answer is absent | ≤20% |

These targets are calibrated to 42M parameters. They are modest by design, and
meeting them honestly is worth more than exceeding an inflated target by
measuring something easier.

---

## 6. Deliverables

| Artifact | Path |
|---|---|
| Instruction data generator | `n32/data/instruct.py` |
| SFT loop | `n32/train/sft.py` |
| Instruction model | `artifacts/models/n32-32k-instruct.pt` |
| Instruction evaluation | `results/instruct/eval.json` |
| Abstention scorecard, all four cells | `results/instruct/abstention.json` |
| Alignment-tax report | `results/instruct/alignment_tax.json` |
| **Capability statement** | `docs/CAPABILITY-CLAIM.md` |
| Public result | `docs/pipeline/results/P15.md` |

`docs/CAPABILITY-CLAIM.md` — like [`docs/CONTEXT-CLAIM.md`](P10-long-context-evaluation.md#5-deliverables),
this is the **single source** for what the model can do. Every README, model card,
and paper copies from it. One claim, one source, no drift.

---

## 7. Gate

| Metric | Threshold |
|---|---|
| BPB regression vs base | **≤2%** |
| Long-context needle regression | **≤3 points** |
| Format compliance | **≥80%** |
| Context-QA exact match | **≥45%** |
| Abstention AUROC | **≥0.70** |
| Over-refusal rate | **≤10%** |
| All four abstention cells reported | required |
| Zero lookup-table answers on any path | **verified by code review** |

The last row is checked by inspection, not by test: **no dictionary of
question → answer may exist anywhere in the serving path.** That mechanism is
what turned the previous programme's research into a demo.

---

## 8. Failure modes

| Symptom | Cause | Action |
|---|---|---|
| BPB regresses >5% | LR too high | Drop to 1e-5; reduce instruction share to 8% |
| Model abstains on everything | Abstention data over-weighted, or the signal is miscalibrated | Reduce to 5%; check the over-refusal cell |
| Format compliance <50% | Too little format data, or special tokens not learned | Raise the format share; verify the tokens were reserved at [P03](P03-tokenizer.md) |
| Long context degrades after SFT | SFT ran at short context | Re-run at 32,768; this is the most common long-context regression |
| Answers memorized from SFT data | Multiple epochs | One epoch only |
| Good demos, bad metrics | Cherry-picking | The metrics are correct. Believe them. |

---

## 9. Do not

- Do not serve any answer from a lookup table.
- Do not hand-code abstention rules. It must be learned and calibrated.
- Do not report abstention without the over-refusal rate beside it.
- Do not train more than one epoch.
- Do not claim chat, assistant, or general-purpose capability.
- Do not accept a BPB regression in exchange for better demos.

---

**Next:** [P16 — Grounding and retrieval](P16-grounding-and-retrieval.md)
