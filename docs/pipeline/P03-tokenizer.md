# P03 — Tokenizer

> **Stage:** 3 of 19 · **Estimate:** 1 day · **GPU time:** none
> **Precondition:** [P02](P02-data-foundation.md) §3.3 complete (deduplicated text available)
> **Gate:** ≤3.6 bytes/token at `vocab_size = 16,384` on held-out data, lossless round-trip.

---

## 1. Why this stage exists

This is the **highest-leverage single change in the entire pipeline**, and it is
one day of work.

The previous model inherited GPT-2's 50,257-token vocabulary while using
`d_model = 64`. The result: **96% of parameters were the embedding table**, and
the actual transformer was 132K parameters — see
[assessment §2.4](../ASSESSMENT-2026-07-30.md#24-the-parameter-budget-was-spent-on-the-wrong-thing).

At `d_model = 512`, dropping to a 16,384-entry domain vocabulary costs 8.4M
embedding parameters instead of 25.7M, and frees the budget for **12 real
transformer layers**.

**Law at risk: R4** — from here on, every parameter count is reported as embedding vs non-embedding.

---

## 2. The vocabulary-size trade-off

| `vocab_size` | Embed params @512 | Bytes/token (est.) | Tokens for 14 GB text | Effect |
|---:|---:|---:|---:|---|
| 8,192 | 4.2 M | ~3.1 | 4.5 B | Cheapest embeddings, longest sequences — more compute per byte |
| **16,384** | **8.4 M** | **~3.5** | **4.0 B** | **Chosen.** Balanced. |
| 32,768 | 16.8 M | ~3.8 | 3.7 B | Embeddings start crowding out depth |
| 50,257 | 25.7 M | ~4.0 | 3.5 B | 61% of a 42M budget spent on lookup |

The tension: a **larger** vocabulary means fewer tokens for the same text (less
compute per byte, longer effective context in characters), but **more** parameters
spent on embeddings and a harder softmax at small `d_model`.

At 32k context, vocabulary size also sets the **character reach** of the context
window. At 3.5 bytes/token, 32,768 tokens ≈ **115 KB of text** ≈ a 30,000-word
document. Report this number; it is what a user actually cares about.

---

## 3. Steps

### 3.1 Sample the training text

```bash
python n32/tokenizer/sample.py --in data/dedup/ --out data/tok_sample.txt \
  --bytes 2e9 --stratify-by-source
```

**Stratification is required.** The sample must match the [P02](P02-data-foundation.md#2-target-corpus)
mixture proportions. A tokenizer trained on 80% prose will fragment code badly,
and code fragmentation is expensive: a model that spends 3 tokens on `    ` (four
spaces) wastes a large fraction of its context on Python indentation.

### 3.2 Train byte-level BPE

```bash
npm run tok:train -- --input data/tok_sample.txt --vocab-size 16384 \
  --out artifacts/tokenizer/n32-16k.json
```

Required configuration:

| Setting | Value | Reason |
|---|---|---|
| Algorithm | Byte-level BPE | Never produces `<unk>`; every byte sequence is representable |
| Initial alphabet | all 256 bytes | Guarantees lossless round-trip |
| Pre-tokenizer | GPT-4-style regex split | Keeps digits and whitespace runs sane |
| **Digit handling** | split every digit individually | Arithmetic degrades badly with merged multi-digit tokens |
| **Whitespace** | dedicated tokens for runs of 2, 4, 8, 16 spaces | Critical for Python; saves ~8% of code tokens |
| Byte fallback | enabled | Handles arbitrary binary and rare Unicode |
| Special tokens | `<|endoftext|>`, `<|pad|>`, `<|user|>`, `<|assistant|>`, `<|tool|>` | Reserve **now**; adding them at [P15](P15-instruction-and-behavior.md) would resize embeddings mid-programme |

Reserve IDs 0–255 for raw bytes and 256–271 for specials, so the special-token
block can grow without invalidating checkpoints.

### 3.3 Evaluate on held-out data

```bash
npm run tok:eval -- --tokenizer artifacts/tokenizer/n32-16k.json \
  --heldout data/heldout_text/ --out results/tokenizer/eval.json
```

Report **per source**, not just in aggregate:

| Metric | Definition | Target |
|---|---|---|
| Bytes per token | total bytes ÷ total tokens | ≥3.4 overall |
| Compression vs GPT-2 | ratio of token counts on identical text | ≥0.95 |
| Round-trip fidelity | `decode(encode(x)) == x` byte-exact | **100%** |
| Continued-word rate | fraction of tokens continuing a word | 0.3–0.5 |
| Code indentation cost | tokens for 4 leading spaces | **1** |
| Digit tokenization | `12345` | **5 tokens** |
| Unused vocabulary entries | merges never seen on held-out | <2% |

### 3.4 Sweep before committing

Train **three** tokenizers — 8,192 / 16,384 / 32,768 — and record all three in
`results/tokenizer/sweep.json`. The cost is a few CPU-hours and it converts the
single most consequential design choice from an assumption into a measurement.

Choose using **total training cost at equal BPB**, not bytes/token alone:

\[
\text{cost} \propto \underbrace{6 N_{\text{total}}(V)}_{\text{per token}} \times \underbrace{\frac{B_{\text{corpus}}}{\text{bytes/token}(V)}}_{\text{token count}}
\]

Smaller vocabularies reduce \(N\) but increase token count. The minimum is
usually flat between 8k and 32k — if the sweep says otherwise, follow the sweep
and record why in `docs/pipeline/results/P03.md`.

---

## 4. Bits per byte — the metric that makes this comparable

Perplexity is **not comparable across tokenizers**: a model with a larger
vocabulary predicts fewer, harder tokens and can show lower perplexity while
being a worse model. This is exactly the trap that lets a tokenizer change look
like a modelling win.

Use **bits per byte**:

\[
\text{BPB} = \frac{\sum_i -\log_2 P(t_i)}{\sum_i \text{bytes}(t_i)}
\]

BPB measures compression of the underlying **bytes** and is invariant to
tokenization. It is the project's primary metric under **R1**, and it is
established here because [P06](P06-evaluation-harness.md) depends on it.

**Reference points** (held-out web text, for orientation):

| BPB | Interpretation |
|---:|---|
| ~1.20 | Strong 1B-parameter model |
| ~1.00 | Strong 7B-parameter model |
| ~0.80 | Frontier-scale |
| **≤1.35** | **`N32-base` success target** — competitive with models ~10× larger |

---

## 5. Deliverables

| Artifact | Path |
|---|---|
| Tokenizer | `artifacts/tokenizer/n32-16k.json` |
| Sweep results (3 sizes) | `results/tokenizer/sweep.json` |
| Held-out evaluation | `results/tokenizer/eval.json` |
| BPB reference implementation | `n32/eval/bpb.py` |
| Public result | `docs/pipeline/results/P03.md` |

---

## 6. Gate

| Metric | Threshold |
|---|---|
| Bytes/token on held-out | **≥3.4** |
| Round-trip fidelity | **100%**, byte-exact, on 1 GB of held-out data |
| 4-space indent | **1 token** |
| Multi-digit numbers | split per digit |
| Vocabulary size | exactly **16,384** (or the sweep-justified alternative) |
| Sweep artifact | present, all three sizes |
| Special tokens | reserved, IDs frozen and documented |

---

## 7. Failure modes

| Symptom | Cause | Action |
|---|---|---|
| Bytes/token <3.0 | Sample too small or too narrow | Increase to 2 GB; verify stratification |
| Round-trip fails on any byte | Byte fallback disabled | Non-negotiable — fix and re-train |
| 4-space indent costs >1 token | Whitespace tokens missing | Add explicit whitespace-run tokens |
| Numbers merge into `12345` | Digit splitting off | Enable it; arithmetic depends on it |
| Vocabulary full of URL fragments | Web boilerplate dominates | Strengthen [P02](P02-data-foundation.md) quality filters, re-sample |

---

## 8. Do not

- Do not reuse GPT-2's 50,257 vocabulary. That choice is the direct cause of the previous failure.
- Do not train the tokenizer on unfiltered or unstratified data.
- Do not change the vocabulary after [P05](P05-training-harness.md) begins. It invalidates every checkpoint and every BPB number.
- Do not report perplexity anywhere. Report BPB.
- Do not skip the sweep to save a day. This is the cheapest decision-quality purchase in the pipeline.

---

**Next:** [P04 — Baseline architecture](P04-baseline-architecture.md)
