# P07 — Scaling micro-laws

> **Stage:** 7 of 19 · **Estimate:** 3 days · **GPU time:** ~20 h
> **Precondition:** [P06](P06-evaluation-harness.md) `PASS`
> **Gate:** a fitted scaling law that predicts held-out loss of an unseen configuration within 3%.

---

## 1. Why this stage exists

Every architectural decision in [P04](P04-baseline-architecture.md) — width 512,
depth 12, vocabulary 16,384 — is currently a **defensible guess**. Published
scaling laws (Kaplan, Chinchilla) were fitted at scales 100–10,000× larger and on
different data mixtures. Extrapolating them down to 42M parameters on this
mixture is unjustified.

This stage fits the laws **on this hardware, this data, and this architecture**,
so that the remaining ~20 GPU-hours of the programme are spent at a measured
optimum rather than an inherited one.

It is also the only stage permitted to overrule [P04](P04-baseline-architecture.md) —
and only with the artifact defined here.

**Law at risk: R2** — a scaling claim without a fitted-curve artifact and its residuals is not a scaling claim.

---

## 2. Design of the sweep

Twelve short runs, each **200M tokens** (~1.7 GPU-hours). Total ≈ 20 hours.

200M tokens is enough for the loss curve to reach its power-law regime while
remaining short enough to run twelve of them.

### Grid A — shape at fixed parameter budget (~42M total)

Isolates depth versus width. All six runs use the same token budget.

| Run | `d_model` | `n_layers` | Non-embed params | Aspect ratio |
|---|---:|---:|---:|---:|
| A1 | 384 | 20 | 31.7 M | 19.2 |
| A2 | 448 | 15 | 32.4 M | 29.9 |
| **A3** | **512** | **12** | **33.8 M** | **42.7** |
| A4 | 640 | 8 | 35.2 M | 80.0 |
| A5 | 768 | 5 | 31.7 M | 153.6 |
| A6 | 512 | 16 | 45.1 M | 32.0 |

