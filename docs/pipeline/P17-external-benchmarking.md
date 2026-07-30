# P17 — External benchmarking

> **Stage:** 17 of 19 · **Estimate:** 3 days · **GPU time:** ~8 h
> **Precondition:** [P16](P16-grounding-and-retrieval.md) `PASS`
> **Gate:** head-to-head numbers against named public baselines, measured on this machine.

---

## 1. Why this stage exists

Everything so far has been measured against the project's own baselines. That is
necessary but self-referential: a project can improve steadily against itself and
remain far behind the state of the art without ever noticing.

This stage answers the only question an outside reader will ask: **is this model
actually good, compared to what already exists?**

The answer may be no. That is an acceptable outcome and must be reported as
clearly as a yes.

**Law at risk: R2** — baseline numbers must be *measured here*, not copied from papers.

---

## 2. Baselines

Every baseline is run **on this machine, with this evaluation harness**. Copying
published numbers is not permitted: different tokenizers, strides, and prompt
formats make published figures incomparable, and using them is the easiest way to
manufacture a favourable result.

| Model | Params | Why this baseline |
|---|---:|---|
| **GPT-2 small** | 124 M | The canonical small-model reference; 3× our size |
| **Pythia-70M** | 70 M | Closest size, fully open training data |
| **Pythia-160M** | 160 M | 4× our size — the "10× larger" claim tests against this class |
| **SmolLM2-135M** | 135 M | Strong modern small model, well-trained |
| **TinyLlama-1.1B** | 1.1 B | 26× larger — establishes the gap to a real small LM |
| **Qwen3-0.6B** or current equivalent | 600 M | Modern architecture, long context |

### The comparison that matters

