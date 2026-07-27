# SHIPKEEP — mode always visible (ask · apps · ship/demo)

## Ship/demo arms

| Arm | product_mode | modeui_line |
|-----|--------------|-------------|
| LOOKUP | **LOOKUP** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |
| PEAK | **PEAK** | `mode=PEAK · wall_ms=0.1400 · n_new=14 · raw=PEAK_FAST+GENBASE` |
| ABSTAIN | **ABSTAIN** | `mode=ABSTAIN · wall_ms=190.0423 · n_new=64 · raw=NO_ANSWER` |

## Apps ask

| app_id | product_mode | modeui_line |
|--------|--------------|-------------|
| known-ask | **LOOKUP** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |
| howto | **LOOKUP** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |
| long-doc | **LOOKUP** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |

Rule: every human-facing answer shows exactly one of `LOOKUP` · `PEAK` · `DECODE` · `ABSTAIN` — never unlabeled.

Charter paths: nano:z:ask, apps ask, ship/demo

## DECODE path probe (content law)

| Field | Value |
|-------|--------|
| product_mode | **ABSTAIN** |
| modeui_line | `mode=ABSTAIN · wall_ms=345.9698 · n_new=64 · raw=NO_ANSWER` |
| completion | `NO_ANSWER` |
| honest | **True** |

Rule: DECODE gibberish must ABSTAIN — never telemetry-only `content_ok`.
