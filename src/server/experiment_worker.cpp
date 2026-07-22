#include "server/experiment_controller.hpp"

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
          {"alive_mean", m.alive_mean}};
}

}  // namespace

void ExperimentController::run_worker(ExperimentConfig cfg, std::string id) {
  Rng rng(cfg.seed);
  auto population = Population::create_random(cfg, rng);
  auto env = make_environment(cfg);
  Recorder recorder(results_dir_);
  for (int gen = 0; gen < cfg.max_generations; ++gen) {
    {
      std::unique_lock<std::mutex> lock(mu_);
      wait_if_paused(lock);
      if (stop_requested_) {
        status_ = ExperimentStatus::Stopped;
        return;
      }
    }
    const GenerationMetrics metrics =
        step_generation(population, *env, cfg, rng, gen);
    recorder.log_generation(metrics);
    hub_.publish(metrics_to_ws(id, metrics).dump());
    {
      std::lock_guard<std::mutex> lock(mu_);
      latest_ = metrics;
      current_generation_ = gen;
      if (stop_requested_) {
        status_ = ExperimentStatus::Stopped;
        return;
      }
    }
    if (cfg.generation_delay_ms > 0) {
      std::this_thread::sleep_for(
          std::chrono::milliseconds(cfg.generation_delay_ms));
    }
  }
  std::lock_guard<std::mutex> lock(mu_);
  if (!stop_requested_) {
    status_ = ExperimentStatus::Completed;
  }
}

}  // namespace evogen
