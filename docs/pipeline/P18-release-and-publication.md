# P18 — Release and publication

> **Stage:** 18 of 19 · **Estimate:** 5 days · **GPU time:** ~4 h (reproduction check)
> **Precondition:** [P17](P17-external-benchmarking.md) `PASS`
> **Gate:** an independent party reproduces the headline numbers from a clean clone.

---

## 1. Why this stage exists

The previous programme produced 573 wave reports, a paper, and 251 formal
documents citing `results/nano-lm/formal-*/formal.json` — **none of which
exist**. See [assessment §2.7](../ASSESSMENT-2026-07-30.md#27-evidence-integrity).

Reproducibility is not a publication formality. It is the only thing that
distinguishes a result from an assertion, and its absence is why the previous
work cannot be salvaged even where the numbers may have been correct.

**Law at risk: R2**, in its final and strictest form.

---

## 2. The reproduction test

The gate is behavioural, not documentary:

> A person (or agent) with this hardware, a clean clone, and no other context
> follows `REPRODUCE.md` and obtains the headline BPB within **1%**.

Verify it by actually doing it:

1. `git clone` into a fresh directory.
2. Follow `REPRODUCE.md` **exactly as written**, changing nothing.
3. Record every point where the instructions are wrong, incomplete, or ambiguous.
4. Fix them.
5. Repeat until a clean pass.

Most projects fail this on the first attempt at step 2, usually within the first
three commands. Budget for three iterations.

Full retraining takes ~39 GPU-hours, so `REPRODUCE.md` offers two tiers:

| Tier | Cost | Verifies |
|---|---|---|
| **Fast** | ~1 h | Download the released checkpoint, reproduce every evaluation number |
| **Full** | ~40 h | Rebuild the data, retrain, reproduce everything from scratch |

The fast tier must be genuinely fast and must work, because it is the only one
almost anyone will run.

---

## 3. Release artifacts

| Artifact | Contents | Where |
|---|---|---|
| **Model weights** | bf16, int8, GGUF | HuggingFace Hub |
| **Tokenizer** | `n32-16k.json` | with the model |
| **Model card** | §4 | with the model |
| **Data manifest** | Sources, licences, SHA-256, processing scripts | repository |
| **Training config** | Exact YAML plus git hash | repository |
| **Evaluation results** | Every JSON from every stage | repository |
| **`REPRODUCE.md`** | Both tiers, step by step | repository root |
| **Paper** | §5 | `paper/` and arXiv |

**Do not release the training data itself** — it is 14 GB of third-party text.
Release the manifest and the scripts that rebuild it byte-for-byte from the
recorded SHA-256 hashes.

---

## 4. The model card

Written from the three claim documents produced earlier, so no new wording is
invented at release time:

- [`docs/CONTEXT-CLAIM.md`](P10-long-context-evaluation.md#5-deliverables) ([P10](P10-long-context-evaluation.md))
- [`docs/CAPABILITY-CLAIM.md`](P15-instruction-and-behavior.md#6-deliverables) ([P15](P15-instruction-and-behavior.md))
- [`docs/COMPARISON.md`](P17-external-benchmarking.md#6-deliverables) ([P17](P17-external-benchmarking.md))

Required sections:

| Section | Requirement |
|---|---|
| Intended use | Long-context in-context tasks. **Explicitly not** a chatbot or knowledge base. |
| Parameters | Embedding / non-embedding / total, separately — **R4** |
| Training data | Sources, token count, licences, cutoff date |
| Training compute | GPU-hours, hardware, total FLOPs |
| Evaluation | Every number from [P17](P17-external-benchmarking.md), including losses |
| **Limitations** | §4.1 |
| Contamination | Decontamination method and `heldout-fresh` result |
| Environmental cost | ~39 GPU-hours on a 45 W laptop GPU ≈ 1.8 kWh |

### 4.1 The limitations section, written honestly

Draft it now so it is not softened under release pressure:

> `N32` has 33.8M non-embedding parameters and was trained on 4B tokens. It
> stores very little world knowledge and scores at or near chance on
> knowledge-intensive benchmarks. It cannot perform multi-step reasoning
> reliably; measured variable-tracking accuracy falls to near chance at 4 hops.
> It generates code poorly. It is not a chat assistant and has not been
> safety-tuned for open-ended dialogue. Its strengths are narrow and specific:
> long-context retrieval, extraction, and summarization over supplied documents,
> at very low memory and latency cost.

**If any of those sentences turns out to be false in the model's favour, correct
it.** But do not remove sentences because they are unflattering — that section is
what makes the rest of the card credible.

---

## 5. The paper

Two papers are available from this work. Both are honest; the first is more
interesting.

### 5.1 Primary — the methodology paper

> **"Thirty-seven waves, zero model improvement: metric selection failure in
> agent-driven research"**

A case study of what this repository did between waves W and BH: a documented
account of an agentic research programme that generated 341,926 lines of code,
856 orchestration scripts, and 573 reports while never measuring held-out
perplexity, and of the specific mechanisms — proxy metrics, retrieval masking a
broken generator, process throughput mistaken for progress — that made this
possible.

This is a **genuinely valuable and unusual paper.** Very few groups publish
their own process failures with full artifacts, and as AI agents take on more
autonomous research, the failure modes documented here become directly relevant
to a growing audience. The evidence base already exists in
[`docs/ASSESSMENT-2026-07-30.md`](../ASSESSMENT-2026-07-30.md) and the quarantined
deleted wave archive, recoverable via the git tag `legacy/waves-w-bh` ([P01](P01-ground-truth-reset.md)).

### 5.2 Secondary — the model paper

> **"N32: a 34M-parameter 32k-context language model trained on one laptop"**

Contributions, in order of strength:

1. A hybrid SWA/global + GQA design giving 32k context in **38.7 MB** of KV cache
2. A full recipe — data, tokenizer, training, extension — reproducible in **~39 GPU-hours on consumer hardware**
3. Measured scaling micro-laws in the 12M–80M regime on a single-GPU budget ([P07](P07-scaling-microlaws.md))
4. Negative results from [P13](P13-quantum-inspired-training-lab.md) and [P14](P14-theoretical-model-triage.md), with controls

Contribution 2 is the most useful to readers: **a complete, honest recipe for
training a real long-context model on hardware people actually own.**

### 5.3 Publication rules

| Rule | Reason |
|---|---|
| Every number in the paper traces to a committed JSON | The 251-missing-artifacts failure must not repeat |
| Every table has a generating script | Tables are built, not typed |
| Negative results appear in the main body, not an appendix | They are results |
| The limitations section is written before the abstract | Prevents claim inflation |
| No claim appears in the paper that is absent from the model card | Prevents drift |

---

## 6. Deliverables

| Artifact | Path |
|---|---|
| Reproduction guide | `REPRODUCE.md` |
| Model card | `MODEL-CARD.md` |
| Release checklist | `docs/RELEASE-CHECKLIST.md` |
| Table generators | `paper/tables/*.py` |
| Papers | `paper/methodology.tex`, `paper/n32.tex` |
| Reproduction log | `results/release/reproduction.json` |
| Public result | `docs/pipeline/results/P18.md` |

---

## 7. Gate

| Metric | Threshold |
|---|---|
| Clean-clone reproduction, fast tier | headline BPB within **1%** |
| Paper numbers traceable to committed JSON | **100%** |
| Tables generated by script | **100%** |
| Model card limitations section | present, honest, specific |
| Data manifest reproduces byte-identical corpus | verified by SHA-256 |
| Broken links or missing artifacts | **0** |
| `heldout-fresh` contamination check | published |
| Every stage has a file in `docs/pipeline/results/` | **19 of 19** |

---

## 8. Failure modes

| Symptom | Cause | Action |
|---|---|---|
| Reproduction differs by >1% | Non-determinism, or an unrecorded config | Pin every seed; diff the configs; find it before publishing |
| A paper number has no artifact | It was typed from memory | Regenerate it or delete it. **No exceptions** — this is the precise failure being corrected. |
| `REPRODUCE.md` fails at step 3 | Written from memory, not tested | Test it on a clean clone. Every time. |
| Reviewers question the training-token count | The claim looks too good | Publish the contamination analysis proactively |
| Tempted to drop a losing benchmark | Presentation pressure | Keep it. The losses are what make the wins believable. |

---

## 9. Do not

- Do not publish a number without its artifact.
- Do not write `REPRODUCE.md` without executing it on a clean clone.
- Do not soften the limitations section.
- Do not omit the methodology paper. It is the most original output of this work.
- Do not release the model without the model card.
- Do not claim capabilities that [P15](P15-instruction-and-behavior.md) and [P17](P17-external-benchmarking.md) did not measure.

---

**Next:** [P19 — Agent operating protocol](P19-agent-operating-protocol.md)
