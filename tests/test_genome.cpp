#include <catch2/catch_test_macros.hpp>

#include "core/genome.hpp"
#include "core/rng.hpp"

TEST_CASE("genome size invariant and rate clamp", "[genome]") {
  evogen::Rng rng(7);
  auto g = rng.make_genome(8, 0.05f, 0.01f);
  REQUIRE(evogen::genome_size_ok(g, 8));
  REQUIRE(g.weights.size() == 8);

  g.mutation_rate = 2.0f;
  g.learning_rate = -1.0f;
  evogen::clamp_genome_rates(g);
  REQUIRE(g.mutation_rate == 1.0f);
  REQUIRE(g.learning_rate == 0.0f);
}

TEST_CASE("rates stay within [0,1] after factory", "[genome]") {
  evogen::Rng rng(99);
  auto g = rng.make_genome(4, 1.5f, -0.2f);
  REQUIRE(g.mutation_rate >= 0.0f);
  REQUIRE(g.mutation_rate <= 1.0f);
  REQUIRE(g.learning_rate >= 0.0f);
  REQUIRE(g.learning_rate <= 1.0f);
}
