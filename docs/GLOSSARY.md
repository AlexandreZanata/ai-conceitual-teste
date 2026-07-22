# Domain Glossary — EvoGen

> Ubiquitous language. Code, APIs, docs, and agents MUST use these terms exactly.
> Source plan: [plano-conceitual-evogen.md](plano-conceitual-evogen.md).

---

## Genome

**Definition:** Heritable parameter set of an agent: weight vector plus evolvable `mutation_rate` and `learning_rate`.  
**Not the same as:** Lifetime (phenotype) weight adjustments from direct learning (unless Lamarckian mode is enabled).  
**Code name:** `Genome`

---

## Agent

**Definition:** Individual that holds a heritable `Genome` (genotype) plus phenotype weights adapted by direct learning during its lifetime; accumulates fitness.  
**Not the same as:** Coding agent (LLM). In this repo, “agent” in domain code always means an evolutionary individual.  
**Code name:** `Agent`

---

## Population

**Definition:** Current set of agents in one generation; subject to selection, crossover, and mutation.  
**Code name:** `Population`

---

## Environment

**Definition:** Task that emits stimuli and returns rewards / evaluation for agent responses. May be batch (T1 function approx) or interactive (T2 Trait Forge Arena).  
**Not the same as:** Host OS environment variables.  
**Code name:** `Environment`

---

## Trait Forge Arena

**Definition:** T2 survival grid world: rules (bounds, drain, death) + variables (food/hazard density, ticks); species develops via selection/learning.  
**Code name:** `SurvivalArenaEnv`

---

## Fitness

**Definition:** Scalar accumulated during an agent’s lifetime from environment rewards; used by selection.  
**Code name:** `fitness`

---

## Direct Learning

**Definition:** Intra-lifetime local weight update after each response (e.g. Hebbian / one-step local gradient).  
**Not the same as:** Genetic mutation between generations.  
**Code name:** `DirectLearner`

---

## Selection

**Definition:** Operator that chooses parents for the next generation from fitness (tournament, roulette, elitism).  
**Code name:** `SelectionOperator`

---

## Mutation

**Definition:** Stochastic perturbation of inherited genome parameters (typically Gaussian). Rate may be read from the genome.  
**Code name:** `MutationOperator`

---

## Crossover

**Definition:** Recombination of two parent genomes into offspring (uniform or single-point).  
**Code name:** `crossover`

---

## Generation

**Definition:** One full evaluate-all-agents cycle followed by selection/reproduction (except condition B).  
**Code name:** `Generation`

---

## Baldwin Effect

**Definition:** Research phenomenon where lifetime learning guides or accelerates genetic evolution; measurable if evolved `learning_rate` falls as good behavior migrates into the genome.  
**Code name:** documented metric, not a type

---

## Inheritance Mode

**Definition:** Experimental switch: `Darwinian` (lifetime updates not inherited) vs `Lamarckian` (partial inheritance of lifetime updates).  
**Enum values:** `Darwinian`, `Lamarckian`  
**Code name:** `InheritanceMode`

---

## Experiment Condition

**Definition:** Controlled setup for comparison.  
**Enum values:** `A` (genetic only), `B` (direct only), `C` (full system)  
**Code name:** `ExperimentCondition`

---

## Recorder

**Definition:** Component that logs per-generation metrics (mean/max fitness, diversity) for the web UI and results files.  
**Code name:** `Recorder`
