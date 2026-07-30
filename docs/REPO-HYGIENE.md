# Repository hygiene — how to build this repo and keep it clean

> **The rule that explains every other rule on this page:**
> **Git history is permanent.** Deleting a file in a later commit does not remove it from history. Push a 200 MB checkpoint once and every clone, every CI run, and every contributor downloads it forever. There is no undo that does not rewrite history and break every existing clone.
>
> The only cheap moment to prevent that is **before the commit**. That is what this document and `scripts/check_repo_hygiene.py` exist for.

---

## 1. Current state — the numbers to defend

The reset on 2026-07-30 removed the failed programme's tree.

| Metric | Before | After | Cap |
|---|---:|---:|---:|
| Tracked files | 2,539 | **70** | **400** |
| npm scripts | 856 | **39** | **40** |
| Lines of Python | 341,926 | **289** | — |
| Markdown documents | 789 | **39** | — |
| Git pack size | 2.06 MiB | 4.85 MiB | **50 MiB** |
| `.git` on disk | 47 MB | **6.6 MB** | — |

Working-tree disk reclaimed: **5.4 GB** (`nano_lm/.venv` 5.1 GB, `build/` 250 MB, `results/` 28 MB) — all gitignored, all regenerable.

The git pack was **already clean** — no binary was ever committed, because `results/` and `*.pt` were gitignored from the start. That was the one thing the previous programme got right about repository management, and it is why this reset needed no history rewrite.

**Everything deleted is recoverable:**

```bash
git checkout legacy/waves-w-bh          # inspect the old tree
git show legacy/waves-w-bh:path/to/file # recover a single file
```

---

## 2. Creating the repository from scratch

If you are starting a fresh clone or a new remote.

### 2.1 Local

```bash
git init
git branch -M main
npm install            # installs lefthook and runs `prepare`
npx lefthook install   # installs the pre-commit / pre-push hooks
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
npm run verify         # must be green before the first commit
```

**`npx lefthook install` is not optional.** Without it the hygiene gate does not run, and the first accidental `git add .` after a training run will commit a checkpoint.

### 2.2 Remote

```bash
gh repo create n32 --private --source=. --remote=origin
git add -A
git commit -m "chore: initial N32 skeleton"
git push -u origin main
```

Start **private**. Make it public only after [P18](pipeline/P18-release-and-publication.md), when the model card, licences, and data provenance are complete. A repository that goes public with unclear data licensing cannot be made clean again.

### 2.3 Verify the remote is clean before the first push

```bash
git count-objects -vH        # size-pack should be < 5 MiB
git ls-files | wc -l         # should be < 400
npm run hygiene              # must exit 0
```

---

## 3. What lives where

The single most useful decision in an ML repository: **the repo is for things humans read and review. Everything a machine produces lives elsewhere.**

| Artifact | Size | Home | In git? |
|---|---:|---|:---:|
| Source code (`n32/`, `bench/`, `scripts/`) | KB | repo | **yes** |
| Stage specs, docs | KB | `docs/` | **yes** |
| Configs (`configs/*.yaml`) | KB | repo | **yes** |
| **Summary JSON** (metrics, gates, hashes) | <100 KB | `results/**/summary.json` | **yes — the exception** |
| Data manifest (URLs + SHA-256) | KB | `n32/data/sources.py` | **yes** |
| Raw + tokenized corpus | ~22 GB | `data/` | no — rebuild from manifest |
| Checkpoints | 13–200 MB | `runs/`, `artifacts/` | no — HuggingFace Hub |
| Released weights | 50–120 MB | **HuggingFace Hub** | no |
| Metric streams (`metrics.jsonl`) | 10–500 MB | `runs/` | no |
| Plots, heatmaps | MB | `results/` | no — regenerate |
| Python venv | 5.1 GB | `.venv/` | no |
| Scratch notes | KB | `.local/` | no |

### Why summary JSON is the one exception

Law **R2** requires that every claim point at a committed artifact carrying a git hash, config hash, seed, and wall time. That artifact must be **in the repository**, or the claim is unverifiable — which is exactly how the previous programme ended up with 251 reports citing `formal.json` files that do not exist.

So: **the small JSON that proves a gate passed is committed. The gigabytes it was computed from are not.** A summary JSON should be under 100 KB. If yours is larger, you are committing raw data, not a summary.

---

## 4. Never commit these

Each is blocked by `scripts/check_repo_hygiene.py`.

