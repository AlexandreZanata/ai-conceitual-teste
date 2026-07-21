#include "core/rng.hpp"

#include <stdexcept>

namespace evogen {

Rng::Rng(std::uint64_t seed) : eng_(seed) {}

float Rng::uniform01() {
  std::uniform_real_distribution<float> dist(0.0f, 1.0f);
  return dist(eng_);
}

float Rng::gaussian(float mean, float stddev) {
  std::normal_distribution<float> dist(mean, stddev);
  return dist(eng_);
}

std::size_t Rng::index(std::size_t n) {
  if (n == 0) {
    throw std::invalid_argument("Rng::index requires n > 0");
  }
  std::uniform_int_distribution<std::size_t> dist(0, n - 1);
  return dist(eng_);
}

Genome Rng::make_genome(std::size_t size, float mut, float lr) {
  Genome g;
  g.weights.resize(size);
  for (float& w : g.weights) {
    w = gaussian(0.0f, 0.5f);
  }
  g.mutation_rate = mut;
  g.learning_rate = lr;
  clamp_genome_rates(g);
  return g;
}

}  // namespace evogen
