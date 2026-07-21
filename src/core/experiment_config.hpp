#pragma once

#include <cstdint>
#include <string>

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
};

ExperimentConfig load_experiment_config(const std::string& path);
void validate_experiment_config(const ExperimentConfig& cfg);

}  // namespace evogen
