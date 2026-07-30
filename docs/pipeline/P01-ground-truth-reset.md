# P01 — Ground-truth reset

> **Stage:** 1 of 19 · **Estimate:** 1 day · **GPU time:** none
> **Precondition:** [P00](P00-charter-and-hardware-envelope.md) `PASS`
> **Gate:** ≤40 npm scripts, legacy removed and tagged, `npm run verify` green, one training entry point.
>
> **Partially executed on 2026-07-30.** Sections 2.1–2.4 are done. **Section 2.5 (contract tests) remains** — this stage is not closed and `docs/pipeline/results/P01.md` must not be written until it is.

---

## 1. Why this stage exists

The repository contained **856 npm scripts, 1,506 Python files, and 341,926 lines** of orchestration serving a 3.35M-parameter model and an 18-row lookup table. An agent could not navigate it, and the volume itself is what caused the failure — see [assessment §4, C5](../ASSESSMENT-2026-07-30.md#c5--process-metastasis).

**Law at risk: R6** — one pipeline. If two entry points survive this stage, the stage failed.

### Why deletion, not a `legacy/` directory

The original plan quarantined the old tree into `legacy/`. That was changed during execution, for a reason worth recording:

**A quarantine directory that an agent can read is not a quarantine.** 341,926 lines sitting in the working tree would be indexed, grepped, and eventually imported — and the whole point is that this material teaches the protocol that failed. A git tag is a strictly better quarantine: the evidence stays perfectly recoverable and byte-identical, but it is invisible to search, impossible to import, and cannot be extended by accident.

```bash
git checkout legacy/waves-w-bh              # inspect the whole old tree
git show legacy/waves-w-bh:path/to/file     # recover one file
```

Nothing was lost. The assessment stays checkable.

---

## 2. Steps

### 2.1 Tag the historical state first — **DONE**

```bash
git tag -a legacy/waves-w-bh -m "Frozen wave protocol, waves W-BH. See docs/ASSESSMENT-2026-07-30.md"
```

Tagged at `2bcea82` (2026-07-29). **Nothing else in this stage is safe until this tag exists.**

### 2.2 Remove the wave machinery — **DONE**

| Removed | Was |
|---|---|
| `nano_lm/` | 1,523 files — wave runners, gate ops, report writers, wave tests |
| `docs/results/nano-lm/` | 573 wave reports |
| `docs/archive/`, `paper/` | Frozen EvoGen docs and the wave-era paper |
| `src/`, `tests/`, `experiments/`, `web/`, `CMakeLists.txt` | EvoGen C++ survival PoC |
| `agent-rules/`, `agent-harness/` | Generic rules harness — content folded into `.cursor/rules/` |
| Wave-era docs | `GLOSSARY.md`, `NANO-STUDENT-AGENDA.md`, `NANO-LM-TRACK.md`, `arxiv.md`, `paper_narrative.md` |

**Salvaged into the active tree** — the licence provenance, which is legally valuable and cannot be reconstructed:

| Salvaged | Now at |
|---|---|
| `nano_lm/data/CURATED-SOURCES.md` | [`docs/DATA-PROVENANCE.md`](../DATA-PROVENANCE.md) §3 |

Three files originally marked "keep" were **not** salvaged, deliberately:

| Not kept | Why | Recover with |
|---|---|---|
| `data_tiny.py` | Plumbing for a 1.24 MB corpus. [P02](P02-data-foundation.md) needs streaming shards for 14 GB — a different design, not an adaptation. | `git show legacy/waves-w-bh:nano_lm/src/data_tiny.py` |
| `qt_quant.py` | Real int8, but written against the old model class. [P12](P12-quantization-and-runtime.md) rewrites it in ~60 lines. | `git show legacy/waves-w-bh:nano_lm/src/qt_quant.py` |
| `curated_sources.py` | URLs and licences preserved in `DATA-PROVENANCE.md` §3; the code was coupled to the deleted tree. | `git show legacy/waves-w-bh:nano_lm/src/curated_sources.py` |

Read them if you want a reference implementation. **Do not restore them wholesale.**

### 2.3 Cut `package.json` to the bone — **DONE**

856 scripts → **39**. Every surviving script (a) runs from a clean clone, (b) does real work, and (c) is referenced by a stage spec. A script referenced by no stage is deleted.

The ceiling is enforced, not merely documented: `scripts/check_repo_hygiene.py` fails the commit at 41.

### 2.4 Establish the new source layout — **DONE**

```
n32/
  data/        # acquisition, cleaning, dedup, tokenization   -> P02
  tokenizer/   # BPE training and evaluation                  -> P03
  model/       # architecture: attention, layers, config      -> P04, P08
  train/       # loop, optimizer, schedule, checkpointing     -> P05
  eval/        # BPB, long-context, benchmarks                -> P06, P10, P17
  serve/       # inference, KV cache, quantized runtime       -> P11, P12
  research/    # quantum-inspired and theoretical probes      -> P13, P14
bench/         # hardware and performance measurement         -> P00, P11
```

One module per concern. Cyclomatic complexity ≤10 per function; line caps waived.

### 2.5 Write the contract test suite — **REMAINING**

Legacy tests asserted that markdown files contained the string `PROMOTE`. That category is gone. The new suite tests **logical contracts that fail when the code breaks them**:

| Contract | Test |
|---|---|
| Param count matches the config arithmetic | `test_model_param_count` — compute expected from config, compare to `sum(p.numel())` |
| Attention masks are causal | `test_causal_mask` — future positions contribute exactly zero |
| Sliding window attends exactly `w` positions | `test_swa_window_width` |
| Tokenizer round-trips losslessly | `test_tokenizer_roundtrip` on held-out bytes |
| Checkpoint resume is bit-exact | `test_resume_bitexact` — 10 steps vs 5 + resume + 5 |
| BPB is tokenizer-invariant | `test_bpb_invariance` — same text, two vocabs, within 1% |

Most of these need code that does not exist yet, so they land alongside [P03](P03-tokenizer.md)–[P05](P05-training-harness.md). **What P01 owes now is the harness itself**: `pytest` wired into `npm test` and `scripts/check-tests.sh`, plus the first test that can actually fail today.

**Never** write a test that mirrors production logic, and never weaken an assertion to make CI green.

---

## 3. Deliverables

| Artifact | Path | Status |
|---|---|:---:|
| Legacy tag | `legacy/waves-w-bh` (git tag) | done |
| New source tree | `n32/` with module stubs | done |
| Reduced scripts | `package.json`, 39 scripts | done |
| Hygiene enforcement | `scripts/check_repo_hygiene.py`, `lefthook.yml`, [`REPO-HYGIENE.md`](../REPO-HYGIENE.md) | done |
| Contract tests | `n32/**/test_*.py` | **remaining** |
| Public result | `docs/pipeline/results/P01.md` | **blocked on tests** |

---

## 4. Gate

| Metric | Threshold | Measured 2026-07-30 |
|---|---|---|
| npm scripts | **≤40** | 39 ✓ |
| Tracked files | **≤400** | ~60 ✓ |
| Active-tree Python files | **≤80** | 14 ✓ |
| Training entry points | exactly **1** | 1 (`n32.train.loop`) ✓ |
| `git tag legacy/waves-w-bh` | exists | ✓ |
| Legacy code in the working tree | **0 files** | ✓ |
| `npm run verify` | green | ✓ |
| Contract tests that can fail | **≥1** | **0 — gate not met** |

---

## 5. Failure modes

| Symptom | Cause | Action |
|---|---|---|
| Urge to restore a deleted module | Sunk cost | Read it via `git show`, then write the ~60 lines you actually need |
| Script count creeps back up | Convenience aliases | Every script needs a stage reference; the hygiene gate rejects the rest |
| Tracked-file count climbing | Documents written instead of code | Re-read [assessment §4, C5](../ASSESSMENT-2026-07-30.md#c5--process-metastasis) |
| A test asserts on a document's contents | Wave habit returning | Delete it. Assert on behaviour. |

---

## 6. Do not

- Do not delete or move the `legacy/waves-w-bh` tag. It is the evidence base for the assessment.
- Do not recreate a `legacy/` directory in the working tree.
- Do not port the wave protocol into the new tree under new names.
- Do not keep the 18-row `error_bank.jsonl` on any product path. It may be used **only** as an eval fixture in [P16](P16-grounding-and-retrieval.md), clearly labelled as retrieval.
- Do not preserve `teacher_lp` as a metric. It has no committed artifacts and is not comparable across tokenizers. [P06](P06-evaluation-harness.md) replaces it with bits-per-byte.

---

**Next:** [P02 — Data foundation](P02-data-foundation.md)
