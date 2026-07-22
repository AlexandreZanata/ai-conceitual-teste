#pragma once

#include "environments/environment.hpp"

#include <cstddef>
#include <string>

namespace evogen {

/**
 * T1 function approximation.
 *
 * Reward (documented): reward = -(response - target)^2
 *   — higher (closer to 0) is better; perfect match yields 0.
 *
 * Tasks:
 *   - xor: 4 classic patterns (not linearly separable; stress test)
 *   - sine: episode_length samples; stimulus [x, 1]; target = sin(x)
 */
class FunctionApproxEnv final : public Environment {
 public:
  FunctionApproxEnv(std::string task, std::size_t episode_length);

  std::vector<std::vector<float>> episode() const override;
  float target_of(const std::vector<float>& stimulus) const override;
  float evaluate(float response,
                 const std::vector<float>& stimulus) const override;

  const std::string& task() const { return task_; }
  std::size_t episode_length() const { return episode_length_; }

 private:
  std::string task_;
  std::size_t episode_length_;
};

}  // namespace evogen
