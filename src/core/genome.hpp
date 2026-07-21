#pragma once

#include <cstddef>
#include <vector>

namespace evogen {

/** Heritable parameters. Rates are clamped to [0, 1]. */
struct Genome {
  std::vector<float> weights;
  float mutation_rate{0.05f};
  float learning_rate{0.0f};
};

void clamp_genome_rates(Genome& genome);
bool genome_size_ok(const Genome& genome, std::size_t expected);

}  // namespace evogen
