#pragma once

#include "core/genome.hpp"

#include <cstdint>
#include <random>

namespace evogen {

/** Seeded RNG for reproducible experiments (plan §10). */
class Rng {
 public:
  explicit Rng(std::uint64_t seed);

  float uniform01();
  float gaussian(float mean, float stddev);
  std::size_t index(std::size_t n);
  Genome make_genome(std::size_t size, float mut, float lr);

 private:
  std::mt19937_64 eng_;
};

}  // namespace evogen
