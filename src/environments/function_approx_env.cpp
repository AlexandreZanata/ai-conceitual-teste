#include "environments/function_approx_env.hpp"

#include <cmath>

namespace evogen {

std::vector<std::vector<float>> FunctionApproxEnv::episode() const {
  return {
      {1.0f, 0.0f, 0.0f, 0.0f},
      {0.0f, 1.0f, 0.0f, 0.0f},
      {0.0f, 0.0f, 1.0f, 0.0f},
      {1.0f, 1.0f, 0.0f, 0.0f},
  };
}

float FunctionApproxEnv::evaluate(float response,
                                  const std::vector<float>& stimulus) const {
  float target = 0.0f;
  for (float v : stimulus) {
    target += v;
  }
  const float err = response - target;
  return -err * err;
}

}  // namespace evogen
