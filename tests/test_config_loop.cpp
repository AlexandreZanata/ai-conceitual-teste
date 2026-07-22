#include <catch2/catch_test_macros.hpp>

#include "core/experiment_config.hpp"
#include "core/generation_loop.hpp"
#include "core/population.hpp"
#include "core/recorder.hpp"
#include "core/rng.hpp"
#include "environments/function_approx_env.hpp"

#include <filesystem>
#include <fstream>
#include <stdexcept>
#include <string>

TEST_CASE("load condition A config", "[config]") {
  const auto cfg = evogen::load_experiment_config(
      "experiments/config_A_only_genetic.json");
  REQUIRE(cfg.condition == "A");
  REQUIRE_FALSE(cfg.enable_direct_learning);
  REQUIRE(cfg.enable_genetic_reproduction);
  REQUIRE(cfg.population_size == 50);
  REQUIRE(cfg.seed == 42);
  REQUIRE(cfg.function_task == "xor");
}

TEST_CASE("reject invalid population_size", "[config]") {
  evogen::ExperimentConfig cfg;
  cfg.population_size = 0;
  REQUIRE_THROWS_AS(evogen::validate_experiment_config(cfg),
                    std::invalid_argument);
}

TEST_CASE("one generation loop logs metrics", "[loop]") {
  evogen::ExperimentConfig cfg;
  cfg.name = "unit";
  cfg.condition = "A";
  cfg.population_size = 8;
  cfg.genome_size = 8;
  cfg.seed = 42;
  cfg.max_generations = 1;
  cfg.enable_direct_learning = false;
  cfg.enable_genetic_reproduction = true;
  cfg.elite_count = 1;
  cfg.function_task = "xor";
  cfg.episode_length = 4;

  const auto dir =
      std::filesystem::temp_directory_path() / "evogen_test_results";
  std::filesystem::remove_all(dir);
  evogen::Rng rng(cfg.seed);
  auto pop = evogen::Population::create_random(cfg, rng);
  evogen::FunctionApproxEnv env(cfg.function_task, cfg.episode_length);
  evogen::Recorder recorder(dir.string());
  const auto result = evogen::run_generations(pop, env, cfg, recorder, 1);
  REQUIRE(result.generations_run == 1);
  REQUIRE(std::filesystem::exists(dir / "metrics.jsonl"));
  std::ifstream in(dir / "metrics.jsonl");
  std::string line;
  REQUIRE(static_cast<bool>(std::getline(in, line)));
  REQUIRE(line.find("fitness_mean") != std::string::npos);
  REQUIRE(line.find("learning_rate_mean") != std::string::npos);
}

TEST_CASE("condition B skips genetic reproduction", "[loop][B]") {
  evogen::ExperimentConfig cfg;
  cfg.condition = "B";
  cfg.population_size = 6;
  cfg.genome_size = 4;
  cfg.seed = 7;
  cfg.enable_direct_learning = true;
  cfg.enable_genetic_reproduction = false;
  cfg.initial_learning_rate = 0.05f;
  cfg.function_task = "xor";
  cfg.episode_length = 4;

  const auto dir =
      std::filesystem::temp_directory_path() / "evogen_test_b";
  std::filesystem::remove_all(dir);
  evogen::Rng rng(cfg.seed);
  auto pop = evogen::Population::create_random(cfg, rng);
  const auto first_w0 = pop.agents().front().genotype().weights[0];
  evogen::FunctionApproxEnv env(cfg.function_task, cfg.episode_length);
  evogen::Recorder recorder(dir.string());
  evogen::run_generations(pop, env, cfg, recorder, 2);
  REQUIRE(pop.agents().front().genotype().weights[0] == first_w0);
}
