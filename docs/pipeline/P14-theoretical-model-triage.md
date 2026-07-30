# P14 — Theoretical model triage

> **Stage:** 14 of 19 · **Estimate:** ongoing, parallel to P15–P18 · **GPU time:** ~4 h per tested idea
> **Precondition:** [P10](P10-long-context-evaluation.md) `PASS` — a validated baseline must exist
> **Gate:** 100 architectures catalogued, top 10 costed, ≥3 tested to a verdict.

---

## 1. Why this stage exists

A research programme needs a **pipeline of ideas** that is broader than what it
can test, so that the choice of what to test next is a selection from many rather
than a rationalization of one. The catalogue lives at
[`docs/hypotheses/`](../hypotheses/README.md): **100 architectures, each in
roughly 100 words.**

The catalogue is deliberately shallow. The previous programme's failure was not a
shortage of ideas — it was writing 573 documents about a handful of them. Here,
**an idea earns depth by surviving triage**, and depth means a run, not a
document.

**Law at risk: R5** — cataloguing costs no FLOPs and is therefore not research. The catalogue exists only to feed the ≥3 tests that are.

---

## 2. Catalogue structure

| File | IDs | Theme |
|---|---|---|
| [CATALOG-01](../hypotheses/CATALOG-01-architecture.md) | T001–T020 | Attention, memory, context |
| [CATALOG-02](../hypotheses/CATALOG-02-learning.md) | T021–T040 | Optimization and learning rules |
| [CATALOG-03](../hypotheses/CATALOG-03-quantum.md) | T041–T060 | Quantum and physics-inspired |
| [CATALOG-04](../hypotheses/CATALOG-04-representation.md) | T061–T080 | Representation and inference-time compute |
| [CATALOG-05](../hypotheses/CATALOG-05-systems.md) | T081–T100 | Systems, grounding, continual learning |

Each entry is exactly five fields:

| Field | Content |
|---|---|
| **Core** | The mechanism, 1–2 sentences |
| **Better because** | The specific weakness of current models it addresses |
| **Kill test** | The single measurement that would falsify it |
| **Cost** | `S` (<2 GPU-h) · `M` (2–8 h) · `L` (8–40 h) · `XL` (>40 h, out of reach here) |
| **Serves** | Which of the three objectives — light / fast / long |

**No entry may exceed 120 words.** An idea that needs more than 120 words to
state is not yet understood well enough to be triaged.

---

## 3. Triage scoring

Each idea is scored 1–5 on four axes; the composite decides its rank.

| Axis | Question | Weight |
|---|---|---:|
| **Impact** | If true, how much does it move BPB, size, or speed? | ×3 |
| **Falsifiability** | Can one run settle it? | ×3 |
| **Feasibility** | Can it run on 8 GB in ≤8 GPU-h? | ×2 |
| **Novelty** | Is it untested at this scale, rather than merely untested by us? | ×1 |

\[
\text{score} = 3I + 3F + 2E + N \quad (\text{max } 45)
\]

**Falsifiability is weighted equally with impact on purpose.** A brilliant idea
that cannot be settled by one run is worth less to this programme than a modest
idea that can, because the previous failure was an inability to resolve
questions, not a shortage of ambition.

Anything scoring **<25** is archived permanently. Anything **≥35** enters the
test queue.

---

## 4. Steps

### 4.1 Score the catalogue

```bash
python n32/research/triage.py --catalog docs/hypotheses/ --out results/triage/scores.json
```

Scores are recorded as data, not prose, so the ranking can be re-derived when the
objectives shift.

### 4.2 Cost the top ten

For each of the top 10, write a **half-page implementation sketch** in
`docs/hypotheses/costed/T0NN.md`:

- Exact code changes (files, functions)
- Named control, per the [P13](P13-quantum-inspired-training-lab.md) anti-washing rule
- Committed numeric prediction
- GPU-hours and VRAM estimate
- What a `PASS` and a `FAIL` each look like numerically

Half a page. Not five pages. If the sketch cannot fit, the idea is not ready.

### 4.3 Test at least three

