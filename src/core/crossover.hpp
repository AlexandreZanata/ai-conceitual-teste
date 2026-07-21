#pragma once

#include "core/genome.hpp"
#include "core/rng.hpp"

namespace evogen {

/** Uniform crossover: each gene from either parent with p=0.5. */
Genome uniform_crossover(const Genome& a, const Genome& b, Rng& rng);

}  // namespace evogen
