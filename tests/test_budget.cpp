#include <catch2/catch_test_macros.hpp>

#include "core/budget.hpp"
#include "core/experiment_config.hpp"
#include "core/generation_loop.hpp"
#include "core/population.hpp"
#include "core/recorder.hpp"
#include "core/rng.hpp"
#include "environments/function_approx_env.hpp"
#include "environments/survival_arena_env.hpp"

#include <filesystem>
#include <fstream>
#include <nlohmann/json.hpp>
#include <stdexcept>
#include <string>

namespace {

evogen::ExperimentConfig tiny_t1() {
  evogen::ExperimentConfig cfg;
  cfg.name = "budget_unit";
  cfg.condition = "A";
  cfg.population_size = 4;
  cfg.genome_size = 4;
  cfg.seed = 1;
  cfg.max_generations = 50;
  cfg.enable_direct_learning = false;
  cfg.enable_genetic_reproduction = true;
  cfg.elite_count = 1;
  cfg.function_task = "xor";
  cfg.episode_length = 4;
  return cfg;
}

}  // namespace

// Contract: EXPERIMENTAL-DESIGN timed budgets — stop on τ
TEST_CASE("given_fitness_threshold_when_met_then_stop_reason_threshold",
          "[budget]") {
  auto cfg = tiny_t1();
  cfg.use_fitness_threshold = true;
  cfg.fitness_threshold = -1.0e9f;
  cfg.max_generations = 20;
  const auto dir =
      std::filesystem::temp_directory_path() / "evogen_budget_tau";
  std::filesystem::remove_all(dir);
  evogen::Rng rng(cfg.seed);
  auto pop = evogen::Population::create_random(cfg, rng);
  evogen::FunctionApproxEnv env(cfg.function_task, cfg.episode_length);
  evogen::Recorder recorder(dir.string());
  const auto result = evogen::run_generations(pop, env, cfg, recorder, -1);
  REQUIRE(result.stop_reason == "fitness_threshold");
  REQUIRE(result.generations_run == 1);
  REQUIRE(std::filesystem::exists(dir / "meta.json"));
  const auto meta = nlohmann::json::parse(std::ifstream(dir / "meta.json"));
  REQUIRE(meta.at("stop_reason") == "fitness_threshold");
  REQUIRE(meta.at("fitness_threshold").get<float>() == cfg.fitness_threshold);
}

// Contract: stop when generation budget exhausted
TEST_CASE("given_max_generations_when_exhausted_then_stop_reason_gens",
          "[budget]") {
  auto cfg = tiny_t1();
  cfg.max_generations = 3;
  const auto dir =
      std::filesystem::temp_directory_path() / "evogen_budget_gens";
  std::filesystem::remove_all(dir);
  evogen::Rng rng(cfg.seed);
  auto pop = evogen::Population::create_random(cfg, rng);
  evogen::FunctionApproxEnv env(cfg.function_task, cfg.episode_length);
  evogen::Recorder recorder(dir.string());
  const auto result = evogen::run_generations(pop, env, cfg, recorder, -1);
  REQUIRE(result.stop_reason == "max_generations");
  REQUIRE(result.generations_run == 3);
}

// Contract: stop when wall-clock budget exhausted
TEST_CASE("given_max_wall_ms_when_elapsed_then_stop_reason_wall", "[budget]") {
  auto cfg = tiny_t1();
  cfg.max_generations = 100;
  cfg.max_wall_ms = 40;
  cfg.generation_delay_ms = 30;
  const auto dir =
      std::filesystem::temp_directory_path() / "evogen_budget_wall";
  std::filesystem::remove_all(dir);
  evogen::Rng rng(cfg.seed);
  auto pop = evogen::Population::create_random(cfg, rng);
  evogen::FunctionApproxEnv env(cfg.function_task, cfg.episode_length);
  evogen::Recorder recorder(dir.string());
  const auto result = evogen::run_generations(pop, env, cfg, recorder, -1);
  REQUIRE(result.stop_reason == "max_wall_ms");
  REQUIRE(result.generations_run >= 1);
  REQUIRE(result.generations_run < 100);
  const auto meta = nlohmann::json::parse(std::ifstream(dir / "meta.json"));
  REQUIRE(meta.at("stop_reason") == "max_wall_ms");
}

// Contract: TB-DRIFT flip at 50% budget logs drift_at_gen
TEST_CASE("given_drift_enabled_when_mid_budget_then_logs_drift_at_gen",
          "[budget][drift]") {
  evogen::ExperimentConfig cfg;
  cfg.environment = "survival_arena";
  cfg.condition = "A";
  cfg.population_size = 4;
  cfg.genome_size = 8;
  cfg.seed = 3;
  cfg.max_generations = 4;
  cfg.enable_drift = true;
  cfg.drift_at_fraction = 0.5f;
  cfg.post_drift_hazard_rate = 0.5f;
  cfg.grid_w = 8;
  cfg.grid_h = 8;
  cfg.food_density = 0.1f;
  cfg.energy_drain = 0.05f;
  cfg.hazard_rate = 0.05f;
  cfg.start_energy = 1.0f;
  cfg.episode_ticks = 8;
  const auto dir =
      std::filesystem::temp_directory_path() / "evogen_budget_drift";
  std::filesystem::remove_all(dir);
  evogen::Rng rng(cfg.seed);
  auto pop = evogen::Population::create_random(cfg, rng);
  evogen::SurvivalArenaEnv env(cfg.grid_w, cfg.grid_h, cfg.food_density,
                               cfg.energy_drain, cfg.hazard_rate,
                               cfg.start_energy, cfg.episode_ticks);
  REQUIRE(env.season() == 0.0f);
  evogen::Recorder recorder(dir.string());
  const auto result = evogen::run_generations(pop, env, cfg, recorder, -1);
  REQUIRE(result.drift_at_gen == 2);
  REQUIRE(env.season() == 1.0f);
  REQUIRE(env.hazard_rate() == 0.5f);
  const auto meta = nlohmann::json::parse(std::ifstream(dir / "meta.json"));
  REQUIRE(meta.at("drift_at_gen") == 2);
}

// Contract: bench JSON exposes budget fields
TEST_CASE("given_tb30_config_when_load_then_budget_fields_ok",
          "[budget][config]") {
  const auto cfg = evogen::load_experiment_config(
      "experiments/survival/benches/TB-30.json");
  REQUIRE(cfg.bench == "TB-30");
  REQUIRE(cfg.max_wall_ms == 30000);
  REQUIRE(cfg.max_generations == 40);
  REQUIRE(cfg.use_fitness_threshold);
  REQUIRE(cfg.fitness_threshold == -0.40f);
}

TEST_CASE("given_negative_max_wall_ms_when_validate_then_throws", "[budget]") {
  evogen::ExperimentConfig cfg;
  cfg.max_wall_ms = -1;
  REQUIRE_THROWS_AS(evogen::validate_experiment_config(cfg),
                    std::invalid_argument);
}
