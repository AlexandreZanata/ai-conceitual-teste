# UC-001 — Run one generation (CLI)

| Field | Value |
|-------|-------|
| Actor | Researcher (CLI) |
| Goal | Evaluate entire population once and obtain metrics |
| Preconditions | Binary built; config JSON valid; RNG seed set |
| Related | [EXPERIMENTAL-DESIGN.md](../EXPERIMENTAL-DESIGN.md) T1 |

## Main flow

1. Researcher starts `evogen --config experiments/config_A_only_genetic.json --generations 1` (or config C).
2. System loads population and Environment stub (T1 stub in phase 03; full T1 in phase 04).
3. Each Agent responds to all stimuli; DirectLearner is a no-op until phase 04.
4. Recorder writes generation metrics to stdout and `results/metrics.jsonl`.
5. Process exits 0.

## Failures

| Case | Expected |
|------|----------|
| Missing config | Non-zero exit + clear error |
| Invalid seed / sizes | Reject before loop |

## Acceptance

GIVEN a valid condition-A or condition-C config  
WHEN one generation runs (`--generations 1`)  
THEN `fitness_mean` and `fitness_max` are logged (stdout + JSONL) and exit code is 0
