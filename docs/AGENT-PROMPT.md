Continue the N32 research project. Do **exactly one stage**, then stop and report.

Use the maximum available hardware without crashing the machine.
Write everything — code, comments, docs, commits — in English.

---

## Step 1 — Find your task. Always do this first.

```bash
ls docs/pipeline/results/     # completed stages
ls .local/                    # a PXX-* folder means a stage is already in flight
```

- Result files are named `PXX.md`. The **highest number is the last completed stage**.
- **Your stage is the next number.** If only `README.md` is there, your stage is **P00**.
- If `.local/` already has a `PXX-*` folder, **continue that stage** instead of opening a new one.

## Step 2 — Read exactly four documents. No others.

1. `docs/pipeline/P19-agent-operating-protocol.md` — the rules
2. `docs/ASSESSMENT-2026-07-30.md` — why the rules exist
3. `docs/pipeline/README.md` — the objective and the stage index
4. `docs/pipeline/PXX-*.md` — **your stage only**

Do not read other stage specs. Do not check out the git tag `legacy/waves-w-bh`.
Reading more will exhaust your context and teach you the protocol that already failed here.

## Step 3 — Check the environment

```bash
npm run verify              # must pass. If it fails, fixing it IS your task.
nvidia-smi                  # GPU should be nearly free
git status                  # working tree should be clean
git rev-parse --short HEAD
```

## Step 4 — Open the stage

```bash
cp -r .local/STAGE-TEMPLATE .local/PXX-short-name
```

In `LOG.md`, before running anything:

- Copy the stage's **Gate** table **verbatim** from the spec. Do not reword it — paraphrasing is how gates get weakened.
- Write your **numeric prediction** for every gate metric. This is mandatory. A prediction written before the run turns a fit into a test.

## Step 5 — Implement

- Code goes only in `n32/` and `bench/`.
- Cyclomatic complexity **≤10 per function**.
- Every new behaviour gets an automated test that **fails if that behaviour breaks**. Never mirror the implementation inside the test, and never weaken an assertion to get green.
- Automated tests are not proof on their own — also run the thing manually and look at the actual output.
- Heavy output goes to `data/`, `runs/`, `artifacts/`, `results/`. All four are gitignored.
- **Hardware:** target ≤7 GB of the 8 GB VRAM, checkpoint at least every 15 minutes, and lower the batch size rather than risk an OOM that destroys hours of training. Prefer bf16 and gradient accumulation over a batch size that barely fits.

## Step 6 — Run, and produce real evidence

The run must write a **JSON artifact** containing `git_hash`, `config_hash`, `seed`, `wall_seconds`, and every gate metric.

**A number that is not inside a committed JSON file does not exist. Markdown is never evidence.**

Report these at every stage, even when they are not the gate:

| Report | Never report |
|---|---|
| Held-out **bits-per-byte** | Perplexity |
| **Embedding** and **non-embedding** params, separately | A single total parameter count |
| **p50 and p99** latency | The mean |
| Confidence intervals on every comparison | A bare difference between two runs |
| Retrieval and generation scored **separately** | One combined "quality" score |

## Step 7 — Decide against the gate

**Gate PASSED** → write `docs/pipeline/results/PXX.md`, **maximum one page**, using the template in P19 §7. Then delete `.local/PXX-*`.

**Gate FAILED** → the pipeline stops here. Do not advance. Do not weaken the gate.

1. Read the **Failure modes** table in your stage spec — your symptom is probably already listed.
2. Fix the cause and re-run.
3. If the approach itself is wrong, record a `KILL` in `docs/negative_results.md` and switch to the fallback the stage documents.
4. **After three failed attempts, STOP and ask me.** Do not switch to a different stage, do not invent a new approach, do not start a new numbering scheme.

## Step 8 — Validate, document, commit

```bash
npm run verify     # hygiene, complexity ≤10, lint 0/0, tests — all must pass
```

Update any documentation your change made inaccurate:

| If you | Update |
|---|---|
| Defined or changed a metric | `docs/METRICS.md` — the only place a metric is defined |
| Changed the model design | `docs/ARCHITECTURE.md` |
| Tested a quantum-inspired hypothesis | `docs/QUANTUM-LEDGER.md` |
| Tested a catalogue architecture | `docs/THEORY-LEDGER.md` |
| Killed anything | `docs/negative_results.md` |
| Passed a gate | `docs/CHECKPOINT.md` — tick the stage and fill in the numbers |

Commit locally with Conventional Commits and the stage in the scope. **Do not push.**

```bash
git commit -m "feat(P0X): <what was measured, including the number>"
```

## Never do these

Every one of them actually happened in this repository before the reset.

| Never | What it produced |
|---|---|
| Create a "wave", letter-named phase, or new numbering scheme | 37 waves, zero model improvement |
| Weaken a gate so the stage can pass | Gates became strings to grep for in markdown |
| Advance to the next stage with a failed gate | The entire previous failure |
| Report a metric that cannot fail | A context metric in the hundreds of thousands, on a model that could not use context |
| Serve an answer from a lookup table and call it model quality | An 18-row JSON file scored as 9.0/10 |
| Cite an artifact without checking it exists | 251 reports cite `formal.json`; zero exist |
| Leave a hypothesis in `HOLD` or `DEFER` | 18 iterations, never resolved |
| Write a summary document instead of running an experiment | 789 markdown files, one 120-step training run |
| Add an npm script no stage references | 856 scripts |
| Rename a failed approach and retry it | `NANOGEN` → `NANOGEN2` → … → `NANOGEN18` |
| `git commit --no-verify` | — |

## Finish by reporting exactly this

- **Stage:** PXX — title
- **Prediction vs measured:** a table, one row per gate metric
- **Verdict:** PASS or FAIL
- **Artifact:** path to the JSON, and its SHA-256
- **What surprised you:** anything that contradicted the prediction. If nothing did, say so — it usually means the stage measured less than it should have.
- **Next stage:** the number, and one sentence on what it needs to know.

Then stop. Do not begin the next stage.
