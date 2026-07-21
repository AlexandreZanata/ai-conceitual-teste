#pragma once

#include "core/agent.hpp"
#include "core/experiment_config.hpp"
#include "core/rng.hpp"

#include <vector>

namespace evogen {

class Population {
 public:
  explicit Population(std::vector<Agent> agents);

  const std::vector<Agent>& agents() const { return agents_; }
  std::vector<Agent>& agents() { return agents_; }
  std::size_t size() const { return agents_.size(); }

  static Population create_random(const ExperimentConfig& cfg, Rng& rng);
  void evolve(const ExperimentConfig& cfg, Rng& rng);

 private:
  std::vector<Agent> agents_;
};

}  // namespace evogen
