# Theoretical model catalogue — 100 architectures

> Governed by [P14](../pipeline/P14-theoretical-model-triage.md). Testing protocol from [P13 §2](../pipeline/P13-quantum-inspired-training-lab.md#2-protocol).
> **The catalogue is not research.** It is a queue. Research is a verdict, and a verdict costs GPU-hours.

---

## What this is

One hundred architectural ideas that could plausibly produce a model better than
current systems **within this project's constraints**: ≤60M non-embedding
parameters, 32k context, one RTX 4060, 4B training tokens.

Each entry is ~80 words. That is deliberate. The previous programme wrote 573
documents about a handful of ideas and tested almost none of them; here an idea
earns depth only by surviving triage, and depth means a training run.

**The count is fixed at 100.** To add one, retire one.

## Entry format

```
### TNNN — Name
**Core.** The mechanism, one or two sentences.
**Better because.** The specific weakness of current models it addresses.
**Kill test.** The single measurement that falsifies it.
`Cost: S|M|L|XL · Serves: light|fast|long|quality`
```

| Cost | GPU-hours | Meaning |
|---|---|---|
| **S** | <2 | Test it this week |
| **M** | 2–8 | Test it if it ranks top-10 |
| **L** | 8–40 | Needs a strong prior to justify |
| **XL** | >40 | Out of reach on this hardware; catalogued for completeness |

## Files

| File | IDs | Theme |
|---|---|---|
| [CATALOG-01](CATALOG-01-architecture.md) | T001–T020 | Attention, memory, context |
| [CATALOG-02](CATALOG-02-learning.md) | T021–T040 | Optimization and learning rules |
| [CATALOG-03](CATALOG-03-quantum.md) | T041–T060 | Quantum- and physics-inspired |
| [CATALOG-04](CATALOG-04-representation.md) | T061–T080 | Representation and inference-time compute |
| [CATALOG-05](CATALOG-05-systems.md) | T081–T100 | Systems, grounding, continual learning |

## Scoring

\[
\text{score} = 3 \times \text{Impact} + 3 \times \text{Falsifiability} + 2 \times \text{Feasibility} + \text{Novelty}
\]

Each axis 1–5; maximum 45. **Falsifiability is weighted equally with impact** —
an idea that cannot be settled by one run is worth less here than a modest idea
that can, because the previous failure was an inability to resolve questions, not
a shortage of ambition.

Score <25 → archived. Score ≥35 → test queue.

## The rules that make this scientific

1. **Name the control.** Every idea is benchmarked against the nearest existing technique, never against a naive baseline. An idea that beats `N32-base` but not its control has demonstrated nothing.
2. **Commit the prediction first.** Write the expected number to git before running.
3. **Resolve.** `PROMOTE`, `FALSIFY`, or `INCONCLUSIVE` — and `INCONCLUSIVE` at most twice, then it becomes `FALSIFY`. Nothing sits in `HOLD`.
4. **Publish the failures.** [`docs/negative_results.md`](../negative_results.md) and [`docs/THEORY-LEDGER.md`](../THEORY-LEDGER.md).

## Honest framing of "better than current AIs"

None of these will produce a 42M-parameter model that outperforms a frontier
system in general capability. That is not arithmetically possible, and claiming
it would repeat the previous programme's central error.

What "better" means here is precise and achievable:

| Better at | Against |
|---|---|
| BPB per parameter | Models of comparable and larger size |
| BPB per byte of memory | Anything that fits on this hardware |
| Usable context per MB of KV cache | Standard full-attention transformers |
| Tokens/second per unit of quality | Larger models on the same GPU |
| Training quality per GPU-hour | Published small-model recipes |

Several entries here could genuinely beat frontier systems **on those axes**.
That is the claim. Nothing larger.
