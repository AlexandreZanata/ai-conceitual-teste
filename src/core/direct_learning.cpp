#include "core/direct_learning.hpp"

#include <algorithm>

namespace evogen {

void apply_direct_learn(std::vector<float>& weights, float learning_rate,
                        const std::vector<float>& input, float error) {
  const std::size_t n = std::min(weights.size(), input.size());
  for (std::size_t i = 0; i < n; ++i) {
    weights[i] += learning_rate * error * input[i];
  }
}

}  // namespace evogen
