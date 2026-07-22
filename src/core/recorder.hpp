#pragma once

#include <cstdint>

#include "core/agent.hpp"

#include <string>
#include <vector>

namespace evogen {

struct GenerationMetrics {
  int generation{0};
  std::uint64_t seed{0};
  std::string condition;
  float fitness_mean{0.0f};
  float fitness_max{0.0f};
  float diversity_mean{0.0f};
  float learning_rate_mean{0.0f};
  float mutation_rate_mean{0.0f};
  float alive_mean{1.0f};
  std::string technique;
};

GenerationMetrics compute_metrics(int generation, std::uint64_t seed,
                                  const std::string& condition,
                                  const std::vector<Agent>& agents);

class Recorder {
 public:
  explicit Recorder(std::string results_dir);

  void log_generation(const GenerationMetrics& metrics) const;

 private:
  std::string results_dir_;
};

}  // namespace evogen
