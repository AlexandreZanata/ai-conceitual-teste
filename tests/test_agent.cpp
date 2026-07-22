#include <catch2/catch_test_macros.hpp>

#include "core/agent.hpp"
#include "environments/function_approx_env.hpp"

TEST_CASE("agent fitness accumulates rewards", "[agent]") {
  evogen::Genome g;
  g.weights = {1.0f, 0.0f, 0.0f, 0.0f};
  evogen::Agent agent(g);
  REQUIRE(agent.fitness() == 0.0f);
  agent.add_reward(1.5f);
  agent.add_reward(0.5f);
  REQUIRE(agent.fitness() == 2.0f);
  agent.reset_fitness();
  REQUIRE(agent.fitness() == 0.0f);
}

TEST_CASE("linear respond and xor environment evaluate", "[agent][env]") {
  evogen::Genome g;
  g.weights = {1.0f, 1.0f};
  evogen::Agent agent(g);
  evogen::FunctionApproxEnv env("xor", 4);
  const auto episode = env.episode();
  REQUIRE(episode.size() == 4);
  float total = 0.0f;
  for (const auto& stim : episode) {
    const float y = agent.respond(stim);
    total += env.evaluate(y, stim);
  }
  agent.add_reward(total);
  REQUIRE(agent.fitness() == total);
}
