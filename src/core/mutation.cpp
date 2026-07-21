#include "core/mutation.hpp"

namespace evogen {

void mutate_genome(Genome& genome, Rng& rng) {
  const float rate = genome.mutation_rate;
  const float stddev = 0.1f + rate;
  for (float& w : genome.weights) {
    if (rng.uniform01() < rate) {
      w += rng.gaussian(0.0f, stddev);
    }
  }
  if (rng.uniform01() < rate) {
    genome.mutation_rate += rng.gaussian(0.0f, 0.01f);
  }
  if (rng.uniform01() < rate) {
    genome.learning_rate += rng.gaussian(0.0f, 0.01f);
  }
  clamp_genome_rates(genome);
}

}  // namespace evogen
