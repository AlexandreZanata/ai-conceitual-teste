#include <catch2/catch_approx.hpp>
#include <catch2/catch_test_macros.hpp>

#include "core/direct_learning.hpp"

TEST_CASE("direct learn golden delta weights", "[direct]") {
  // Hand calculation: w += lr * error * input
  // w={0,0}, lr=0.1, error=1, input={1,2} → Δw={0.1,0.2}
  std::vector<float> weights{0.0f, 0.0f};
  evogen::apply_direct_learn(weights, 0.1f, {1.0f, 2.0f}, 1.0f);
  REQUIRE(weights[0] == Catch::Approx(0.1f));
  REQUIRE(weights[1] == Catch::Approx(0.2f));
}

TEST_CASE("direct learn second step accumulates", "[direct]") {
  std::vector<float> weights{0.1f, 0.2f};
  evogen::apply_direct_learn(weights, 0.1f, {1.0f, 0.0f}, 2.0f);
  REQUIRE(weights[0] == Catch::Approx(0.3f));
  REQUIRE(weights[1] == Catch::Approx(0.2f));
}