The claim from [`README.md`](README.md#1-the-objective-stated-so-it-can-be-falsified) is
**BPB competitive with models ~10× larger**. Concretely:

> `N32` (33.8M non-embedding) achieves BPB within **5%** of Pythia-160M
> (~150M non-embedding) on the same held-out data.

That is falsifiable, and it is the sentence the paper will live or die by.

**Also report the honest gap** to TinyLlama-1.1B. It will be large. Reporting it
prominently is what makes the favourable comparison credible.

---

## 3. Fair-comparison protocol

Comparing models with different tokenizers is where benchmark results quietly
become fiction. Enforce all of the following:

| Requirement | Reason |
|---|---|
| **BPB, never perplexity** | The only tokenizer-invariant likelihood metric |
| Identical held-out text | Same bytes, same documents, same order |
| Identical stride | Fixed at half the context; stated in the report |
| Each model at its own native context | Do not cripple a baseline by truncating it |
| Same hardware, same measurement code | Latency numbers are otherwise meaningless |
| Report parameters as **embedding / non-embedding / total** | **R4** — a model with a 150k vocabulary is not comparable on total params |
| Note training-token counts | We train on 4B; SmolLM2 trained on ~2T. **State this.** |

The training-token disclosure is essential to honesty. If `N32` matches a model
trained on 500× more data, that is an extraordinary claim requiring extraordinary
scrutiny — the most likely explanations are evaluation contamination or a
measurement bug, and both must be ruled out before the claim is made.

---

## 4. What to measure

### 4.1 Quality

| Benchmark | Metric | Note |
|---|---|---|
| Held-out BPB (web / code / docs / wiki / math) | BPB | **Primary** |
| `heldout-fresh` (post-cutoff) | BPB | Contamination canary |
| LAMBADA | accuracy | Informative at this scale |
| BLiMP | accuracy | Informative at this scale |
| HellaSwag, ARC-e, PIQA, WinoGrande | accuracy | Expect near chance; report anyway |

### 4.2 Long context — where the project should win

| Benchmark | Note |
|---|---|
| Needle-in-a-haystack at each model's max context | Most baselines cap at 2k–4k |
| Positional BPB curve | Direct comparison of context exploitation |
| RULER subset | External comparability |

**Most baselines of this size support 2,048 tokens.** A fair presentation shows
both: `N32` at 32k versus baselines at their maximum (a capability comparison),
**and** all models at 2,048 (a like-for-like quality comparison). Showing only
the first would be the kind of framing this project has committed to avoid.

### 4.3 Efficiency — the other place to win

| Metric | Measured on |
|---|---|
| Decode tok/s at 2k, batch 1 | RTX 4060 and CPU-only |
| Time to first token at 2k | both |
| Peak VRAM at 2k | both |
| Model size on disk, int8 | — |
| **BPB per MB** | a fair efficiency-frontier metric |
| **BPB per GPU-hour of training** | training efficiency |

The efficiency frontier is likely the strongest honest claim available:
*for a given memory budget or latency budget, `N32` is the best model.* That
framing is defensible even if absolute quality trails the larger baselines.

---

## 5. Steps

```bash
npm run eval:baselines -- --models gpt2,pythia-70m,pythia-160m,smollm2-135m,tinyllama-1.1b \
  --sets heldout-web,heldout-code,heldout-docs,heldout-fresh \
  --stride-frac 0.5 --out results/bench/baselines.json

npm run eval:frontier -- --results results/bench/ --out results/bench/frontier.svg
```

`frontier.svg` plots BPB against model size, BPB against decode latency, and BPB
against training FLOPs, with every model as a labelled point. **If `N32` is not
on the Pareto frontier of any of the three plots, the programme has not
succeeded**, and [P18](P18-release-and-publication.md) must say so.

---

## 6. Deliverables

| Artifact | Path |
|---|---|
| Baseline runner | `n32/eval/baselines.py` |
| All measurements | `results/bench/baselines.json` |
| Frontier plots | `results/bench/frontier.svg` |
| Comparison table | `results/bench/comparison.md` |
| **Honest gap statement** | `docs/COMPARISON.md` |
| Public result | `docs/pipeline/results/P17.md` |

`docs/COMPARISON.md` must contain a section titled **"Where N32 loses"**,
listing every benchmark where a baseline wins and by how much. A comparison
document without that section is not admissible.

---

## 7. Gate

| Metric | Threshold |
|---|---|
| Baselines measured on this machine | **≥5** |
| BPB vs Pythia-160M | **within 5%** |
| Any comparison using published rather than measured numbers | **0** |
| Params reported as embedding / non-embedding / total | all models |
| Training-token counts disclosed | all models |
| "Where N32 loses" section | present and complete |
| Pareto frontier position | on the frontier in **≥1** of size / latency / training-FLOPs |
| `heldout-fresh` BPB vs `heldout-web` | within **10%** (contamination check) |

**If the model is not within 5% of Pythia-160M**, the gate fails and the claim in
the objective must change to whatever is true. Do not weaken the gate; change the
claim and record why in `docs/pipeline/results/P17.md`.

---

## 8. Expected results

Stated in advance.

| Comparison | Prediction | Confidence |
|---|---|---|
| BPB vs Pythia-70M | `N32` **wins** by 3–8% | high — better data and tokenizer |
| BPB vs Pythia-160M | within 2–6% | medium — the headline claim |
| BPB vs SmolLM2-135M | `N32` **loses** by 5–15% | high — trained on ~500× more tokens |
| BPB vs TinyLlama-1.1B | `N32` **loses** by 20–30% | high — and this is fine |
| Needle @32k vs all | `N32` **wins** | high — baselines cap at 2k–4k |
| Decode tok/s | `N32` **wins** substantially | high |
| BPB per MB | `N32` **wins** | high |
| LAMBADA | `N32` loses to all >100M | high |

**The honest summary that these predictions imply:** *`N32` is the best model in
its size class for long-context, in-context tasks, and it is not competitive with
models trained on far more data on knowledge-intensive benchmarks.* If the
measurements support that sentence, the programme succeeded.

---

## 9. Do not

- Do not copy published numbers. Measure every baseline here.
- Do not compare perplexity across tokenizers.
- Do not truncate a baseline's context to make `N32` look better.
- Do not omit larger baselines because they win.
- Do not report a favourable result without checking `heldout-fresh` for contamination.
- Do not aggregate benchmarks into a single score. Report each.

---

**Next:** [P18 — Release and publication](P18-release-and-publication.md)
