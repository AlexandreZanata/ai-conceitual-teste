#include "core/agent.hpp"

#include <algorithm>
#include <utility>

namespace evogen {

Agent::Agent(Genome genome) : genome_(std::move(genome)) {
  clamp_genome_rates(genome_);
}

void Agent::reset_fitness() { fitness_ = 0.0f; }

void Agent::add_reward(float reward) { fitness_ += reward; }

float Agent::respond(const std::vector<float>& stimulus) const {
  const auto& weights = genome_.weights;
  const std::size_t n = std::min(weights.size(), stimulus.size());
  float sum = 0.0f;
  for (std::size_t i = 0; i < n; ++i) {
    sum += weights[i] * stimulus[i];
  }
  return sum;
}

}  // namespace evogen
