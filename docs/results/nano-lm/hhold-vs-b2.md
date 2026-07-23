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
Formal reverse-check on `eval_prompts.yaml` still required before claim
(smoke promotes have reversed before — e.g. H-SEL).

Integrity note: holdout did **not** erase the smoke edge vs B2, so H-FIT’s
smoke Δ is not explained by prompt leak alone at this budget. Still not a
formal claim.

Commands: `npm run nano:hold` → `npm run nano:matrix:report`.  
Artifacts: `results/nano-lm/student-matrix/hold_smoke.json`, `HHOLD_seed*_train.json`.
