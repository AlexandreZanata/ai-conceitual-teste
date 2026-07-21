# Research Questions — EvoGen

Open questions from the conceptual plan. Do not “resolve” in code without documenting the experimental answer.

| ID | Question | How we will test |
|----|----------|------------------|
| RQ1 | Should direct learning be purely Darwinian or partially Lamarckian? | `InheritanceMode` switch; compare fitness curves |
| RQ2 | Do evolvable `mutation_rate` and `learning_rate` converge to a stable meta-optimum or oscillate? | Time series of means ± variance per generation |
| RQ3 | In which environments (static vs concept drift) does C clearly beat A and B? | T1 vs T3 with same A/B/C protocol |
| RQ4 | Where are diminishing returns for population size vs compute under the lightness constraint? | Sweep population size; measure wall-clock to target fitness |

Related reading (cite in reports; verify URLs before publication):

- Baldwin effect — classic evolutionary computation literature (Hinton & Nowlan 1987 and surveys).  
- Genetic algorithms — Goldberg / Mitchell textbooks for operator baselines.  
- Hebbian learning — standard local update formulations for the DirectLearner.

Agents must not invent citations; store verified sources in the active phase `OFFICIAL-REFERENCE.md` under `.local/phases/` when implementing, and mirror lasting citations into `docs/` for phase 09.
