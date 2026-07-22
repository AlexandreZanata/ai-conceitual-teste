#include "core/generation_loop.hpp"

#include "core/budget.hpp"
#include "core/direct_learning.hpp"

#include <chrono>
#include <iostream>
#include <thread>

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

void maybe_drift(Environment& env, const ExperimentConfig& cfg, int gen,
                 RunResult& result) {
  if (!is_drift_generation(cfg, gen)) {
    return;
  }
  apply_arena_drift(env, cfg);
  result.drift_at_gen = gen;
}

nlohmann::json build_run_meta(const ExperimentConfig& cfg,
                              const RunResult& result, int gen_cap) {
  nlohmann::json meta = {{"technique", cfg.technique},
                         {"bench", cfg.bench},
                         {"seed", cfg.seed},
                         {"max_wall_ms", cfg.max_wall_ms},
                         {"max_generations", gen_cap},
                         {"stop_reason", result.stop_reason},
                         {"drift_at_gen", result.drift_at_gen},
                         {"generations_run", result.generations_run}};
  if (cfg.use_fitness_threshold) {
    meta["fitness_threshold"] = cfg.fitness_threshold;
  }
  return meta;
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
  metrics.technique = cfg.technique;
  population.evolve(cfg, rng);
  return metrics;
}

RunResult run_generations(Population& population, Environment& env,
                          const ExperimentConfig& cfg, Recorder& recorder,
                          int generations) {
  Rng rng(cfg.seed);
  RunResult result;
  const int n = generations < 0 ? cfg.max_generations : generations;
  const auto t0 = SteadyClock::now();
  for (int gen = 0; gen < n; ++gen) {
    const std::int64_t wall_before = wall_ms_since(t0);
    if (cfg.max_wall_ms > 0 && wall_before >= cfg.max_wall_ms) {
      result.stop_reason = "max_wall_ms";
      break;
    }
    maybe_drift(env, cfg, gen, result);
    result.last = step_generation(population, env, cfg, rng, gen);
    result.last.wall_ms_elapsed = wall_ms_since(t0);
    recorder.log_generation(result.last);
    std::cout << "generation=" << result.last.generation
              << " fitness_mean=" << result.last.fitness_mean
              << " fitness_max=" << result.last.fitness_max
              << " alive_mean=" << result.last.alive_mean
              << " learning_rate_mean=" << result.last.learning_rate_mean
              << " wall_ms_elapsed=" << result.last.wall_ms_elapsed << '\n';
    result.generations_run = gen + 1;
    const std::string reason = stop_reason_after_gen(
        cfg, result.last.fitness_mean, result.last.wall_ms_elapsed);
    if (!reason.empty()) {
      result.stop_reason = reason;
      break;
    }
    if (cfg.generation_delay_ms > 0) {
      std::this_thread::sleep_for(
          std::chrono::milliseconds(cfg.generation_delay_ms));
    }
  }
  recorder.write_meta(build_run_meta(cfg, result, n));
  return result;
}

}  // namespace evogen
