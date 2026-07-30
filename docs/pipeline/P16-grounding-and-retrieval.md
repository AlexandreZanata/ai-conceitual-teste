# P16 — Grounding and retrieval

> **Stage:** 16 of 19 · **Estimate:** 3 days · **GPU time:** ~2 h
> **Precondition:** [P15](P15-instruction-and-behavior.md) `PASS`
> **Gate:** generation and retrieval contributions measured and reported separately, always.

---

## 1. Why this stage exists

A 42M-parameter model holds very little world knowledge. Retrieval is the correct
engineering answer — and it is also **the exact mechanism that destroyed the
previous programme's scientific integrity**, which reported retrieval hits as
model capability for 37 waves.

Retrieval is therefore reintroduced under one strict condition: **every answer is
attributed to a source — parametric memory or retrieved context — and the two are
never aggregated into a single score.**

**Law at risk: R3.** This stage exists to enforce it.

---

## 2. The contamination problem, stated plainly

Consider a system that retrieves a document and generates an answer from it.
Naively, its accuracy is one number. That number is scientifically useless,
because it cannot distinguish:

| Scenario | Accuracy | Reality |
|---|---:|---|
| Perfect retriever, model copies the span verbatim | 95% | The **retriever** works; the model is a copy function |
| Poor retriever, model answers from parametric memory | 60% | The **model** works; retrieval is dead weight |
| Both mediocre, errors happen to cancel | 70% | Nothing is understood |

All three look like "70–95% accuracy." The previous programme lived in row 1 and
reported it as row 2.

### The mandatory four-condition ablation

Every retrieval-augmented result is reported as **four numbers, never one**:

| Condition | Context provided | Measures |
|---|---|---|
| **A — closed book** | none | Parametric knowledge alone |
| **B — gold context** | the correct document, supplied | Model's ability to use context (ceiling) |
| **C — retrieved context** | whatever the retriever found | End-to-end system performance |
| **D — distractor context** | a plausible but wrong document | Robustness to bad retrieval |

From these:

\[
\text{retrieval contribution} = C - A, \qquad
\text{retrieval quality} = \frac{C - A}{B - A}, \qquad
\text{distractor robustness} = D - A
\]

**If D < A, retrieval is actively harmful** — the model is being misled by wrong
context, and the honest recommendation is to ship without retrieval. That
measurement is impossible to make without condition D, which is why it is
mandatory.

---

## 3. Design

The model's genuine advantage is a **32k context window**, so the retrieval
design should exploit it rather than work around it.

| Choice | Decision | Reason |
|---|---|---|
| Chunk size | 512 tokens | Small enough to be precise, large enough to be coherent |
| Chunks in context | up to **48** (~24k tokens) | Uses the 32k window as the feature it is |
| Retriever | BM25 first; embeddings only if BM25 is beaten | BM25 is a strong, zero-cost, zero-training baseline that is frequently skipped |
| Embedding model | If used, an external off-the-shelf model | **Do not** use `N32` as its own retriever — 42M is too small, and it entangles the two capabilities |
| Reranking | None initially | Adds a component before the baseline is understood |
| Attribution | Every answer cites the chunk IDs used | Enables per-answer auditing |

**Start with BM25.** Report the embedding retriever only if it beats BM25 on the
same four-condition ablation. A large fraction of published RAG gains disappear
against a properly tuned BM25 baseline, and this project has already paid the
price for skipping controls.

---

## 4. Steps

### 4.1 Build the index

```bash
npm run rag:index -- --corpus data/dedup/ --chunk-tokens 512 --overlap 64 \
  --retriever bm25 --out artifacts/rag/index_bm25/
```

Index the pretraining corpus, so retrieval and parametric knowledge cover the
same domain — otherwise condition A and condition C are not comparable.

### 4.2 Run the four-condition ablation

```bash
npm run eval:rag -- --model artifacts/models/n32-32k-instruct.pt \
  --index artifacts/rag/index_bm25/ \
  --conditions closed,gold,retrieved,distractor \
  --out results/rag/ablation.json
```

Every reported number carries its condition label. A number without a condition
label is not admissible in any document.

### 4.3 Measure the context-length benefit

The specific question this project is positioned to answer:

| Chunks in context | Tokens | Accuracy | Latency |
|---:|---:|---|---|
| 1 | 512 | | |
| 4 | 2,048 | | |
| 12 | 6,144 | | |
| 24 | 12,288 | | |
| **48** | **24,576** | | |

**This table is the project's headline result if it slopes upward.** It would
demonstrate that a small model with a large context beats a small model with a
small context on a real task — which is the thesis of the entire programme.

If accuracy plateaus at 12 chunks, say so. That would mean the 32k window is not
paying for itself on this task, and it is a finding worth publishing rather than
hiding.

### 4.4 Reuse the old bank — correctly

The 18-row `error_bank.jsonl` from the previous programme may be used **only** as
a fixture in condition B (gold context), clearly labelled as supplied context. It
may never appear on a serving path.

---

## 5. Deliverables

| Artifact | Path |
|---|---|
| Indexer and retriever | `n32/serve/rag.py` |
| Four-condition ablation | `results/rag/ablation.json` |
| Context-length scaling table | `results/rag/context_scaling.json` |
| Attribution audit (100 answers) | `results/rag/attribution.json` |
| Public result | `docs/pipeline/results/P16.md` |

---

## 6. Gate

| Metric | Threshold |
|---|---|
| All four conditions reported | **required** |
| Retrieval contribution (C − A) | **>0** and reported with a confidence interval |
| Distractor robustness (D − A) | **≥ −0.05** (retrieval must not be harmful) |
| BM25 baseline | reported before any embedding retriever |
| Attribution | 100% of answers cite the chunks used |
| Context-scaling table | complete, 1 → 48 chunks |
| Any answer served from a table | **0** |

---

## 7. Failure modes

| Symptom | Cause | Action |
|---|---|---|
| C ≈ B | The model copies spans rather than using them | Check whether answers are verbatim substrings; if >80% are, it is extraction, not comprehension — report it as such |
| D ≪ A | Distractors mislead the model | Add distractor-context examples to [P15](P15-instruction-and-behavior.md) SFT data |
| Accuracy flat past 4 chunks | Long context unused, or the retriever puts the answer first every time | Shuffle chunk order; re-check the [P10](P10-long-context-evaluation.md) positional curve |
| Embeddings lose to BM25 | Normal and common | Report it. Ship BM25. |
| Latency explodes at 48 chunks | Prefill cost | Use chunked prefill from [P11](P11-throughput-engineering.md); cache retrieved-chunk KV across queries |

---

## 8. Do not

- Do not report a single retrieval-augmented accuracy number.
- Do not omit condition D. Without it, harmful retrieval is invisible.
- Do not use `N32` as its own retriever.
- Do not put any lookup table on a serving path.
- Do not compare an embedding retriever against no baseline. BM25 is the baseline.
- Do not describe retrieval performance as model capability. **R3.**

---

**Next:** [P17 — External benchmarking](P17-external-benchmarking.md)
