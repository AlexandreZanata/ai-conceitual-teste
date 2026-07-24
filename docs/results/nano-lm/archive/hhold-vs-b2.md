# H-HOLD smoke vs B2 (integrity)

Holdout fitness: select on `fit_prompts.yaml` (`f01`,`f02`); claim eval on
`smoke_prompts.yaml` (`p01`,`p02`). Contract: `fit_prompt_ids` ∩ `eval_prompt_ids` = ∅.
Overfit kill if `train_fit − eval_lp` > 1.0 (any seed).

| family | mean teacher_lp | Δ vs B2 | overfit | n |
|--------|-----------------|---------|---------|---|
| B2 | −17.09 | — | — | 3 |
| H-FIT (leaky control) | −16.83 | +0.26 | — | 3 |
| H-HOLD | −16.71 | **+0.39** | no | 3 |

**Decision: PROMOTE** (tentative) — beats B2 on disjoint eval; no overfit flag.
Params ≤5M; `fit_prompt_ids`/`eval_prompt_ids` logged per seed.

**Formal reverse:** `docs/results/nano-lm/formal-hhold-vs-b2.md` — **KILL**
(overfit on 2/3 seeds; also Δ−1.84 vs B2). Smoke promote reversed.

Commands: `npm run nano:hold` → `npm run nano:formal:hhold` → report.  
Artifacts: `results/nano-lm/student-matrix/hold_smoke.json`; formal under
`results/nano-lm/formal-hhold-b2/`.
