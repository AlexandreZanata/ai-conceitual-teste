# P10 — Long-context evaluation

> **Stage:** 10 of 19 · **Estimate:** 2 days · **GPU time:** ~4 h
> **Precondition:** [P09](P09-long-context-extension.md) `PASS`
> **Gate:** ≥90% needle retrieval at 32k across all depths, **and** a non-rising positional BPB curve.

---

## 1. Why this stage exists

"Supports 32k context" is the most commonly inflated claim in language modelling.
A model can accept 32,768 tokens of input and use none of them. The previous
programme had an equivalent failure: it reported `L_eff` values in the hundreds
of thousands while the model could not use context at all — a metric that could
only report good news.

This stage builds evaluation that **can fail**, and defines what the 32k claim
means before the claim is made.

**Law at risk: R3** — needle retrieval and predictive use of context are different capabilities and are always reported separately.

---

## 2. The three questions, which are genuinely different

| Question | Test | Failure meaning |
|---|---|---|
| Can it **find** information in long context? | Needle-in-a-haystack | Cannot retrieve |
| Can it **use** long context to predict better? | Positional BPB curve | Tolerates context without exploiting it |
| Can it **combine** information across long context? | Multi-hop / variable tracking | Retrieves but cannot reason over what it retrieved |

A model can pass 1 and fail 2 and 3 — that is the standard outcome of training on
randomly packed documents. **All three are reported. No aggregate score is
computed**, because averaging them hides exactly the failure that matters.

---

## 3. The test suite

### 3.1 Needle-in-a-haystack (retrieval)

Insert a synthetic fact into filler text; ask for it back.

| Dimension | Values |
|---|---|
| Context lengths | 1k, 2k, 4k, 8k, 16k, 24k, 32k |
| Needle depths | 0%, 10%, 25%, 50%, 75%, 90%, 100% |
| Needle types | numeric fact, named entity, code constant, rare token |
| Repeats per cell | 20 different needles |
| **Total** | 7 × 7 × 4 × 20 = **3,920 trials** |

Output a 7 × 7 accuracy heatmap. **Report the minimum cell, not the mean** — a
model that is 100% everywhere except 40% at depth 10% is a model with a specific,
important defect that the mean would hide.

The needle must be **information-theoretically absent** from the filler: use
randomly generated facts (`the calibration constant for unit QX-7734 is 82.19`),
never facts the model could know.

### 3.2 Positional BPB (predictive use)

Carried over from [P09](P09-long-context-extension.md) and re-run here with the
full held-out long set.

```bash
npm run eval:long -- --model artifacts/models/n32-32k.pt \
  --set heldout-long --buckets 1024 --out results/longctx/positional_bpb.json
```

Report BPB per 1,024-token bucket across 200 documents of ≥32k tokens.

**This is the honest metric.** Needle tests measure a narrow skill that can be
trained directly; positional BPB measures whether context genuinely improves
prediction and is very hard to game.

### 3.3 Context ablation (the control that matters)

For each document, compute BPB on the final 1,024 tokens with:

| Condition | Context given |
|---|---|
| C0 | 0 preceding tokens |
| C1 | 1,024 preceding tokens |
| C2 | 4,096 |
| C3 | 16,384 |
| C4 | 31,744 (full) |

\[
\text{context gain} = \text{BPB}(C0) - \text{BPB}(C4)
\]

**If the gain from C3 to C4 is under 0.01 BPB, the last 16k of context is
decorative** and the honest claim is 16k, not 32k. This single measurement is the
project's protection against overstating its headline feature.

### 3.4 Variable tracking (multi-hop)

Synthetic, scalable, and free of contamination:

```
x1 = 47
... 3,000 tokens of filler ...
x2 = x1 + 13
... 3,000 tokens of filler ...
x3 = x2 * 2
... 3,000 tokens of filler ...
What is x3?     -> 120
```

Sweep hop count 1–5 and inter-hop distance 1k–8k. Expect a 42M model to handle
1–2 hops and fail at 4+. **Report the failure honestly**; it is a real limit of
the scale, not of the effort.

### 3.5 RULER-style tasks (external comparability)

Implement the subset that is meaningful at this scale: multi-key needle,
multi-value needle, frequent-word extraction, and variable tracking. Skip QA
tasks requiring world knowledge — a 42M model will score at chance and the number
carries no information.

---

