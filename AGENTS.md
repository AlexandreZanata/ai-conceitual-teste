# AGENTS.md — N32

> **Read this, then [`docs/pipeline/P19-agent-operating-protocol.md`](docs/pipeline/P19-agent-operating-protocol.md). Then stop reading and start working.**

**Project:** `N32` — a ≤60M non-embedding-parameter, 32k-context causal language model, trained end to end on one RTX 4060 in under 72 hours.
**Language:** 100% English for code, comments, commits, documents, and technical output.
**Status:** redirected 2026-07-30. Waves W–BH are frozen. The wave protocol is retired permanently.

---

## Where you are

This project already failed once. Not from lack of effort — 341,926 lines of Python, 856 npm scripts, 564 commits, 37 "waves" — but because **none of it was ever checked against a number that could go down**. Held-out perplexity was never computed. The shipped product answered questions from an 18-row lookup table.

The full autopsy is [`docs/ASSESSMENT-2026-07-30.md`](docs/ASSESSMENT-2026-07-30.md). Read it before you write code. The rules below exist because of specific things that happened, and they will look excessive until you know what they prevent.

---

## First five commands

```bash
ls docs/pipeline/results/     # highest-numbered file = last completed stage; the next one is your job
ls .local/                    # a PXX-* directory means that stage is in flight — read its LOG.md
npm run verify                # must be green before anything else
nvidia-smi                    # GPU must be free
git rev-parse --short HEAD    # record this in your stage log
```

---

## Required reading — and nothing else

| Order | Document | Lines |
|---|---|---:|
| 1 | [`docs/pipeline/P19-agent-operating-protocol.md`](docs/pipeline/P19-agent-operating-protocol.md) | ~250 |
| 2 | [`docs/ASSESSMENT-2026-07-30.md`](docs/ASSESSMENT-2026-07-30.md) | ~230 |
| 3 | [`docs/pipeline/README.md`](docs/pipeline/README.md) | ~200 |
| 4 | Your stage spec, `docs/pipeline/PXX-*.md` | ~200 |

**Do not read anything else.** The wave history — 573 reports and 341,926 lines — was deleted on 2026-07-30 and lives only in the git tag `legacy/waves-w-bh`. Do not check it out. Do not read stage specs other than your own. That material will exhaust your context and teach you the protocol that failed.

---

## The seven laws

| # | Law |
|---|---|
| R1 | Held-out **bits-per-byte** is the primary metric. Report it at every stage. Never report perplexity. |
| R2 | **No claim without a committed artifact** carrying git hash, config hash, seed, and wall time. Markdown is never evidence. |
| R3 | **Retrieval and generation are measured separately.** A lookup hit is never model capability. |
| R4 | **Embedding and non-embedding parameters** are always reported separately. |
| R5 | **A stage that costs no FLOPs is not a research stage.** Documents are overhead. |
| R6 | **One pipeline.** No waves, no letters, no forever packs, no new numbering schemes. |
| R7 | **A failed gate stops the pipeline.** Fix the cause, never the gate. |

---

## Never do these

Every item is something that actually happened here.

| Never | What it produced |
|---|---|
| Create a wave or letter-named phase | 37 waves, zero model improvement |
| Weaken a gate so a stage passes | Gates became strings to grep for in markdown |
| Report a metric that cannot fail | `L_eff` in the hundreds of thousands, on a model that could not use context |
| Serve an answer from a lookup table | An 18-row JSON file scored as 9.0/10 model quality |
| Cite an artifact without verifying it exists | 251 reports cite `formal.json`; **zero exist** |
| Leave a hypothesis in `HOLD` or `DEFER` | NANOGEN 1–18, never resolved |
| Write a document instead of running an experiment | 789 markdown files, one 120-step training run |
| Rename a failed approach and retry it | `NANOGEN` → `NANOGEN2` → … → `NANOGEN18` |
| Add an npm script no stage references | 856 scripts |

**Three failed attempts at a gate means stop and ask the user.** The previous programme's answer to a blocked path was to open a new wave, 37 times. That is the most expensive mistake available to you.

---

## Always do these

- Copy your stage's gate **verbatim** into `.local/PXX-*/LOG.md`. Paraphrasing is how gates get weakened.
- **Commit a numeric prediction before running.** It converts a fit into a test.
- Name the **classical control** for any novel method. Beating the naive baseline proves nothing.
- Report p50 and p99, never the mean. Report confidence intervals on every comparison.
- Write failures to [`docs/negative_results.md`](docs/negative_results.md). Failures are results.
- Run `npm run verify` before every commit. Cyclomatic complexity ≤10 per function.
- Write heavy output to `data/`, `runs/`, `artifacts/`, `results/` — all gitignored. Promote only the small summary JSON that proves the gate passed. **Never `git commit --no-verify`.**

---

## Repository map

| Path | Contents | Editable? |
|---|---|---|
| `docs/pipeline/` | 19 stage specs + protocol | Only with user approval |
| `docs/pipeline/results/` | The scoreboard | Append only |
| `docs/hypotheses/` | 100-architecture catalogue | Yes — keep the count at 100 |
| `docs/ASSESSMENT-2026-07-30.md` | Historical audit | **No.** Frozen. |
| `docs/negative_results.md` | Failures ledger | **Append always** |
| `docs/METRICS.md` | Metric definitions | Yes — the **only** place a metric is defined |
| `n32/` | Active source | Yes |
| `.local/` | Your scratch space; `STAGE-TEMPLATE/` is permanent | Yes |
| `docs/REPO-HYGIENE.md` | What may enter git | Read before committing anything unusual |
| `data/` `runs/` `artifacts/` `results/` | Heavy output, gitignored | Write freely; commit nothing |
| git tag `legacy/waves-w-bh` | Deleted history | **No.** Do not check out. |

---

## The whole job, in one paragraph

> Find the highest-numbered file in `docs/pipeline/results/`; the next stage is yours. Read the four documents above and nothing else. Copy your gate verbatim, commit a numeric prediction, run the experiment, and produce a JSON artifact with a git hash in it. If the gate passes, write a one-page result and advance. If it fails, fix the cause — never the gate. If it fails three times, stop and ask. Do not create waves, do not write summary documents, do not serve answers from lookup tables, and never report a number you cannot point at a file for.
