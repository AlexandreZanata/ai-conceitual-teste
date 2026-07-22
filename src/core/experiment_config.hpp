#pragma once

#include <cstdint>
#include <string>

#include <nlohmann/json.hpp>

namespace evogen {

struct ExperimentConfig {
  std::string name;
  std::string condition{"A"};
  std::string technique;
  std::string environment{"function_approx"};
  std::size_t population_size{50};
  int max_generations{100};
  std::uint64_t seed{42};
  std::string inheritance_mode{"Darwinian"};
  bool enable_direct_learning{false};
  bool enable_genetic_reproduction{true};
  float initial_mutation_rate{0.05f};
  float initial_learning_rate{0.0f};
  std::size_t genome_size{16};
  std::size_t tournament_k{3};
  std::size_t elite_count{1};
  std::string function_task{"xor"};
  std::size_t episode_length{16};
  int generation_delay_ms{0};
  std::size_t grid_w{16};
  std::size_t grid_h{16};
  float food_density{0.08f};
  float energy_drain{0.05f};
  float hazard_rate{0.03f};
  float start_energy{1.0f};
  std::size_t episode_ticks{32};
  /** 0 = wall-clock budget disabled. */
  std::int64_t max_wall_ms{0};
  bool use_fitness_threshold{false};
  float fitness_threshold{0.0f};
  bool enable_drift{false};
  float drift_at_fraction{0.5f};
  /** <0 = double current hazard_rate on drift. */
  float post_drift_hazard_rate{-1.0f};
  /** <0 = leave food_density unchanged on drift. */
  float post_drift_food_density{-1.0f};
  std::string bench;
};

ExperimentConfig load_experiment_config(const std::string& path);
ExperimentConfig parse_experiment_config(const nlohmann::json& j);
void apply_condition_defaults(ExperimentConfig& cfg);
void validate_experiment_config(const ExperimentConfig& cfg);

}  // namespace evogen
