# P02 — Data foundation

> **Stage:** 2 of 19 · **Estimate:** 3 days (mostly download and CPU time) · **GPU time:** none
> **Precondition:** [P01](P01-ground-truth-reset.md) `PASS`
> **Gate:** ≥4B deduplicated, licence-clean tokens on disk with a reproducible manifest.

---

## 1. Why this stage exists

This is **the** cause of the previous failure. The old model was trained on
TinyStories — children's fiction — and saw on the order of **10⁵ token-positions**.
The curated corpus that was supposed to give it knowledge is **1.24 MB across 4
files**, and the model was never trained on it at all.

A 42M-parameter model needs **10⁹–10¹⁰ tokens** to be worth anything. Everything
downstream is bounded by this stage. **If you do only one stage properly, do this one.**

**Laws at risk: R5** (this stage is expensive and unglamorous — it is the real work), **R2** (every corpus statistic must be a committed artifact).

---

## 2. Target corpus

**4.0 B tokens** after deduplication and filtering. Mixture chosen for a model
whose intended competence is technical text and code.

| Source | Share | Tokens | Why | Licence |
|---|---:|---:|---|---|
| **FineWeb-Edu** (sample-10BT subset) | 40% | 1.6 B | Highest-quality general web text available openly; the strongest single lever on small-model quality | ODC-By 1.0 |
| **The Stack v2 / StarCoder data** (permissive subset) | 25% | 1.0 B | Code competence; permissive licences only | per-file, permissive only |
| **Cosmopedia v2** | 15% | 0.6 B | Synthetic textbook prose — punches far above its weight at small scale | Apache 2.0 |
| **Wikipedia** (EN, current dump) | 10% | 0.4 B | Factual grounding, clean structure | CC BY-SA 3.0 |
| **Technical documentation** | 7% | 0.28 B | Python docs, Rust book, RFCs, MDN — extends the existing 22 curated sources | mixed, attribute |
| **arXiv abstracts + intros** (cs.*) | 3% | 0.12 B | Formal register, mathematical notation | arXiv non-exclusive |

**Raw text on disk:** ~14 GB. **Tokenized `uint16`:** ~8 GB. Against 214 GB free, this is comfortable — hold both.

### Why this mixture

Small models are **quality-starved, not quantity-starved**. The FineWeb-Edu and
Cosmopedia results are the clearest recent evidence that aggressive educational
filtering beats raw volume at the <1B-parameter scale. Do not substitute
unfiltered CommonCrawl to hit the token count faster; it will cost more BPB than
the extra tokens gain.

---

## 3. Steps

### 3.1 Extend the source registry

`n32/data/sources.py`, seeded from the surviving `curated_sources.py`. Each entry
must carry: `id`, `url`, `licence`, `sha256`, `expected_bytes`, `attribution_required`.

**Reject any source whose licence is unknown.** Record every rejection in
`docs/DATA-PROVENANCE.md` — legal defensibility is not optional and cannot be
retrofitted at [P18](P18-release-and-publication.md).

```bash
npm run data:fetch -- --manifest n32/data/sources.py --out data/raw/
```

Downloads must be resumable, checksummed, and rate-limited. 14 GB over a laptop
connection will take hours; make it restartable.

### 3.2 Clean

`n32/data/clean.py`, applied in this order:

| Filter | Rule | Drops |
|---|---|---|
| Encoding | Valid UTF-8; strip control chars except `\n\t` | ~0.1% |
| Language | fastText `lid.176` ≥0.65 for English (code exempt) | ~5% |
| Length | Documents <200 or >1M chars | ~3% |
| Quality heuristics | Gopher rules: mean word length 3–10; ≤10% symbol-to-word; ≥80% lines ending in punctuation (prose only) | ~10% |
| Repetition | Drop if top 2-gram >20% of content, or any line repeats >30% | ~2% |
| PII | Redact emails, phone numbers, API-key patterns, private IPs | in place |
| Benchmark decontamination | **13-gram overlap** against every eval set from [P06](P06-evaluation-harness.md), [P17](P17-external-benchmarking.md) | ~0.1% |

