# H-SYS smoke — CURL lo=8 × EARLY|POOL decode

Compose official train tip (CURL seq_lo=8) with EARLY / POOL decode search.
Kill arm if ≤ CURL default-decode or ≤ same tip on B2 (free lunch).

| family | mean teacher_lp | mean wall_ms | n |
|--------|-----------------|--------------|---|
| H-CURL | -16.7160 | 50 | 3 |
| H-EARLY | -16.5322 | 43 | 3 |
| H-POOL | -15.5365 | 44 | 3 |
| H-SYS-E | -16.8511 | 45 | 3 |
| H-SYS-P | -15.6814 | 99 | 3 |

### Arm decisions

- **H-SYS-E:** KILL (≤ CURL default decode)
- **H-SYS-P:** KILL (≤ H-POOL@B2)

**Decision: KILL (H-SYS-E: KILL (≤ CURL default decode); H-SYS-P: KILL (≤ H-POOL@B2))**

Commands: `npm run nano:sys` → `npm run nano:sys:report`.
