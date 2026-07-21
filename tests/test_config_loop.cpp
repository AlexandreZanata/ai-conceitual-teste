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

  const auto dir =
      std::filesystem::temp_directory_path() / "evogen_test_results";
  std::filesystem::remove_all(dir);
  evogen::Rng rng(cfg.seed);
  auto pop = evogen::Population::create_random(cfg, rng);
  evogen::FunctionApproxEnv env;
  evogen::Recorder recorder(dir.string());
  const auto result = evogen::run_generations(pop, env, cfg, recorder, 1);
  REQUIRE(result.generations_run == 1);
  REQUIRE(std::filesystem::exists(dir / "metrics.jsonl"));
  std::ifstream in(dir / "metrics.jsonl");
  std::string line;
  REQUIRE(static_cast<bool>(std::getline(in, line)));
  REQUIRE(line.find("fitness_mean") != std::string::npos);
  REQUIRE(line.find("fitness_max") != std::string::npos);
}
