#pragma once

#include "environments/environment.hpp"

namespace evogen {

/** Fixed stimuli stub for phase 03 CLI validation. */
class FunctionApproxEnv final : public Environment {
 public:
  std::vector<std::vector<float>> episode() const override;
  float evaluate(float response,
                 const std::vector<float>& stimulus) const override;
};

}  // namespace evogen
