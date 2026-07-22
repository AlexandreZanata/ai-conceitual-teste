#include <catch2/catch_test_macros.hpp>

#include "core/experiment_config.hpp"
#include "server/experiment_controller.hpp"
#include "server/metrics_hub.hpp"

#include <filesystem>
#include <stdexcept>

namespace {

evogen::ExperimentConfig tiny_config() {
  evogen::ExperimentConfig cfg;
  cfg.name = "ctrl";
  cfg.condition = "A";
  cfg.population_size = 6;
  cfg.genome_size = 4;
  cfg.seed = 9;
  cfg.max_generations = 40;
  cfg.enable_direct_learning = false;
  cfg.enable_genetic_reproduction = true;
  cfg.function_task = "xor";
  cfg.episode_length = 4;
  cfg.elite_count = 1;
  return cfg;
}

}  // namespace

// Contract: docs/API-CONTRACT.md — pause/resume/stop lifecycle
TEST_CASE("given_running_when_pause_resume_stop_then_no_crash", "[controller]") {
  const auto dir =
      std::filesystem::temp_directory_path() / "evogen_ctrl_lifecycle";
  std::filesystem::remove_all(dir);
  evogen::MetricsHub hub;
  evogen::ExperimentController controller(hub, dir.string());

  const auto started = controller.start(tiny_config());
  const std::string id = started.at("experiment_id").get<std::string>();
  REQUIRE(started.at("status") == "running");

  REQUIRE(controller.pause(id));
  REQUIRE(controller.snapshot(id).at("status") == "paused");

  REQUIRE(controller.resume(id));
  REQUIRE(controller.snapshot(id).at("status") == "running");

  REQUIRE(controller.stop(id));
  REQUIRE(controller.snapshot(id).at("status") == "stopped");
}

// Contract: docs/API-CONTRACT.md — one active experiment
TEST_CASE("given_active_when_start_again_then_conflict", "[controller]") {
  const auto dir =
      std::filesystem::temp_directory_path() / "evogen_ctrl_conflict";
  std::filesystem::remove_all(dir);
  evogen::MetricsHub hub;
  evogen::ExperimentController controller(hub, dir.string());
  const auto started = controller.start(tiny_config());
  const std::string id = started.at("experiment_id").get<std::string>();
  REQUIRE_THROWS_AS(controller.start(tiny_config()), std::runtime_error);
  REQUIRE(controller.stop(id));
}
