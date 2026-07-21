#pragma once

#include "core/genome.hpp"
#include "core/rng.hpp"

namespace evogen {

/**
 * Gaussian mutation. Probability of touching each weight ~= mutation_rate.
 * Stddev scales with mutation_rate (adaptive via genome).
 */
void mutate_genome(Genome& genome, Rng& rng);

}  // namespace evogen
