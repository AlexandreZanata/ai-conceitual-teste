# ADR notes — survival timed benchmarks (phase 09)

Architecture Decision Records for choices locked while building T2/T3 benches.

## ADR-1 — Discrete 5-way action set

| | |
|--|--|
| **Status** | Accepted (phase 06) |
| **Context** | Agents emit a scalar `response`; arena needs navigable moves. |
| **Decision** | Bin scalar into N / E / S / W / stay. |
| **Consequences** | Simple stimulus→action map; limits fine motor policies. Revisit only with contract + bench re-baseline. |

## ADR-2 — Fitness thresholds (τ)

| | |
|--|--|
| **Status** | Accepted (phase 08 calibration) |
| **Context** | Equal-budget success needs explicit τ per difficulty. |
| **Decision** | τ_mild=−0.40, τ_med=−0.60, τ_harsh=−0.68 from C/seed42 smoke peaks on mild/med/harsh knobs. |
| **Consequences** | TB-120 never hits τ in R=2 smoke — may need recalibration for discriminative harsh benches. |

## ADR-3 — Technique IDs

| | |
|--|--|
| **Status** | Accepted (phase 07) |
| **Context** | Comparable learning regimes for the report matrix. |
| **Decision** | R0 / A / B / C / C-L / A+ with `apply_technique_defaults` (see EXPERIMENTAL-DESIGN). |
| **Consequences** | Condition A/B/C still exist; technique overrides flags when set. |

## ADR-4 — Smoke vs full R

| | |
|--|--|
| **Status** | Accepted (phase 08/09) |
| **Context** | CI and narrative need a cheap protocol; science needs more seeds. |
| **Decision** | R=2 smoke for CI / this report; R=10 proposed for full claims. |
| **Consequences** | Report answers are tentative; do not publish without R=10 or equivalent. |
