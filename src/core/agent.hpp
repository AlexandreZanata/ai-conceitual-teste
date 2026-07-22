#pragma once

#include "core/genome.hpp"

#include <string>
#include <vector>

namespace evogen {

/**
 * Evolutionary individual.
 * Genotype is heritable; phenotype weights adapt via DirectLearner in-lifetime.
 */
class Agent {
 public:
  explicit Agent(Genome genotype);

  const Genome& genotype() const { return genotype_; }
  Genome& genotype() { return genotype_; }
  const std::vector<float>& phenotype() const { return phenotype_; }
  std::vector<float>& phenotype() { return phenotype_; }
  float fitness() const { return fitness_; }

  /** Copy genotype weights into phenotype (start of a Darwinian lifetime). */
  void begin_lifetime();
  void reset_fitness();
  void add_reward(float reward);
  float respond(const std::vector<float>& stimulus) const;

  /** Darwinian: genotype only. Lamarckian: phenotype weights written back. */
  Genome reproduction_genome(bool lamarckian) const;

 private:
  Genome genotype_;
  std::vector<float> phenotype_;
  float fitness_{0.0f};
};

inline bool is_lamarckian(const std::string& inheritance_mode) {
  return inheritance_mode == "Lamarckian";
}

}  // namespace evogen
