#pragma once

#include <vector>

namespace evogen {

/**
 * Environment port: stimuli episode + reward evaluation.
 * Stub T1 in phase 03; full function approx in phase 04.
 */
class Environment {
 public:
  virtual ~Environment() = default;
  virtual std::vector<std::vector<float>> episode() const = 0;
  virtual float evaluate(float response,
                         const std::vector<float>& stimulus) const = 0;
};

}  // namespace evogen