**Prediction:** the optimum sits at an aspect ratio of 30–60, making A3 or A6 the
winner. If A5 (very wide, very shallow) wins, something is wrong with the deep
runs — most likely initialization scaling ([P04 §4.2](P04-baseline-architecture.md#42-initialization)).

### Grid B — parameter/token trade-off at fixed compute

Isolates the Chinchilla ratio at this scale. Fixed compute ≈ 1.5 × 10¹⁷ FLOPs.

| Run | Params | Tokens | Tokens/param |
|---|---:|---:|---:|
| B1 | 12 M | 2.0 B | 167 |
| B2 | 25 M | 1.0 B | 40 |
| **B3** | **42 M** | **0.6 B** | **14** |
| B4 | 80 M | 0.3 B | 4 |

**Prediction:** at this scale, and for a model intended for **inference
efficiency**, the optimum will favour *smaller model, more tokens* than Chinchilla's
20:1. Chinchilla optimizes training compute; this project optimizes deployed
size and speed, which pushes strongly toward over-training a small model. If B1
or B2 wins on BPB, **shrink the model and train longer** — that serves objective 1
(light) and objective 2 (fast) simultaneously.

### Grid C — learning rate

Two extra runs at the winning shape, LR ∈ {3e-4, 1.2e-3}, to bracket the 6e-4
assumption and confirm it is not on a cliff edge.

---

## 3. Steps

### 3.1 Run the sweep

```bash
npm run train:sweep -- --grid configs/sweep_a.yaml --tokens 2e8 --out runs/sweep/
```

Every run must share: the same data shards in the same order, the same seed, the
same eval protocol. **Only the swept variable changes.** A sweep with two
confounded variables is worse than no sweep, because it produces a confident
wrong answer.

### 3.2 Fit the law

Fit the Chinchilla parametric form to the observed final losses:

\[
L(N, D) = E + \frac{A}{N^{\alpha}} + \frac{B}{D^{\beta}}
\]

- \(E\) — irreducible entropy of the data
- \(A, \alpha\) — how loss falls with parameters
- \(B, \beta\) — how loss falls with tokens

Fit with Huber loss in log space (robust to a single bad run). Report parameter
estimates **with confidence intervals**, and publish the residual for every run.

```bash
python n32/research/fit_scaling.py --runs runs/sweep/ --out results/scaling/law.json
```

### 3.3 Validate by prediction

The only honest test of a fitted law: **predict before measuring.**

1. Choose a configuration **not in the sweep** (e.g. `d_model=576, n_layers=14`, 400M tokens).
2. Write the predicted final BPB into `results/scaling/prediction.json` **and commit it**.
3. Run the configuration.
4. Compare.

Committing the prediction first is what makes this a test rather than a
post-hoc fit. Within 3% is a `PASS`.

### 3.4 Re-derive the design point

With a validated law, compute the optimal configuration subject to the real
constraints:

| Constraint | Value | Source |
|---|---|---|
| Training compute | ≤72 h at measured MFU | [P00](P00-charter-and-hardware-envelope.md) `budget.json` |
| Non-embedding params | ≤60 M | objective 1 |
| Inference speed | ≥100 tok/s @8k | objective 2 |
| KV cache at 32k | ≤50 MB | objective 3 |
| Available tokens | 4.0 B | [P02](P02-data-foundation.md) |

Solve for the minimum predicted BPB inside that feasible region.

**If the answer differs from `N32-base`, change `N32-base`** and record the change
in `docs/pipeline/results/P07.md` with the law, the residuals, and the validated
prediction. This is the one sanctioned way to revise [P04](P04-baseline-architecture.md).

---

## 4. Deliverables

| Artifact | Path |
|---|---|
| Sweep configs | `configs/sweep_{a,b,c}.yaml` |
| Sweep runs | `runs/sweep/*/metrics.jsonl` |
| Fitted law with CIs | `results/scaling/law.json` |
| Committed prediction | `results/scaling/prediction.json` |
| Validation outcome | `results/scaling/validation.json` |
| Isoflop plot | `results/scaling/isoflop.svg` |
| Final design point | `configs/n32-final.yaml` |
| Public result | `docs/pipeline/results/P07.md` |

---

## 5. Gate

| Metric | Threshold |
|---|---|
| Sweep runs completed | **≥12** |
| Fit quality (R² in log space) | **≥0.95** |
| Held-out prediction error | **≤3%** |
| Prediction committed **before** the validation run | verifiable in git history |
| Design point derived from the law, not asserted | documented in P07.md |
| Confidence intervals on \(\alpha, \beta\) | reported |

**If prediction error >3%**, the law does not describe this regime. Do **not**
use it to justify design changes; record the failure in
[`docs/negative_results.md`](../negative_results.md) and keep `N32-base` as
specified. A failed scaling study is a legitimate, publishable outcome.

---

## 6. What the answers will likely be

Stated in advance so the stage can be wrong.

| Question | Prediction | Consequence if true |
|---|---|---|
| Optimal aspect ratio | 30–60 | `d_model=512, n_layers=12–16` confirmed |
| Optimal tokens/param at fixed compute | 50–150, far above Chinchilla's 20 | Shrink to ~25M params, train on all 4B tokens |
| Optimal LR at 42M | 5e-4 – 8e-4 | 6e-4 confirmed |
| \(\alpha\) (parameter exponent) | 0.25–0.40 | Consistent with published values |
| \(\beta\) (token exponent) | 0.25–0.40 | Consistent with published values |
| \(E\) (irreducible BPB) | 0.6–0.9 | Sets the ceiling on what any model can reach on this data |

\(E\) is the most valuable number this stage produces: it is the **best BPB any
model could ever achieve on this corpus**, and it turns "is 1.35 good?" from an
opinion into arithmetic.

---

## 7. Failure modes

| Symptom | Cause | Action |
|---|---|---|
| All runs give nearly identical loss | Too few tokens to separate them | Raise to 400M tokens per run and re-run |
| Deep runs (A1) diverge | Init not scaled by `1/sqrt(2L)` | Fix [P04 §4.2](P04-baseline-architecture.md#42-initialization), re-run the grid |
| Fit R² <0.8 | Confounded variables, or one bad run | Plot residuals; find the outlier; check nothing else changed |
| Prediction error 10%+ | The parametric form does not hold here | Report honestly; keep `N32-base`; note the limitation in [P18](P18-release-and-publication.md) |
| Sweep exceeds 30 h | Runs too long | 200M tokens per run is the design; do not inflate |

---

## 8. Do not

- Do not fit the law and then "adjust" the design by intuition. Either the law is used or it is not.
- Do not change more than one variable per sweep axis.
- Do not skip the committed-prediction step. Without it, this is curve-fitting, not science.
- Do not extrapolate the law more than 3× beyond the fitted range.
- Do not treat published Chinchilla constants as applicable here without validating them.

---

**Next:** [P08 — Efficient attention](P08-efficient-attention.md)
