#include "core/crossover.hpp"

#include <algorithm>
#include <stdexcept>

namespace evogen {

Genome uniform_crossover(const Genome& a, const Genome& b, Rng& rng) {
  if (a.weights.size() != b.weights.size()) {
    throw std::invalid_argument("uniform_crossover: size mismatch");
  }
  Genome child;
  child.weights.resize(a.weights.size());
  for (std::size_t i = 0; i < a.weights.size(); ++i) {
    child.weights[i] = (rng.uniform01() < 0.5f) ? a.weights[i] : b.weights[i];
  }
  child.mutation_rate =
      (rng.uniform01() < 0.5f) ? a.mutation_rate : b.mutation_rate;
  child.learning_rate =
      (rng.uniform01() < 0.5f) ? a.learning_rate : b.learning_rate;
  clamp_genome_rates(child);
  return child;
}

}  // namespace evogen