Same protocol as [P13 §2](P13-quantum-inspired-training-lab.md#2-protocol):
commit the prediction, run treatment and control at 200M tokens with identical
seed and data order, resolve to `PROMOTE` / `FALSIFY` / `INCONCLUSIVE`.

### 4.4 Maintain the ledger

`docs/THEORY-LEDGER.md` — one row per tested idea: ID, control, prediction,
measured, verdict, artifact. Same discipline as the quantum ledger: a table,
no narrative, failures as visible as successes.

---

## 5. The current top ten

Provisional, derived from the catalogue as written. Re-derive after
[P07](P07-scaling-microlaws.md) and [P10](P10-long-context-evaluation.md) results
are in — the scores depend on which weaknesses turn out to be real.

| Rank | ID | Idea | Score | Cost | Serves |
|---:|---|---|---:|---|---|
| 1 | **T003** | Hybrid SSM–attention: replace 8 of 12 attention layers with Mamba-style SSM blocks | 42 | M | long, fast |
| 2 | **T007** | Learned KV-cache eviction — keep the top-`k` most-attended keys, drop the rest | 40 | M | long, light |
| 3 | **T024** | Curriculum by measured example difficulty, using per-token loss from a prior run | 39 | M | quality |
| 4 | **T061** | Multi-token prediction — predict the next 4 tokens with auxiliary heads, discard at inference | 38 | S | quality, fast |
| 5 | **T012** | Attention sinks — dedicated always-attended registers for SWA layers | 37 | S | long |
| 6 | **T045** | Unitary recurrent memory (= [Q7](P13-quantum-inspired-training-lab.md#q7--unitary-recurrent-memory-for-long-context)) | 37 | L | long, light |
| 7 | **T083** | Byte-level patching with a learned entropy-based patcher, removing the tokenizer | 36 | L | quality |
| 8 | **T031** | Muon / spectral-norm optimizer for the 2D weight matrices | 36 | S | quality |
| 9 | **T068** | Depth recurrence — loop a 4-layer block 3× with shared weights | 35 | M | light |
| 10 | **T092** | Retrieval-augmented pretraining — nearest-neighbour chunks in-context during training | 35 | L | quality |

### Why these three should be tested first

- **T061 (multi-token prediction)** — cost `S`, well-supported by published results, and the auxiliary heads are discarded at inference, so it improves quality at **zero** deployment cost. Best cost-to-payoff ratio in the catalogue.
- **T012 (attention sinks)** — cost `S`, targets the exact weakness [P10](P10-long-context-evaluation.md) predicts (depth-0% needle failure), and is a ~30-line change.
- **T003 (hybrid SSM–attention)** — cost `M`, and it is the single largest potential win for objectives 1–3 together: SSM layers have **constant** KV memory, which would cut the 32k cache from 38.7 MB toward ~10 MB while speeding up decode.

---

## 6. Deliverables

| Artifact | Path |
|---|---|
| 100-entry catalogue | `docs/hypotheses/CATALOG-0{1..5}-*.md` |
| Scores | `results/triage/scores.json` |
| Costed top 10 | `docs/hypotheses/costed/T0NN.md` |
| Test results | `results/theory/T0NN_result.json` |
| Verdict ledger | `docs/THEORY-LEDGER.md` |
| Public result | `docs/pipeline/results/P14.md` |

---

## 7. Gate

| Metric | Threshold |
|---|---|
| Catalogue entries | **100** |
| Entries with all five fields | **100%** |
| Entries exceeding 120 words | **0** |
| Scored entries | **100** |
| Costed sketches | **≥10** |
| Ideas tested to a verdict | **≥3** |
| Tests with a committed prior prediction | **100%** |
| Tests with a named control | **100%** |

As with [P13](P13-quantum-inspired-training-lab.md), **three falsifications are a
full `PASS`.** The gate measures resolution, not success.

---

## 8. Do not

- Do not write more than 120 words per catalogue entry.
- Do not create a separate document per hypothesis. The catalogue is five files; costed sketches exist only for the top 10.
- Do not test an idea without a named control.
- Do not let the catalogue grow past 100. To add one, retire one.
- Do not treat catalogue size as progress. **Progress is a verdict**, and a verdict costs GPU-hours.
- Do not allow this stage onto the critical path.

---

**Next:** [P15 — Instruction and behaviour](P15-instruction-and-behavior.md)
