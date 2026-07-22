#include <catch2/catch_test_macros.hpp>

#include "core/experiment_config.hpp"
#include "core/technique.hpp"

#include <nlohmann/json.hpp>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

struct ExpectedFlags {
  bool genetic;
  bool direct;
  std::string inheritance;
  std::size_t elite;
  std::string condition;
};

ExpectedFlags expected_for(const std::string& id) {
  if (id == "R0") {
    return {false, false, "Darwinian", 1, "A"};
  }
  if (id == "A") {
    return {true, false, "Darwinian", 1, "A"};
  }
  if (id == "B") {
    return {false, true, "Darwinian", 1, "B"};
  }
  if (id == "C") {
    return {true, true, "Darwinian", 1, "C"};
  }
  if (id == "C-L") {
    return {true, true, "Lamarckian", 1, "C"};
  }
  return {true, false, "Darwinian", 5, "A"};  // A+
}

}  // namespace

// Contract: docs/EXPERIMENTAL-DESIGN.md technique matrix ↔ runtime flags
TEST_CASE("given_each_technique_when_apply_then_flags_match_table",
          "[technique]") {
  const std::vector<std::string> ids = {"R0", "A", "B", "C", "C-L", "A+"};
  for (const auto& id : ids) {
    INFO("technique=" << id);
    evogen::ExperimentConfig cfg;
    cfg.technique = id;
    evogen::apply_technique_defaults(cfg);
    const auto exp = expected_for(id);
    REQUIRE(cfg.enable_genetic_reproduction == exp.genetic);
    REQUIRE(cfg.enable_direct_learning == exp.direct);
    REQUIRE(cfg.inheritance_mode == exp.inheritance);
    REQUIRE(cfg.elite_count == exp.elite);
    REQUIRE(cfg.condition == exp.condition);
  }
}

TEST_CASE("given_unknown_technique_when_apply_then_throws", "[technique]") {
  evogen::ExperimentConfig cfg;
  cfg.technique = "Z9";
  REQUIRE_THROWS_AS(evogen::apply_technique_defaults(cfg),
                    std::invalid_argument);
}

TEST_CASE("given_survival_technique_configs_when_load_then_flags_ok",
          "[technique][config]") {
  const auto r0 =
      evogen::load_experiment_config("experiments/survival/R0.json");
  REQUIRE(r0.technique == "R0");
  REQUIRE_FALSE(r0.enable_genetic_reproduction);
  REQUIRE_FALSE(r0.enable_direct_learning);

  const auto c = evogen::load_experiment_config("experiments/survival/C.json");
  REQUIRE(c.technique == "C");
  REQUIRE(c.enable_genetic_reproduction);
  REQUIRE(c.enable_direct_learning);
  REQUIRE(c.inheritance_mode == "Darwinian");

  const auto cl =
      evogen::load_experiment_config("experiments/survival/C-L.json");
  REQUIRE(cl.technique == "C-L");
  REQUIRE(cl.inheritance_mode == "Lamarckian");

  const auto ap =
      evogen::load_experiment_config("experiments/survival/A+.json");
  REQUIRE(ap.technique == "A+");
  REQUIRE(ap.elite_count == 5);
  REQUIRE_FALSE(ap.enable_direct_learning);
}

TEST_CASE("given_json_technique_when_parse_then_overrides_condition_flags",
          "[technique][config]") {
  const auto j = nlohmann::json::parse(R"({
    "technique":"R0","condition":"C","environment":"survival_arena",
    "population_size":4,"genome_size":8,"seed":1,
    "enable_direct_learning":true,"enable_genetic_reproduction":true
  })");
  const auto cfg = evogen::parse_experiment_config(j);
  REQUIRE(cfg.technique == "R0");
  REQUIRE_FALSE(cfg.enable_direct_learning);
  REQUIRE_FALSE(cfg.enable_genetic_reproduction);
}

// Regression: T1 configs still load
TEST_CASE("given_t1_config_A_when_load_then_ok", "[technique][regression]") {
  const auto cfg =
      evogen::load_experiment_config("experiments/config_A_only_genetic.json");
  REQUIRE(cfg.technique.empty());
  REQUIRE(cfg.condition == "A");
  REQUIRE(cfg.enable_genetic_reproduction);
  REQUIRE_FALSE(cfg.enable_direct_learning);
}
