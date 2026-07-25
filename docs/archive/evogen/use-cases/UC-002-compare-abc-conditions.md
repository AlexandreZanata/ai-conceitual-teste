# UC-002 — Compare conditions A/B/C (function approx)

| Field | Value |
|-------|-------|
| Actor | Researcher |
| Goal | Measure whether full system (C) beats controls A and B on T1 |
| Preconditions | Phase 04+ core; configs A/B/C exist; fixed seed protocol |
| Related | [EXPERIMENTAL-DESIGN.md](../EXPERIMENTAL-DESIGN.md) |

## Main flow

1. Run condition A for N generations with seed S; store results.
2. Run condition B with same N, S, population size, genome size.
3. Run condition C likewise.
4. Compare generations-to-target and max fitness.

## Acceptance

GIVEN identical hyper-parameters except condition flags  
WHEN A, B, and C complete  
THEN results files are comparable and include seed + condition id
