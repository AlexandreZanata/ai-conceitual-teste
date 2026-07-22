#include "core/generation_loop.hpp"

#include "core/direct_learning.hpp"

#include <iostream>

namespace evogen {

namespace {

void evaluate_agent(Agent& agent, Environment& env, bool enable_direct,
                    bool reset_phenotype) {
  if (reset_phenotype) {
    agent.begin_lifetime();
  }
  agent.reset_fitness();
  for (const auto& stimulus : env.episode()) {
    const float response = agent.respond(stimulus);
    const float target = env.target_of(stimulus);
    const float reward = env.evaluate(response, stimulus);
    if (enable_direct) {
      const float error = target - response;
      apply_direct_learn(agent.phenotype(), agent.genotype().learning_rate,
                         stimulus, error);
    }
    agent.add_reward(reward);
  }
}

}  // namespace

GenerationMetrics step_generation(Population& population, Environment& env,
                                  const ExperimentConfig& cfg, Rng& rng,
                                  int generation) {
  // Condition B: keep phenotype across generations (online learning only).
  const bool reset_phenotype =
      cfg.enable_genetic_reproduction || generation == 0;
  for (Agent& agent : population.agents()) {
    evaluate_agent(agent, env, cfg.enable_direct_learning, reset_phenotype);
  }
  GenerationMetrics metrics =
      compute_metrics(generation, cfg.seed, cfg.condition, population.agents());
  population.evolve(cfg, rng);
  return metrics;
}

RunResult run_generations(Population& population, Environment& env,
                          const ExperimentConfig& cfg, Recorder& recorder,
                          int generations) {
  Rng rng(cfg.seed);
  RunResult result;
  const int n = generations < 0 ? cfg.max_generations : generations;
  for (int gen = 0; gen < n; ++gen) {
    result.last = step_generation(population, env, cfg, rng, gen);
    recorder.log_generation(result.last);
    std::cout << "generation=" << result.last.generation
              << " fitness_mean=" << result.last.fitness_mean
              << " fitness_max=" << result.last.fitness_max
              << " learning_rate_mean=" << result.last.learning_rate_mean
              << '\n';
    result.generations_run = gen + 1;
  }
  return result;
}

}  // namespace evogen
