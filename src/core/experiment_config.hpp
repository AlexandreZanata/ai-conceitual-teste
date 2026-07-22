#pragma once

#include <cstdint>
#include <string>

#include <nlohmann/json.hpp>

namespace evogen {

struct ExperimentConfig {
  std::string name;
  std::string condition{"A"};
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
};

ExperimentConfig load_experiment_config(const std::string& path);
ExperimentConfig parse_experiment_config(const nlohmann::json& j);
void apply_condition_defaults(ExperimentConfig& cfg);
void validate_experiment_config(const ExperimentConfig& cfg);

}  // namespace evogen
