#include <catch2/catch_test_macros.hpp>
#include <catch2/matchers/catch_matchers_floating_point.hpp>

#include "core/experiment_config.hpp"
#include "core/generation_loop.hpp"
#include "core/population.hpp"
#include "core/recorder.hpp"
#include "core/rng.hpp"
#include "environments/env_factory.hpp"
#include "environments/survival_arena_env.hpp"

#include <filesystem>
#include <nlohmann/json.hpp>

using Catch::Matchers::WithinAbs;

namespace {

evogen::SurvivalArenaEnv make_arena() {
  return evogen::SurvivalArenaEnv(8, 8, 1.0f, 0.05f, 0.0f, 1.0f, 16);
}

}  // namespace

// Contract: SURVIVAL-GAME-PLAN — wall = no move
TEST_CASE("given_edge_when_move_out_then_position_unchanged", "[survival]") {
  auto env = make_arena();
  // Search a seed that places agent on western edge (x==0).
  bool found = false;
  for (std::uint64_t s = 0; s < 2000; ++s) {
    env.reset_episode(s);
    if (env.x() == 0) {
      const int y0 = env.y();
      env.step(-0.66f);  // W
      REQUIRE(env.x() == 0);
      REQUIRE(env.y() == y0);
      found = true;
      break;
    }
  }
  REQUIRE(found);
}

// Contract: food raises energy
TEST_CASE("given_adjacent_food_when_step_onto_then_energy_rises",
          "[survival]") {
  auto env = make_arena();
  env.reset_episode(1);
  const float before = env.energy();
  const auto stim = env.observe();
  // food_density=1 ⇒ adjacent food signals should be 1 after reset.
  REQUIRE(stim[1] + stim[2] + stim[3] + stim[4] > 0.0f);
  const float target = env.target_of(stim);
  env.step(target);
  REQUIRE(env.energy() > before - 0.05f);  // food gain dominates drain
  REQUIRE(env.energy() > before);
}

// Contract: energy ≤ 0 ends episode
TEST_CASE("given_low_energy_when_drain_then_episode_ends", "[survival]") {
  evogen::SurvivalArenaEnv env(4, 4, 0.0f, 0.5f, 0.0f, 0.4f, 10);
  env.reset_episode(7);
  REQUIRE_FALSE(env.episode_done());
  env.step(0.0f);
  REQUIRE(env.episode_done());
  REQUIRE_FALSE(env.agent_alive());
  REQUIRE_THAT(env.energy(), WithinAbs(0.0f, 1e-5f));
}

// Contract: deterministic under fixed seed
TEST_CASE("given_same_seed_when_reset_then_same_observe", "[survival]") {
  auto a = make_arena();
  auto b = make_arena();
  a.reset_episode(99);
  b.reset_episode(99);
  REQUIRE(a.observe() == b.observe());
  REQUIRE(a.x() == b.x());
  REQUIRE(a.y() == b.y());
}

// Contract: greedy target policy beats random responses (smoke)
TEST_CASE("given_food_rich_when_greedy_then_beats_random", "[survival]") {
  auto greedy = make_arena();
  auto random = make_arena();
  greedy.reset_episode(42);
  random.reset_episode(42);
  float g_sum = 0.0f;
  float r_sum = 0.0f;
  while (!greedy.episode_done()) {
    const auto s = greedy.observe();
    g_sum += greedy.step(greedy.target_of(s));
  }
  float fake = -1.5f;
  while (!random.episode_done()) {
    r_sum += random.step(fake);
    fake = -fake;
  }
  REQUIRE(g_sum > r_sum);
}

// Contract: invalid arena knobs rejected
TEST_CASE("given_bad_food_density_when_validate_then_throws", "[survival][config]") {
  evogen::ExperimentConfig cfg;
  cfg.environment = "survival_arena";
  cfg.food_density = 1.5f;
  REQUIRE_THROWS_AS(evogen::validate_experiment_config(cfg),
                    std::invalid_argument);
}

TEST_CASE("given_survival_config_when_factory_then_interactive",
          "[survival][config]") {
  const auto j = nlohmann::json::parse(R"({
    "name":"s","condition":"C","environment":"survival_arena",
    "population_size":4,"genome_size":8,"seed":1,"max_generations":2,
    "grid_w":8,"grid_h":8,"food_density":0.1,"energy_drain":0.05,
    "hazard_rate":0.0,"start_energy":1.0,"episode_ticks":8,
    "initial_learning_rate":0.01
  })");
  const auto cfg = evogen::parse_experiment_config(j);
  auto env = evogen::make_environment(cfg);
  REQUIRE(env->interactive());
}

TEST_CASE("given_survival_when_one_generation_then_alive_mean_logged",
          "[survival][loop]") {
  evogen::ExperimentConfig cfg;
  cfg.name = "unit";
  cfg.condition = "C";
  cfg.environment = "survival_arena";
  cfg.population_size = 4;
  cfg.genome_size = 8;
  cfg.seed = 3;
  cfg.max_generations = 1;
  cfg.enable_direct_learning = true;
  cfg.enable_genetic_reproduction = true;
  cfg.initial_learning_rate = 0.01f;
  cfg.grid_w = 8;
  cfg.grid_h = 8;
  cfg.food_density = 0.2f;
  cfg.hazard_rate = 0.0f;
  cfg.episode_ticks = 10;
  cfg.elite_count = 1;

  const auto dir =
      std::filesystem::temp_directory_path() / "evogen_survival_loop";
  std::filesystem::remove_all(dir);
  evogen::Rng rng(cfg.seed);
  auto pop = evogen::Population::create_random(cfg, rng);
  auto env = evogen::make_environment(cfg);
  evogen::Recorder recorder(dir.string());
  const auto result = evogen::run_generations(pop, *env, cfg, recorder, 1);
  REQUIRE(result.generations_run == 1);
  REQUIRE(result.last.alive_mean >= 0.0f);
  REQUIRE(result.last.alive_mean <= 1.0f);
}
