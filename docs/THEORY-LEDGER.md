# Theoretical architecture ledger

> One row per **tested** idea from the [100-entry catalogue](hypotheses/README.md). **No narrative.**
> Protocol: [P14](pipeline/P14-theoretical-model-triage.md).

A catalogue entry is a queue item. **A row here is research** — it cost GPU-hours and produced a verdict.

---

## Tested

| ID | Idea | Named control | Predicted | Measured | Verdict | Artifact |
|---|---|---|---|---|---|---|
| — | *(none yet)* | | | | | |

---

## Test queue (provisional top 10)

Re-derive after [P07](pipeline/P07-scaling-microlaws.md) and [P10](pipeline/P10-long-context-evaluation.md) — scores depend on which weaknesses turn out to be real.

| Rank | ID | Idea | Score | Cost |
|---:|---|---|---:|---|
| 1 | [T003](hypotheses/CATALOG-01-architecture.md) | Hybrid SSM–attention | 42 | M |
| 2 | [T007](hypotheses/CATALOG-01-architecture.md) | Learned KV eviction | 40 | M |
| 3 | [T024](hypotheses/CATALOG-02-learning.md) | Difficulty curriculum | 39 | M |
| 4 | [T061](hypotheses/CATALOG-04-representation.md) | Multi-token prediction | 38 | S |
| 5 | [T012](hypotheses/CATALOG-01-architecture.md) | Attention sinks | 37 | S |
| 6 | [T045](hypotheses/CATALOG-03-quantum.md) | Unitary recurrent memory | 37 | L |
| 7 | [T083](hypotheses/CATALOG-05-systems.md) | Byte-level entropy patching | 36 | L |
| 8 | [T031](hypotheses/CATALOG-02-learning.md) | Muon / spectral optimizer | 36 | S |
| 9 | [T068](hypotheses/CATALOG-04-representation.md) | Depth recurrence | 35 | M |
| 10 | [T092](hypotheses/CATALOG-05-systems.md) | Retrieval-augmented pretraining | 35 | L |

**Test first:** T061 (cost `S`, discarded at inference, so quality gain at zero deployment cost), T012 (cost `S`, targets the predicted depth-0% needle failure), T003 (cost `M`, largest combined win for light + fast + long).

---

## Status

| | Count |
|---|---:|
| Catalogued | **100** |
| Scored | 0 |
| Costed sketches | 0 |
| Tested to a verdict | **0** |
| **Gate ([P14](pipeline/P14-theoretical-model-triage.md))** | **100 catalogued · 10 costed · ≥3 tested** |

Three falsifications are a full `PASS`. The gate measures resolution, not success.

## Recording rules

1. Commit the prediction before running.
2. `Measured` cites a JSON path under `results/theory/`.
3. Every `FALSIFY` is also appended to [`negative_results.md`](negative_results.md).
4. The catalogue stays at exactly 100 entries. To add one, retire one.
5. Rows are never deleted.
