#include <catch2/catch_approx.hpp>
#include <catch2/catch_test_macros.hpp>

#include "core/crossover.hpp"
#include "core/experiment_config.hpp"
#include "core/mutation.hpp"
#include "core/population.hpp"
#include "core/rng.hpp"
#include "core/selection.hpp"

TEST_CASE("tournament prefers higher fitness", "[selection]") {
  std::vector<evogen::Agent> agents;
  evogen::Genome low;
  low.weights = {0.0f};
  evogen::Genome high;
  high.weights = {1.0f};
  agents.emplace_back(low);
  agents.emplace_back(high);
  agents[0].add_reward(0.0f);
  agents[1].add_reward(10.0f);
  evogen::Rng rng(1);
  std::size_t wins = 0;
  constexpr int trials = 200;
  for (int i = 0; i < trials; ++i) {
    if (evogen::tournament_pick(agents, 2, rng) == 1) {
      ++wins;
    }
  }
  REQUIRE(wins > trials / 2);
}

TEST_CASE("uniform crossover preserves size", "[crossover]") {
  evogen::Rng rng(3);
  auto a = rng.make_genome(10, 0.1f, 0.0f);
  auto b = rng.make_genome(10, 0.2f, 0.0f);
  auto child = evogen::uniform_crossover(a, b, rng);
  REQUIRE(child.weights.size() == 10);
}

TEST_CASE("mutation changes weights with high probability", "[mutation]") {
  evogen::Rng rng(5);
  auto g = rng.make_genome(32, 0.9f, 0.0f);
  const auto before = g.weights;
  for (int i = 0; i < 5; ++i) {
    evogen::mutate_genome(g, rng);
  }
  REQUIRE(g.weights != before);
}

TEST_CASE("evolve keeps population size", "[population]") {
  evogen::ExperimentConfig cfg;
  cfg.population_size = 12;
  cfg.genome_size = 8;
  cfg.elite_count = 2;
  cfg.enable_genetic_reproduction = true;
  cfg.seed = 11;
  evogen::Rng rng(cfg.seed);
  auto pop = evogen::Population::create_random(cfg, rng);
  for (auto& a : pop.agents()) {
    a.add_reward(static_cast<float>(rng.uniform01()));
  }
  pop.evolve(cfg, rng);
  REQUIRE(pop.size() == 12);
}