| Category | Examples | Why | Instead |
|---|---|---|---|
| **Model weights** | `.pt .pth .bin .safetensors .gguf .onnx .ckpt` | 13–200 MB each, changes every run, git cannot delta-compress binaries | HuggingFace Hub; commit the SHA-256 |
| **Datasets** | `data/`, `.parquet`, `.arrow`, `.npy` | Gigabytes, and often licence-encumbered | Commit the manifest with hashes |
| **Run outputs** | `runs/`, `metrics.jsonl`, checkpoints | Regenerable, huge, changes constantly | `runs/` is gitignored; promote a summary |
| **Environments** | `.venv/`, `node_modules/` | 5.1 GB and 14 MB here; platform-specific | `requirements.txt`, `package-lock.json` |
| **Secrets** | `.env`, `*.pem`, `*.key`, tokens | **Cannot be un-leaked.** Rotate immediately if pushed. | Environment variables, secret manager |
| **Caches** | `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, `wandb/` | Pure noise in diffs | gitignored |
| **Build output** | `build/`, `dist/`, `*.so`, `*.o` | Regenerable | gitignored |
| **Notebook outputs** | `.ipynb` with cell output | Embeds images and data as base64; destroys diffs | `nbstripout` before committing |
| **Anything >1 MB** | — | Hard block | Decide explicitly; document why |

---

## 5. The enforcement — three layers

### Layer 1 — `.gitignore`
Prevents accidental `git add .`. Broad and commented. **Read it before adding a new output directory**; if your stage writes somewhere new, add it there first.

One trap worth knowing, because it silently breaks the summary-JSON exception: **git never descends into an ignored directory**, so a negation for a nested file can never match. `results/*` followed by `!results/**/summary.json` looks correct and does nothing. Directories must be re-admitted first:

```gitignore
results/**
!results/**/          # re-admit directories so git descends into them
!results/**/summary.json
```

Verify any exception you add, rather than assuming it works:

```bash
git check-ignore -v results/data/summary.json   # should print nothing, or exit 1
```

### Layer 2 — pre-commit hook (`lefthook.yml`)
Runs `check_repo_hygiene.py --staged` plus the full quality gate on every commit, including local ones. Blocks:

- binary extensions, secret filenames, files >1 MB
- files inside `data/`, `runs/`, `artifacts/`, `node_modules/`, `.local/`
- tracked-file count >400, npm scripts >40

### Layer 3 — pre-push hook
Runs the gate across the whole tree. Last check before anything becomes public.

### Bypassing

```bash
git commit --no-verify    # DO NOT
```

If the gate blocks you, it is almost certainly right. The one legitimate case — a genuinely necessary file over 1 MB — is handled by raising `MAX_FILE_BYTES` in a commit that explains why, so the decision is reviewable. Silently bypassing leaves no record.

---

## 6. Commit and branch model

Deliberately minimal. Branch complexity is its own kind of pollution.

### Branches

| Branch | Purpose |
|---|---|
| `main` | Always green. Every commit passes `npm run verify`. |
| `stage/PXX-name` | One branch per pipeline stage. Merged when the gate passes. |
| `exp/short-name` | Throwaway experiments. **Delete after merge or abandonment.** |

No `develop`, no release branches, no long-lived forks. One pipeline, one line of work — law **R6**.

### Commits

Conventional Commits, with the stage in the scope:

```
feat(P04): implement GQA attention with sliding window
fix(P05): restore RNG state on checkpoint resume
docs(P07): record scaling law fit and validation
chore: bump ruff to 0.7.2
```

| Rule | Reason |
|---|---|
| One logical change per commit | Reviewable, revertable |
| Subject ≤72 characters, imperative | Readable `git log --oneline` |
| Reference the stage | Ties every change to a spec |
| Never commit a broken `main` | The gate enforces it |
| No "wip", "fix", "asdf" | 564 commits of noise is its own archaeology problem |

### Tags

```
legacy/waves-w-bh    # frozen pre-reset state
stage/P07-complete   # each passed gate
v0.1.0               # released models
```

---

## 7. If something bad gets in anyway

Act fast. The cost grows with every clone and every downstream fork.

### Not yet pushed

```bash
git reset --soft HEAD~1     # undo the commit, keep the file on disk
echo "path/to/file" >> .gitignore
git commit -m "chore: exclude regenerable artifact"
```

### Already pushed

```bash
pip install git-filter-repo
git filter-repo --path path/to/big/file --invert-paths
git push --force-with-lease origin main
```

**This rewrites history.** Every collaborator must re-clone; existing clones and forks break. Coordinate before doing it, and never force-push `main` without telling everyone.

### A secret was pushed

**Rewriting history is not enough — assume the secret is compromised.**

1. **Rotate the credential immediately.** GitHub caches blobs; forks retain them; scrapers watch public pushes within seconds.
2. Then rewrite history with `git filter-repo`.
3. Then audit for unauthorized use.

Order matters. Rotation first, always.

---

## 8. Routine maintenance

```bash
# Monthly, or after any large deletion — compacts loose objects
git gc --aggressive --prune=now

# Audit what is actually taking space in history
git count-objects -vH
git rev-list --objects --all \
  | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' \
  | awk '/^blob/ {print $3, $4}' | sort -rn | head -20

# Confirm hygiene across the whole tree
npm run hygiene
```

The `rev-list` command is the one to run if the repo ever feels slow: it lists the largest blobs **in history**, including ones already deleted from the working tree.

---

## 9. Daily loop for an agent

Full protocol in [P19](pipeline/P19-agent-operating-protocol.md). The hygiene-relevant part:

```bash
# 1. Where are we?
ls docs/pipeline/results/

# 2. Work on a stage branch
git checkout -b stage/P02-data-foundation

# 3. Heavy output goes to gitignored directories
#    data/  runs/  artifacts/  results/  .local/

# 4. Promote ONLY the small summary
cp runs/P02/stats.json results/data/corpus_stats.json   # < 100 KB

# 5. Commit — the hook checks before anything becomes permanent
git add -A && git commit -m "feat(P02): 4.1B deduplicated tokens with provenance"

# 6. Gate passed? Write the one-page result and merge.
```

**The discipline in one sentence:** write big things to gitignored directories, promote only the small JSON that proves the gate passed, and never bypass the hook.

---

## 10. Why this matters here specifically

The previous programme did not fail because of repository bloat — its git pack stayed small. It failed for the reasons in [`ASSESSMENT-2026-07-30.md`](ASSESSMENT-2026-07-30.md).

But the bloat was the **visible symptom** of the same cause. 856 npm scripts, 1,506 Python files, and 573 wave reports were produced because writing files felt like progress. The caps in `check_repo_hygiene.py` — 400 files, 40 scripts — are not storage limits. They are a **forcing function against mistaking output for results**, and they will start failing long before disk space does.

If you find yourself needing to raise a cap, that is the signal to stop and ask whether the work is real — not to raise the cap.
