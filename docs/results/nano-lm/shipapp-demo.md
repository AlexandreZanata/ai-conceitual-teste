# SHIPAPP — mode always visible (ask · apps · ship/demo)

## Ship/demo arms

| Arm | product_mode | modeui_line |
|-----|--------------|-------------|
| LOOKUP | **LOOKUP** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |
| PEAK | **PEAK** | `mode=PEAK · wall_ms=0.0281 · n_new=3 · raw=PEAK_FAST+GENBASE` |
| DECODE | **DECODE** | `mode=DECODE · wall_ms=213.9937 · n_new=8 · raw=QT+EARLY n=1` |
| ABSTAIN | **ABSTAIN** | `mode=ABSTAIN · wall_ms=399.1223 · n_new=64 · raw=NO_ANSWER` |

## Apps ask

| app_id | product_mode | modeui_line |
|--------|--------------|-------------|
| known-ask | **LOOKUP** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |
| howto | **LOOKUP** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |
| long-doc | **LOOKUP** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |

Rule: every human-facing answer shows exactly one of `LOOKUP` · `PEAK` · `DECODE` · `ABSTAIN` — never unlabeled.

Charter paths: nano:z:ask, apps ask, ship/demo