**Decontamination is mandatory and irreversible if skipped.** Contaminated
pretraining silently invalidates every benchmark number the project will ever
produce, and it cannot be detected after the fact. Run it before tokenization,
and record the eval-set hashes it was run against.

### 3.3 Deduplicate

Two passes, cheap then expensive:

1. **Exact** — SHA-256 over normalized text, removes 15–30% of web data.
2. **Near-duplicate** — MinHash LSH, 128 permutations, 5-grams, **Jaccard threshold 0.8**, banding `(b=16, r=8)`.

```bash
npm run data:dedup -- --in data/clean/ --out data/dedup/ --threshold 0.8
```

Memory discipline: with ~10 GB RAM, process in shards of ≤500 MB and keep only
MinHash signatures resident (128 × 4 bytes per document). Do not load the corpus.

### 3.4 Tokenize and shard

Runs **after** [P03](P03-tokenizer.md) trains the tokenizer. The dependency is
circular by design — train the tokenizer on a 2 GB sample from `data/dedup/`,
then return here to tokenize the whole corpus.

```bash
npm run data:tokenize -- --in data/dedup/ --tokenizer artifacts/tokenizer/n32-16k.json \
  --out data/tokens/ --shard-tokens 100000000 --dtype uint16
```

- `uint16` is valid only while `vocab_size ≤ 65,536`. Assert this at write time.
- 100M-token shards → ~40 shards of 200 MB. Sized for the page cache.
- Append `<|endoftext|>` between documents; do **not** allow documents to bleed across the separator during packing.
- Hold out **10M tokens** as a strict eval split, selected **by source document** rather than by token offset, so no document straddles the boundary.

### 3.5 Publish statistics

```bash
npm run data:stats -- --in data/tokens/ --out results/data/corpus_stats.json
```

Must report: token count per source, bytes per token per source, document count,
duplicate rate at each pass, length histogram, top-1000 token frequency, and the
decontamination hit count.

---

## 4. Deliverables

| Artifact | Path |
|---|---|
| Source manifest with licences | `n32/data/sources.py` |
| Provenance and rejections | `docs/DATA-PROVENANCE.md` |
| Deduplicated text | `data/dedup/` (gitignored) |
| Token shards | `data/tokens/*.bin` (gitignored) |
| Held-out eval split | `data/tokens/heldout.bin` |
| Corpus statistics | `results/data/corpus_stats.json` |
| Public result | `docs/pipeline/results/P02.md` |

---

## 5. Gate

| Metric | Threshold |
|---|---|
| Total tokens after dedup | **≥4.0 × 10⁹** |
| Exact-duplicate rate in output | **<0.1%** |
| Near-duplicate rate (Jaccard >0.8) on a 100k sample | **<2%** |
| Sources with unknown licence | **0** |
| 13-gram contamination against eval sets | **<0.01%** |
| Held-out split | ≥10M tokens, **zero** document overlap with train |
| Manifest reproducibility | re-running `data:fetch` reproduces every SHA-256 |

**FAIL on token count** → widen sources before proceeding. Do not compensate by training longer on less data; repeated epochs on 1B tokens will not reach the same loss as 4B unique tokens.

---

## 6. Failure modes

| Symptom | Cause | Action |
|---|---|---|
| Dedup removes >50% | Overlapping dumps or a bad threshold | Inspect samples; verify Jaccard 0.8 is not matching boilerplate-heavy pages |
| Bytes/token far from 3.5 | Wrong tokenizer or a language leak | Re-check [P03](P03-tokenizer.md); check the language filter |
| RAM exhaustion during MinHash | Corpus loaded instead of streamed | Shard to 500 MB; keep only signatures resident |
| Download stalls at ~9 GB | Rate limiting | Resume with backoff; never restart from zero |
| Contamination check finds >1% | Eval set is inside the pretraining data | Stop. Remove the source. Do not "note it as a caveat." |

---

## 7. Do not

- Do not train on TinyStories. It is why the previous model could only produce children's prose.
- Do not use unfiltered CommonCrawl to reach the token target faster.
- Do not skip decontamination "for now." It cannot be repaired later.
- Do not hold out by token offset. Hold out by document.
- Do not download anything whose licence you have not recorded.

---

**Next:** [P03 — Tokenizer](P03-tokenizer.md)
