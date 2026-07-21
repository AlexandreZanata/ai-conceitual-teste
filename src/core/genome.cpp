#include "core/genome.hpp"

#include <algorithm>

namespace evogen {

void clamp_genome_rates(Genome& genome) {
  genome.mutation_rate = std::clamp(genome.mutation_rate, 0.0f, 1.0f);
  genome.learning_rate = std::clamp(genome.learning_rate, 0.0f, 1.0f);
}

bool genome_size_ok(const Genome& genome, std::size_t expected) {
  return genome.weights.size() == expected;
}

}  // namespace evogen
