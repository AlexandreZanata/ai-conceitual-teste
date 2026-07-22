#pragma once

#include <vector>

namespace evogen {

/**
 * One-step supervised delta rule (plan §2.2):
 *   w_i += learning_rate * error * input_i
 * where error = target - response.
 * Hebbian-style local update; O(n) in weight dimension.
 */
void apply_direct_learn(std::vector<float>& weights, float learning_rate,
                        const std::vector<float>& input, float error);

}  // namespace evogen
