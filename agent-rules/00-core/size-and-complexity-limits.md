---
id: core.size-complexity
triggers:
  - size
  - complexity
  - cyclomatic
  - function
  - file
  - lint
  - typecheck
  - lines
alwaysApply: false
---
# Size and Complexity Limits

> This repo **waives** file ≤200 and function ≤80 line caps.  
> **Cyclomatic ≤ 10 per function** remains a hard gate.

## Hard caps

| Scope | Cap |
|-------|-----|
| Function / method lines | **waived** |
| File / module lines | **waived** |
| Cyclomatic complexity | **10 per function** |

## Verification

1. Run `npm run verify` (cyclomatic + lint + system).
2. Refactor when cyclomatic reaches **8** — **10** is the ceiling.
3. Prefer readable structure; do not split only to hit a line quota.

## Agent NEVER

- Submit cyclomatic > 10 without explicit user waiver.
- Add nested branches to hide complexity — extract instead.
