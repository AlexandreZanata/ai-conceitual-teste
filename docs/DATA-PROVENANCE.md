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

Registry: `n32/data/sources.py` · Fetch: `npm run data:fetch` · Manifest: `data/manifest.json` (hashes committed, bytes not).

---

## 2. Target mixture — 4.0 B tokens

Specified in [P02 §2](pipeline/P02-data-foundation.md#2-target-corpus). Fill in the measured columns as acquisition proceeds.

| Source | Share | Target tokens | Licence | Acquired | SHA-256 recorded |
|---|---:|---:|---|:---:|:---:|
| FineWeb-Edu (sample-10BT) | 40% | 1.60 B | ODC-By 1.0 | ☐ | ☐ |
| The Stack v2 / StarCoder (permissive only) | 25% | 1.00 B | per-file, permissive | ☐ | ☐ |
| Cosmopedia v2 | 15% | 0.60 B | Apache 2.0 | ☐ | ☐ |
| Wikipedia EN | 10% | 0.40 B | CC BY-SA 3.0 | ☐ | ☐ |
| Technical documentation | 7% | 0.28 B | mixed — attribute | ☐ | ☐ |
| arXiv cs.* abstracts + intros | 3% | 0.12 B | arXiv non-exclusive | ☐ | ☐ |

**CC BY-SA on Wikipedia is a share-alike licence.** Confirm at [P18](pipeline/P18-release-and-publication.md) whether it constrains the released model's licence, and record the conclusion here.

---

## 3. Carried forward from the previous programme

These 22 public sources were licence-checked before the reset and are a valid seed for the "technical documentation" slice. The **URLs and licences** are reusable; the downloaded blobs and the old registry code were deleted.

| Domain | Sources | Licence |
|---|---|---|
| **Bitcoin / protocol** | Bitcoin Core README, developer-notes, `doc/bips.md`, JSON-RPC and REST docs; BIPs 1, 32, 39, 141, 340 | MIT + BSD-2-Clause |
| **Programming** | Python tutorial (intro, control flow, data structures, classes, I/O); Rust book ch. 03–05 | PSF-2.0 · MIT/Apache-2.0 |
| **Systems / networking** | IETF RFC 791, RFC 8446 (TLS 1.3), RFC 8949 (CBOR) | IETF Trust — freely distributable |

Cap large RFCs with `max_bytes` when fetching. Recover the original registry if needed:

```bash
git show legacy/waves-w-bh:nano_lm/src/curated_sources.py
```

**Scale caveat:** this seed totalled **1.24 MB** — roughly 0.008% of the 14 GB the new corpus needs. It is a starting point for one 7% slice, not a corpus. Under-estimating this was the root cause of the previous failure ([assessment §4, C1](ASSESSMENT-2026-07-30.md#c1--data-starvation-fatal)).

---

## 4. Rejected sources

Record every rejection. An empty table after acquisition means the licence filter was never applied.

| Source | Reason for rejection | Date |
|---|---|---|
| — | | |

---

## 5. Decontamination record

Filled in by [P02 §3.2](pipeline/P02-data-foundation.md#32-clean).

| Eval set | Hash | 13-gram overlap | Documents removed |
|---|---|---:|---:|
| — | | | |
