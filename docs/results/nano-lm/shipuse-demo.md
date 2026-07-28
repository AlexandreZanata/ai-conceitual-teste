# SHIPUSE — mode always visible (ask · apps · ship/demo)

## Ship/demo arms

| Arm | product_mode | modeui_line |
|-----|--------------|-------------|
| LOOKUP | **LOOKUP** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |
| PEAK | **PEAK** | `mode=PEAK · wall_ms=0.1598 · n_new=14 · raw=PEAK_FAST+GENBASE` |
| ABSTAIN | **ABSTAIN** | `mode=ABSTAIN · wall_ms=480.2653 · n_new=64 · raw=NO_ANSWER` |

## Apps ask

| app_id | product_mode | modeui_line |
|--------|--------------|-------------|
| ? | **LOOKUP** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |
| ? | **ABSTAIN** | `mode=ABSTAIN · wall_ms=0.0000 · n_new=0 · raw=NO_ANSWER` |
| ? | **LOOKUP** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |
| ? | **ABSTAIN** | `mode=ABSTAIN · wall_ms=453.2908 · n_new=64 · raw=NO_ANSWER` |

Rule: every human-facing answer shows exactly one of `LOOKUP` · `PEAK` · `DECODE` · `ABSTAIN` — never unlabeled.

Charter paths: nano:z:ask, apps ask, ship/demo
