#pragma once

#include "core/genome.hpp"

#include <vector>

namespace evogen {

/** Evolutionary individual: genome + lifetime fitness. */
class Agent {
 public:
  explicit Agent(Genome genome);

  const Genome& genome() const { return genome_; }
  Genome& genome() { return genome_; }
  float fitness() const { return fitness_; }

  void reset_fitness();
  void add_reward(float reward);
  float respond(const std::vector<float>& stimulus) const;

 private:
  Genome genome_;
  float fitness_{0.0f};
};

}  // namespace evogen
