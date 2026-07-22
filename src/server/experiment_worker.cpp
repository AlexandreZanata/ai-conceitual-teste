#include "server/experiment_controller.hpp"

#include "core/budget.hpp"
#include "core/generation_loop.hpp"
#include "core/population.hpp"
#include "core/rng.hpp"
#include "environments/env_factory.hpp"

#include <chrono>
#include <thread>

namespace evogen {

namespace {

nlohmann::json metrics_to_ws(const std::string& id,
                             const GenerationMetrics& m) {
  return {{"type", "generation"},
          {"experiment_id", id},
          {"generation", m.generation},
          {"fitness_mean", m.fitness_mean},
          {"fitness_max", m.fitness_max},
          {"diversity_mean", m.diversity_mean},
          {"learning_rate_mean", m.learning_rate_mean},
          {"alive_mean", m.alive_mean},
          {"technique", m.technique},
          {"wall_ms_elapsed", m.wall_ms_elapsed}};
}

nlohmann::json run_meta(const ExperimentConfig& cfg, const RunResult& r) {
  nlohmann::json meta = {{"technique", cfg.technique},
                         {"bench", cfg.bench},
                         {"seed", cfg.seed},
                         {"max_wall_ms", cfg.max_wall_ms},
                         {"max_generations", cfg.max_generations},
                         {"stop_reason", r.stop_reason},
                         {"drift_at_gen", r.drift_at_gen},
                         {"generations_run", r.generations_run}};
  if (cfg.use_fitness_threshold) {
    meta["fitness_threshold"] = cfg.fitness_threshold;
  }
  return meta;
}

bool wall_budget_hit(const ExperimentConfig& cfg,
                     SteadyClock::time_point t0) {
  return cfg.max_wall_ms > 0 && wall_ms_since(t0) >= cfg.max_wall_ms;
}

void apply_drift_step(Environment& env, const ExperimentConfig& cfg, int gen,
                      RunResult& result) {
  if (!is_drift_generation(cfg, gen)) {
    return;
  }
  apply_arena_drift(env, cfg);
  result.drift_at_gen = gen;
}

}  // namespace

void ExperimentController::run_worker(ExperimentConfig cfg, std::string id) {
  Rng rng(cfg.seed);
  auto population = Population::create_random(cfg, rng);
  auto env = make_environment(cfg);
  Recorder recorder(results_dir_);
  RunResult result;
  const auto t0 = SteadyClock::now();
  for (int gen = 0; gen < cfg.max_generations; ++gen) {
    {
      std::unique_lock<std::mutex> lock(mu_);
      wait_if_paused(lock);
      if (stop_requested_) {
        result.stop_reason = "stopped";
        break;
      }
    }
    if (wall_budget_hit(cfg, t0)) {
      result.stop_reason = "max_wall_ms";
      break;
    }
    apply_drift_step(*env, cfg, gen, result);
    GenerationMetrics metrics =
        step_generation(population, *env, cfg, rng, gen);
    metrics.wall_ms_elapsed = wall_ms_since(t0);
    result.last = metrics;
    result.generations_run = gen + 1;
    recorder.log_generation(metrics);
    hub_.publish(metrics_to_ws(id, metrics).dump());
    {
      std::lock_guard<std::mutex> lock(mu_);
      latest_ = metrics;
      current_generation_ = gen;
      if (stop_requested_) {
        result.stop_reason = "stopped";
        break;
      }
    }
    const std::string reason = stop_reason_after_gen(
        cfg, metrics.fitness_mean, metrics.wall_ms_elapsed);
    if (!reason.empty()) {
      result.stop_reason = reason;
      break;
    }
    if (cfg.generation_delay_ms > 0) {
      std::this_thread::sleep_for(
          std::chrono::milliseconds(cfg.generation_delay_ms));
    }
  }
  recorder.write_meta(run_meta(cfg, result));
  std::lock_guard<std::mutex> lock(mu_);
  status_ = (result.stop_reason == "stopped" || stop_requested_)
                ? ExperimentStatus::Stopped
                : ExperimentStatus::Completed;
}

}  // namespace evogen
