#pragma once

#include <vector>

namespace evogen {

/**
 * Environment port: episode stimuli, supervised target, reward.
 * Reward formula is defined by each concrete environment.
 */
class Environment {
 public:
  virtual ~Environment() = default;
  virtual std::vector<std::vector<float>> episode() const = 0;
  virtual float target_of(const std::vector<float>& stimulus) const = 0;
  virtual float evaluate(float response,
                         const std::vector<float>& stimulus) const = 0;
};

}  // namespace evogen
