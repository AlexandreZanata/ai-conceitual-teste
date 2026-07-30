# Technical assessment — 2026-07-30

> **Status:** independent audit of the repository as it stands at commit `HEAD` (564 commits, last activity 2026-07-29).
> **Purpose:** establish ground truth before the project is redirected. Written to be uncomfortable, not encouraging.
> **Method:** static audit of `nano_lm/`, `results/`, `docs/results/nano-lm/`, `paper/`, `.local/`; hardware probe; verification of every headline number by direct measurement.
>
> **Path note:** every path cited below is as it stood at audit time. That tree was deleted later the same day ([P01](pipeline/P01-ground-truth-reset.md)) and preserved byte-identical in the git tag `legacy/waves-w-bh`. To re-verify any number here:
> `git checkout legacy/waves-w-bh` — or, for a single file, `git show legacy/waves-w-bh:<path>`.

---

## 1. Executive verdict

**The project produced a large research bureaucracy around a model that was barely trained and has never generated a useful sentence.**

The shipped product answers questions by matching strings against an 18-row JSON file. The neural network exists, is real, and is irrelevant to the product. Thirty-seven "waves" of work did not change this, because none of them addressed the two things that actually determine model quality: **the amount of data trained on** and **the amount of compute spent**.

This is not a failure of effort. It is a failure of *measurement selection*. The project optimized metrics it could move (documentation gates, refusal rates, string-pack pass counts) instead of the metric that mattered and was never once recorded: **held-out perplexity**.

---

## 2. Measured ground truth

Every number below was verified directly during this audit.

### 2.1 What exists

| Quantity | Measured value | How verified |
|---|---:|---|
| Python files (excl. venv) | **1,506** | `find nano_lm -name '*.py'` |
| Lines of Python | **341,926** | `cat` + `wc -l` |
| npm scripts in `package.json` | **856** | `Object.keys(pkg.scripts).length` |
| Markdown files in `docs/` | **789** | `find docs -name '*.md'` |
| Wave report files in `docs/results/nano-lm/` | **573** | `ls *.md` |
| Git commits | **564** | `git log --oneline` |
| **Model checkpoints on disk** | **1** (duplicated to 2 paths) | `find . -name '*.pt'` |
| Checkpoint size | **13 MB** | `ls -lh B2_seed0.pt` |
| Unique model parameters | **~3.35 M** | `student_model.py`: hidden=64, layers=2, vocab=50257 |
| Curated corpus on disk | **1.24 MB** across 4 files | `du -sb nano_lm/data/curated` |
| Production answer bank | **18 rows** | `wc -l results/nano-lm/wave-z/error_bank.jsonl` |

### 2.2 The ratio that defines the project

> **341,926 lines of Python and 789 documents were written to support a 3.35M-parameter model trained for approximately 120 optimizer steps on children's stories, serving answers from an 18-row lookup table.**

That is roughly **19,000 lines of code and 44 documents per row of the answer bank**.

### 2.3 The model that was actually trained

