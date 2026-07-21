#include "core/generation_loop.hpp"

#include "core/rng.hpp"

#include <iostream>

namespace evogen {

namespace {

void evaluate_agent(Agent& agent, Environment& env, bool /*direct*/) {
  agent.reset_fitness();
  for (const auto& stimulus : env.episode()) {
    const float response = agent.respond(stimulus);
    const float reward = env.evaluate(response, stimulus);
    // Phase 03: DirectLearner disabled (condition A path / no-op).
    agent.add_reward(reward);
  }
}

}  // namespace

RunResult run_generations(Population& population, Environment& env,
                          const ExperimentConfig& cfg, Recorder& recorder,
                          int generations) {
  Rng rng(cfg.seed);
  RunResult result;
  const int n = generations < 0 ? cfg.max_generations : generations;
  for (int gen = 0; gen < n; ++gen) {
    for (Agent& agent : population.agents()) {
      evaluate_agent(agent, env, cfg.enable_direct_learning);
    }
    result.last =
        compute_metrics(gen, cfg.seed, cfg.condition, population.agents());
    recorder.log_generation(result.last);
    std::cout << "generation=" << result.last.generation
              << " fitness_mean=" << result.last.fitness_mean
              << " fitness_max=" << result.last.fitness_max << '\n';
    population.evolve(cfg, rng);
    result.generations_run = gen + 1;
  }
  return result;
}

}  // namespace evogen
