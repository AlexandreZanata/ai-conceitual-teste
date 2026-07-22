#include <catch2/catch_approx.hpp>
#include <catch2/catch_test_macros.hpp>

#include "core/agent.hpp"
#include "core/genome.hpp"
#include "environments/function_approx_env.hpp"

TEST_CASE("xor episode is deterministic with four patterns", "[env][xor]") {
  evogen::FunctionApproxEnv env("xor", 16);
  const auto a = env.episode();
  const auto b = env.episode();
  REQUIRE(a.size() == 4);
  REQUIRE(a == b);
  REQUIRE(env.target_of({0.0f, 0.0f}) == Catch::Approx(0.0f));
  REQUIRE(env.target_of({0.0f, 1.0f}) == Catch::Approx(1.0f));
  REQUIRE(env.target_of({1.0f, 0.0f}) == Catch::Approx(1.0f));
  REQUIRE(env.target_of({1.0f, 1.0f}) == Catch::Approx(0.0f));
}

TEST_CASE("sine episode length and reward formula", "[env][sine]") {
  evogen::FunctionApproxEnv env("sine", 8);
  const auto ep = env.episode();
  REQUIRE(ep.size() == 8);
  REQUIRE(ep == env.episode());
  const float y = 0.0f;
  const float target = env.target_of(ep.front());
  const float reward = env.evaluate(y, ep.front());
  REQUIRE(reward == Catch::Approx(-(y - target) * (y - target)));
}

TEST_CASE("darwinian reproduction ignores phenotype", "[agent][inherit]") {
  evogen::Genome g;
  g.weights = {1.0f, 2.0f};
  g.learning_rate = 0.1f;
  evogen::Agent agent(g);
  agent.phenotype()[0] = 9.0f;
  const auto heritable = agent.reproduction_genome(false);
  REQUIRE(heritable.weights[0] == Catch::Approx(1.0f));
  const auto lamarck = agent.reproduction_genome(true);
  REQUIRE(lamarck.weights[0] == Catch::Approx(9.0f));
}