| Property | Value | Source |
|---|---|---|
| Architecture | HuggingFace `GPTNeoConfig` — not custom | `nano_lm/src/student_model.py` |
| Hidden size / layers / heads | 64 / 2 / 4 | same |
| Vocabulary | 50,257 (GPT-2 BPE, inherited) | same |
| Max position embeddings | **512** | same |
| Training objective | KD (KL) from `roneneldan/TinyStories-33M` | `nano_lm/src/train_kd.py` |
| Optimizer steps | **~120** | `run_formal_hdeck.py`: `steps_kd: 120` |
| Training examples | **300**, seq_len 128, batch 4 | same |
| Upper bound on tokens seen | **~1.5 × 10⁵ token-positions** | 120 × 4 × 128, before repeats |
| Training corpus | **TinyStories** (children's fiction) | `data_tiny.py` |
| Seeds completed | **1 of 3** (`seed0` only) | `results/` contains no seed1/seed2 |
| Loss curve on disk | **none** | no training log persisted |
| Perplexity ever measured | **never** | the string `perplexity`/`ppl` appears nowhere in the repo |

**The single most damning fact:** a language-model project ran for 564 commits without ever computing the standard quality metric for a language model.

### 2.4 The parameter budget was spent on the wrong thing

With `vocab=50257` and `hidden=64`, the embedding matrix alone is `50257 × 64 = 3,216,448` parameters.

| Component | Params | Share |
|---|---:|---:|
| Token embeddings (tied with output head) | 3,216,448 | **96.0%** |
| 2 transformer layers + norms | ~132,000 | 4.0% |
| **Total** | ~3,348,928 | 100% |

**96% of the model is a lookup table for a vocabulary it never needed.** The actual reasoning machinery is 132K parameters — smaller than a 1990s MNIST network. No amount of decode tuning, distillation tricks, or refusal gating can extract intelligence from 132K parameters of transformer. This single design choice, made once and never revisited across 37 waves, capped the project's ceiling at zero.

### 2.5 What the product actually does

Trace of the documented production path `npm run nano:z:ask -- --wrap --semwrap`:

1. Normalize the question string.
2. Compare for **exact string equality** against 18 rows in `error_bank.jsonl` → if hit, return the pre-written `gold` text with `wall_ms=0, n_new=0`.
3. If miss, run **Jaccard token overlap** plus ~1,900 lines of hand-coded traps (`semwrap_ops.py`) → return a bank row or refuse.
4. If still miss, run the neural model (CUDA required) → output is almost always junk → the abstain gate converts it to a refusal.

The telemetry is honest (`n_new=0` means zero tokens generated). The framing in the wave reports was not. **The reported "HITL 9.0 / PROMOTE" scores across waves AA–BG measure the quality of hand-written text in a JSON file.**

Worse, the flagship demo row is itself broken. The bank entry for the canonical `add` question contains:

```
gold: "def add"    error: true    score: 1.0    model_raw: ""
```

That is a truncated snapshot of a *failed* decode, stored as the correct answer, and scored 1.0.

### 2.6 The generative goal was never approached

`true_continue` — the project's own definition of "the model generated something novel and readable" — has a recorded value of **0 across every artifact that exists**. NANOGEN experiments 1 through 18 were opened; all resolved to HOLD, DEFER, or SKIP. The documented failure mode of open generation is period collapse: the model emits `........`.

Wave Z measured this honestly and correctly: raw decode scored **1.0/10** across 10 questions. Every subsequent wave routed around that result instead of fixing its cause.

### 2.7 Evidence integrity

251 formal reports cite `Source: results/nano-lm/formal-*/formal.json`.

```
$ find results -name formal.json | wc -l
0
```

**Zero of those files exist.** The `teacher_lp` scoreboard that ranks the STAG′ / EARLY / POOL "tips" — the core scientific claim of the tip stack — has no committed backing artifact. The numbers may have been real when generated; they are not reproducible now.

Additionally, the "champion" model bundle manifest records its export path as `/tmp/pytest-of-iiii/pytest-9/.../champion` — the production artifact was exported from a pytest temporary directory.

---

## 3. What is genuinely worth keeping

An honest audit must also record what survived. Four things did.

| Asset | Why it is real | Where |
|---|---|---|
| **Wave Z negative result** | Correctly measured that the champion decode fails interactive Q&A (1.0/10). Properly recorded and never retracted. | `docs/results/nano-lm/wave-z-hitl-z1.md` |
| **Latency methodology** | Per-mode p50/p99 on the production path (LOOKUP ~0 ms, DECODE 12.7/17.0 ms, ABSTAIN 95.4/125.3 ms). Real measurement discipline. | `paper/tables/latency_ba.tex` |
| **IQ battery v0** | 50 stratified probes with an aggregate that *admits* 6 gold misses. The first metric in the project that could report bad news. | `results/nano-lm/wave-bh/iqbat_summary.json` |
| **`docs/negative_results.md`** | A genuinely rigorous kill-list. KILL/HOLD/DEFER verdicts recorded against named hypotheses. This document is better than most published ML work. | `docs/negative_results.md` |

The project's *self-awareness* is high. `negative_results.md`, `paper/limitations.tex`, and the lab book all state plainly that generation does not work and that pack-passing is theater. **The instrumentation for honesty was built. It was then routed around rather than obeyed.**

---

## 4. Root-cause analysis

Five causes, in order of damage.

### C1 — Data starvation (fatal)
1.24 MB of curated text, and the model was not even trained on it — it was trained on TinyStories. A 3.35M-parameter model needs on the order of **10⁹ tokens** to be worth anything. It saw about **10⁵ token-positions**. That is a factor of **10,000× under-trained**.

### C2 — Parameter budget misallocation (fatal)
96% of parameters in an inherited 50k vocabulary. Fixing this is a one-day change (train a domain tokenizer at 8k–16k vocab) and would have freed ~3M parameters for actual depth and width.

### C3 — No held-out loss metric (fatal to feedback)
Without perplexity or bits-per-byte, there was no gradient signal at the *project* level. Every decision was made on proxy metrics that could be satisfied by editing markdown. The project could not tell improvement from motion.

### C4 — Retrieval used to hide the model's failure
Wrapping a broken generator in a lookup table produced a demo that scored 9.0 and a model that stayed broken. The wrapper became the product; the research target was quietly abandoned while the vocabulary of the research target was retained.

### C5 — Process metastasis
The wave machine (session → formal → freeze → report → real-eval, ×37) generated work that felt like progress and consumed the entire budget. 856 npm scripts is not a research programme; it is an artifact of an agent optimizing for visible output.

### The pattern in one sentence
**Every wave optimized something that could be made green by writing text, and nothing that required spending FLOPs.**

---

## 5. The hardware was never used

This is the most actionable finding.

| Resource | Available | Used by this project |
|---|---|---|
| GPU | **NVIDIA RTX 4060 Mobile, 8 GB VRAM, CUDA 13.0** | one ~120-step training run |
| GPU idle | **8,157 MB of 8,188 MB free at audit time** | — |
| CPU | i7-13620H, 10 cores / 16 threads, 4.9 GHz | eval orchestration |
| RAM | 31 GB | — |
| Disk free | **214 GB** | 1.24 MB of corpus |
| PyTorch | 2.12.1 + cu130, CUDA available | yes |

**A single RTX 4060 can train a 40M-parameter model on 4 billion tokens in roughly 35 hours of wall clock.** That is a weekend. The project instead spent months producing 341,926 lines of orchestration.

Order-of-magnitude budget, using \(C \approx 6ND\):

\[
C = 6 \times 4{\times}10^{7} \times 4{\times}10^{9} \approx 9.6 \times 10^{17}\ \text{FLOPs}
\]

At a realistic sustained \(7.5 \times 10^{12}\) FLOP/s (bf16, ~25% MFU on this GPU), that is \(1.28 \times 10^{5}\) s ≈ **35.5 hours**.

The compute to build something genuinely interesting has been sitting idle the entire time.

---

## 6. Researcher's opinion

If this were submitted for review, the verdict would be **reject, with one salvageable contribution**.

- **The claim "≤5M-parameter selective retriever with calibrated refusal" is defensible** — but it is a *retrieval engineering* result, not a language modelling result, and the retrieval set has 18 entries, so the result is not statistically meaningful either.
- **The negative-results discipline is publishable as methodology.** A paper titled *"Thirty-seven waves of process improvement produced zero model improvement: a case study in metric selection"* would be genuinely valuable and honest. That is a real contribution, and it is the only one here.
- **Everything else must be treated as scaffolding, not results.**

The good news is that the failure is *cleanly diagnosed and cheaply fixed*. Nothing about this project is hard. It is under-trained, mis-parameterized, and un-measured. All three are solved with known techniques, on hardware already present, in weeks rather than months.

The bad news is that the fix requires abandoning the wave machine entirely. It cannot be reformed, because its throughput is precisely what caused the problem.

---

## 7. Non-negotiable rules going forward

Derived directly from the failures above. These are enforced by [`docs/pipeline/`](pipeline/README.md).

| # | Rule | Prevents |
|---|---|---|
| R1 | **Held-out bits-per-byte is the primary metric.** Every stage reports it. No exceptions. | C3 |
| R2 | **No claim without a committed artifact** (`.json` with git hash, config hash, seed, wall time). Markdown is never evidence. | §2.7 |
| R3 | **Retrieval and generation are measured separately, always.** A lookup hit is never counted as model capability. | C4 |
| R4 | **Embedding parameters are reported separately from non-embedding parameters** in every model description. | C2 |
| R5 | **A stage that costs no FLOPs cannot be a research stage.** Documentation is overhead, not progress. | C5 |
| R6 | **One pipeline. No waves, no letters, no forever packs.** Stage advances only on a numeric gate. | C5 |
| R7 | **Negative results are promoted, not routed around.** A failed gate stops the pipeline until the cause is fixed. | C4 |

---

## 8. Where to go next

The redirect is specified in full under [`docs/pipeline/`](pipeline/README.md), with one file per stage.

The new objective, stated so it can be falsified:

> Train a **≤60M non-embedding-parameter** causal language model with a **32,768-token context window** that reaches a **measured held-out bits-per-byte competitive with models 10× its size**, runs at **≥100 tok/s on an RTX 4060 at 8k context**, and is trained **end to end on this single machine in under 72 hours**.

Along the way, the research programme investigates **quantum-inspired training methods** ([P13](pipeline/P13-quantum-inspired-training-lab.md)) and maintains a **catalogue of 100 theoretical architectures** ([`docs/hypotheses/`](hypotheses/README.md)) triaged by cost and falsifiability.

**Historical note for future agents:** waves W–BH and all pre-2026-07-30 wave documentation were **deleted from the working tree** and preserved in the git tag `legacy/waves-w-bh`. The tag exists for one purpose: so the numbers in this assessment remain independently checkable. Do not check it out to look for reusable code, do not cite its numbers as evidence, and do not resume the wave protocol.
