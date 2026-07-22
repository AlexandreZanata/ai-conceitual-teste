#include "core/agent.hpp"

#include <algorithm>
#include <utility>

namespace evogen {

Agent::Agent(Genome genotype) : genotype_(std::move(genotype)) {
  clamp_genome_rates(genotype_);
  begin_lifetime();
}

void Agent::begin_lifetime() { phenotype_ = genotype_.weights; }

void Agent::reset_fitness() { fitness_ = 0.0f; }

void Agent::add_reward(float reward) { fitness_ += reward; }

float Agent::respond(const std::vector<float>& stimulus) const {
  const std::size_t n = std::min(phenotype_.size(), stimulus.size());
  float sum = 0.0f;
  for (std::size_t i = 0; i < n; ++i) {
    sum += phenotype_[i] * stimulus[i];
  }
  return sum;
}

Genome Agent::reproduction_genome(bool lamarckian) const {
  Genome out = genotype_;
  if (lamarckian) {
    out.weights = phenotype_;
  }
  clamp_genome_rates(out);
  return out;
}

}  // namespace evogen
