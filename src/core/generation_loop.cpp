#include "core/generation_loop.hpp"

#include "core/direct_learning.hpp"

#include <iostream>

namespace evogen {

namespace {

void learn_step(Agent& agent, Environment& env,
                const std::vector<float>& stimulus, float response,
                bool enable_direct) {
  if (!enable_direct) {
    return;
  }
  const float error = env.target_of(stimulus) - response;
  apply_direct_learn(agent.phenotype(), agent.genotype().learning_rate,
                     stimulus, error);
}

void evaluate_agent_batch(Agent& agent, Environment& env, bool enable_direct,
                          bool reset_phenotype) {
  if (reset_phenotype) {
    agent.begin_lifetime();
  }
  agent.reset_fitness();
  for (const auto& stimulus : env.episode()) {
    const float response = agent.respond(stimulus);
    const float reward = env.evaluate(response, stimulus);
    learn_step(agent, env, stimulus, response, enable_direct);
    agent.add_reward(reward);
  }
}

void evaluate_agent_interactive(Agent& agent, Environment& env,
                                bool enable_direct, bool reset_phenotype,
                                std::uint64_t episode_seed) {
  if (reset_phenotype) {
    agent.begin_lifetime();
  }
  agent.reset_fitness();
  env.reset_episode(episode_seed);
  while (!env.episode_done()) {
    const std::vector<float> stimulus = env.observe();
    const float response = agent.respond(stimulus);
    const float reward = env.step(response);
    learn_step(agent, env, stimulus, response, enable_direct);
    agent.add_reward(reward);
  }
}

}  // namespace

GenerationMetrics step_generation(Population& population, Environment& env,
                                  const ExperimentConfig& cfg, Rng& rng,
                                  int generation) {
  const bool reset_phenotype =
      cfg.enable_genetic_reproduction || generation == 0;
  std::size_t alive = 0;
  std::size_t agent_i = 0;
  for (Agent& agent : population.agents()) {
    if (env.interactive()) {
      const std::uint64_t ep_seed =
          cfg.seed + static_cast<std::uint64_t>(generation) * 10007ULL +
          static_cast<std::uint64_t>(agent_i) * 97ULL;
      evaluate_agent_interactive(agent, env, cfg.enable_direct_learning,
                                 reset_phenotype, ep_seed);
      if (env.agent_alive()) {
        ++alive;
      }
    } else {
      evaluate_agent_batch(agent, env, cfg.enable_direct_learning,
                           reset_phenotype);
      ++alive;
    }
    ++agent_i;
  }
  GenerationMetrics metrics =
      compute_metrics(generation, cfg.seed, cfg.condition, population.agents());
  metrics.alive_mean =
      static_cast<float>(alive) / static_cast<float>(population.size());
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
              << " alive_mean=" << result.last.alive_mean
              << " learning_rate_mean=" << result.last.learning_rate_mean
              << '\n';
    result.generations_run = gen + 1;
  }
  return result;
}

}  // namespace evogen
