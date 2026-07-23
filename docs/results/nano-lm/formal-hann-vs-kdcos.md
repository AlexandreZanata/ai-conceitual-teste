# Formal H-ANN vs KD-cos (anneal LR+temp vs cosine LR)

Source: `results/nano-lm/formal-hann/formal.json`
Wall clock: 280.1s

Equal budget: KD 120 steps, seeds 0–2, eval_prompts (8).
Kill if H-ANN ≤ KD-cos on teacher_lp.

| family | mean teacher_lp | Δ vs KD-cos | Δ vs B2 | mean wall_ms | n |
|--------|-----------------|-------------|---------|--------------|---|
| B2 | -14.6480 | — | — | 63 | 3 |
| KD-cos | -16.3828 | — | -1.7348 | 63 | 3 |
| H-ANN | -16.2372 | +0.1456 | -1.5892 | 66 | 3 |

**Decision:** PROMOTE (beats cosine KD)

Smoke promote was tentative; this run is the claim-facing check.

Commands: `npm run nano:formal:hann` → `npm run nano:formal:hann:report`.
