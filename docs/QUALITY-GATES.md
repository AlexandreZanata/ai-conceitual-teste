# Quality gates (Lefthook)

Commits and pushes are blocked until all gates pass — including local commits.

Source of truth: `agent-rules/00-core/size-and-complexity-limits.md`.

## Caps

| Metric | Hard cap |
|--------|----------|
| File / module lines | **waived** |
| Function / method lines | **waived** |
| Cyclomatic complexity | ≤ 10 |
| Lint | 0 errors, 0 warnings |
| System / compile | 0 errors (when typecheck/build exists) |

## Commands

```bash
npm install              # installs Lefthook + git hooks (prepare)
npx lefthook install     # re-wire hooks if needed
npm run verify           # full gate
npm run check:size       # cyclomatic (line caps waived)
npm run check:lint       # lint only
npm run check:system     # compile/check only
```

## Implementation

| Piece | Path |
|-------|------|
| Hook config | `lefthook.yml` |
| Orchestrator | `scripts/check-quality.sh` |
| Size/complexity | `scripts/check_size_complexity.py` |
| Lint | `scripts/check-lint.sh` |
| System | `scripts/check-system.sh` |

When JS/TS sources appear, add an ESLint script named `lint` with `--max-warnings 0`.  
When a TypeScript project exists, add a `typecheck` script (preferred) or `build`.
