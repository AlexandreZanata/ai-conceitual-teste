# SHIPDEMO — mode always visible (incl. ABSTAIN)

| Arm | product_mode | modeui_line |
|-----|--------------|-------------|
| LOOKUP | **LOOKUP** | `mode=LOOKUP · wall_ms=0.0000 · n_new=0 · raw=WRAP_LOOKUP` |
| PEAK | **PEAK** | `mode=PEAK · wall_ms=0.0238 · n_new=3 · raw=PEAK_FAST+GENBASE` |
| DECODE | **DECODE** | `mode=DECODE · wall_ms=11.4219 · n_new=8 · raw=QT+EARLY n=1` |
| ABSTAIN | **ABSTAIN** | `mode=ABSTAIN · wall_ms=11.4055 · n_new=8 · raw=NO_ANSWER` |

Rule: every answer shows exactly one of `LOOKUP` · `PEAK` · `DECODE` · `ABSTAIN` — never unlabeled.
