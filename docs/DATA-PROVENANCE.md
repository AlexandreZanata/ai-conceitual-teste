# Data provenance

> Licence and source record for every corpus this project trains on.
> Maintained by [P02](pipeline/P02-data-foundation.md). **A source with an unrecorded licence may not be downloaded.**

Legal defensibility cannot be retrofitted at release time. This file is written as data is acquired, not afterwards.

---

## 1. Rules

| Rule | Reason |
|---|---|
| Public URLs only; licence recorded before download | Cannot be reconstructed later |
| Every source carries `id`, `url`, `licence`, `sha256`, `expected_bytes`, `attribution_required` | Reproducibility and attribution |
| Rejected sources are recorded here with the reason | Shows the filter was applied, not skipped |
| Corpus bytes are **never committed** — only the manifest | See [`REPO-HYGIENE.md`](REPO-HYGIENE.md) |
| Decontaminate against every eval set **before** tokenizing | Irreversible if skipped |

Registry: `n32/data/sources.py` · Fetch: `npm run data:fetch` · Working manifest: `data/manifest.json` (gitignored) · Committed hashes: `results/data/summary.json` → `manifest_files`.

---

## 2. Target mixture — 4.0 B tokens

Specified in [P02 §2](pipeline/P02-data-foundation.md#2-target-corpus). Fill in the measured columns as acquisition proceeds.

| Source | Share | Target tokens | Licence | Acquired | SHA-256 recorded |
|---|---:|---:|---|:---:|:---:|
| FineWeb-Edu (sample-10BT, all 14 shards) | 40%→100%* | 4.42 B measured | ODC-By 1.0 | ☑ | ☑ |
| The Stack v2 / StarCoder (permissive only) | 25% | 1.00 B | per-file, permissive | ☐ deferred | — |
| Cosmopedia v2 | 15% | 0.60 B | Apache 2.0 | ☐ deferred | — |
| Wikipedia EN | 10% | 0.40 B | CC BY-SA 3.0 | ☐ deferred | — |
| Technical documentation (seed) | 7% | 0.28 B | mixed — attribute | ☑ seed only | ☑ |
| arXiv cs.* abstracts + intros | 3% | 0.12 B | arXiv non-exclusive | ☐ deferred | — |

\* Stack auth gated; Cosmopedia/Wikipedia/arXiv deferred this stage. FineWeb-Edu sample-10BT widened to cover the ≥4.0×10⁹ token gate alone. Revisit mixture diversity after P03 if BPB plateaus.

**CC BY-SA on Wikipedia is a share-alike licence.** Confirm at [P18](pipeline/P18-release-and-publication.md) whether it constrains the released model's licence, and record the conclusion here.

---

## 3. Carried forward from the previous programme

These 22 public sources were licence-checked before the reset and are a valid seed for the "technical documentation" slice. The **URLs and licences** are reusable; the downloaded blobs and the old registry code were deleted.

| Domain | Sources | Licence |
|---|---|---|
| **Bitcoin / protocol** | Bitcoin Core README, developer-notes, `doc/bips.md`, JSON-RPC and REST docs; BIPs 1, 32, 39, 141, 340 | MIT + BSD-2-Clause |
| **Programming** | Python tutorial (intro, control flow, data structures, classes, I/O); Rust book ch. 03–05 | PSF-2.0 · MIT/Apache-2.0 |
| **Systems / networking** | IETF RFC 791, RFC 8446 (TLS 1.3), RFC 8949 (CBOR) | IETF Trust — freely distributable |

Fetched seed in this stage: Python tutorial introduction + RFC 791 (see `data/raw/tech_docs_seed/`).

**Scale caveat:** this seed totalled **~164 KB** on disk — a provenance anchor, not the 7% slice. Under-estimating corpus scale was the root cause of the previous failure ([assessment §4, C1](ASSESSMENT-2026-07-30.md#c1--data-starvation-fatal)).

---

## 4. Rejected sources

| Source | Reason for rejection | Date |
|---|---|---|
| `roneneldan/TinyStories` | Children's fiction corpus that caused prior failure; banned by P02 §7 | 2026-07-30 |
| Unfiltered CommonCrawl / FineWeb without edu filter | P02 §2: quality-starved models lose BPB on unfiltered crawl | 2026-07-30 |
| `bigcode/the-stack-v2` (unfiltered) | Requires per-file permissive filter + HF gate; deferred until auth available | 2026-07-30 |

---

## 5. Decontamination record

Filled in by [P02 §3.2](pipeline/P02-data-foundation.md#32-clean).

| Eval set | Hash | 13-gram overlap | Documents removed |
|---|---|---:|---:|
| `data/eval_sets/math_probe.txt` | see `results/data/summary.json` | 0.0 | 0 |
| `data/eval_sets/needle_probe.txt` | see `results/data/summary.json` | 0.0 | 0 |

Full P06/P17 eval sets do not exist yet; probes stand in so the 13-gram path is exercised. Re-run decontamination when those eval sets land.

**Measured (P02 gate):** total tokens 4,416,607,471 · held-out 10,000,067 · bytes/token ≈ 4.30 · exact residual 0.0 · near residual 0.00018 · unknown licences 0. Artifact: `results/data/summary.json`.