## 4. Steps

```bash
npm run eval:needle -- --model artifacts/models/n32-32k.pt \
  --lengths 1024,2048,4096,8192,16384,24576,32768 \
  --depths 0,10,25,50,75,90,100 --repeats 20 \
  --out results/longctx/needle.json

npm run eval:ablation -- --model artifacts/models/n32-32k.pt \
  --set heldout-long --out results/longctx/ablation.json

npm run eval:tracking -- --model artifacts/models/n32-32k.pt \
  --hops 1,2,3,4,5 --distances 1024,2048,4096,8192 \
  --out results/longctx/tracking.json
```

Then render `results/longctx/heatmap.svg` and write
`docs/pipeline/results/P10.md` containing **all** numbers, including the failures.

---

## 5. Deliverables

| Artifact | Path |
|---|---|
| Needle results + heatmap | `results/longctx/needle.json`, `heatmap.svg` |
| Positional BPB curve | `results/longctx/positional_bpb.json`, `.svg` |
| Context ablation | `results/longctx/ablation.json` |
| Variable tracking | `results/longctx/tracking.json` |
| Eval implementations | `n32/eval/longctx/*.py` |
| **Honest capability statement** | `docs/CONTEXT-CLAIM.md` |
| Public result | `docs/pipeline/results/P10.md` |

`docs/CONTEXT-CLAIM.md` states in one paragraph exactly what the model can and
cannot do with long context, with the numbers that support each sentence. It is
the text that may be copied into the README, the model card, and the paper —
**and no other long-context wording may be used anywhere in the project.** One
claim, one source, no drift.

---

## 6. Gate

| Metric | Threshold |
|---|---|
| Needle accuracy at 32k, **minimum over all depths** | **≥90%** |
| Needle accuracy at 8k, minimum over all depths | ≥95% |
| Positional BPB, 16k–32k bucket vs 4k–8k bucket | **non-increasing** |
| Context gain C0 → C4 | **≥0.15 BPB** |
| Context gain C3 → C4 (the last 16k) | **≥0.01 BPB** |
| Variable tracking, 1 hop @4k distance | ≥70% |
| All results committed, including failures | verified |

**If C3→C4 gain <0.01**, the gate fails and the honest claim is 16k. Change every
document in the project to say 16k. Do not ship a 32k claim the measurement does
not support.

---

## 7. Expected results

Predicted before running, so the stage can be wrong.

| Test | Prediction | If much worse |
|---|---|---|
| Needle @32k | 92–98% | Too few global layers → revisit [P08](P08-efficient-attention.md) E4 |
| Needle @depth 0% (very start) | Weakest cell, ~88% | Known "lost in the middle/start" effect; more global layers help |
| Positional BPB 16k–32k | ~1.32, flat | Rising → [P09](P09-long-context-extension.md) data was randomly packed |
| Context gain C0→C4 | 0.18–0.25 BPB | <0.10 → context is barely used |
| Tracking 1 hop | 75–85% | — |
| Tracking 3 hops | 30–45% | Expected weakness at 42M |
| Tracking 5 hops | ~10%, near chance | **Expected. Report it.** |

---

## 8. Failure modes

| Symptom | Cause | Action |
|---|---|---|
| Needle 100% everywhere, BPB curve rising | Retrieval learned, prediction not | Rebuild [P09](P09-long-context-extension.md) X2/X3 data with natural long documents |
| Needle fails only at depth 0% | Early context lost in SWA hops | Add a global layer near the input (layer 2) |
| Needle fails only at 32k | RoPE extension incomplete | Re-run the base sweep; try YaRN |
| Context gain ≈ 0 | Model ignores context entirely | Serious. Verify the eval feeds context correctly, then check [P09](P09-long-context-extension.md). |
| Tracking at chance for 1 hop | Arithmetic capability absent | Check digit tokenization from [P03](P03-tokenizer.md) |

---

## 9. Do not

- Do not average across depths. Report the minimum.
- Do not use needles the model could know from pretraining.
- Do not report a needle score without the positional BPB curve beside it.
- Do not aggregate the three questions into one "long-context score."
- Do not claim 32k if the measured context gain stops at 16k.
- Do not hide the multi-hop failures. They are the honest limit of a 42M model, and stating them is what makes the passing numbers believable.

---

**Next:** [P11 — Throughput engineering](P11-throughput-engineering.md)
