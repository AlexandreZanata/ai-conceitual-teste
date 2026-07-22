#include "environments/function_approx_env.hpp"

#include <cmath>
#include <stdexcept>

namespace evogen {

namespace {

constexpr float kPi = 3.14159265358979323846f;

float xor_target(const std::vector<float>& stimulus) {
  if (stimulus.size() < 2) {
    throw std::invalid_argument("xor stimulus needs >= 2 dims");
  }
  const int a = stimulus[0] >= 0.5f ? 1 : 0;
  const int b = stimulus[1] >= 0.5f ? 1 : 0;
  return static_cast<float>(a ^ b);
}

}  // namespace

FunctionApproxEnv::FunctionApproxEnv(std::string task,
                                     std::size_t episode_length)
    : task_(std::move(task)), episode_length_(episode_length) {
  if (task_ != "xor" && task_ != "sine") {
    throw std::invalid_argument("function_task must be xor or sine");
  }
  if (episode_length_ == 0) {
    throw std::invalid_argument("episode_length must be > 0");
  }
}

std::vector<std::vector<float>> FunctionApproxEnv::episode() const {
  if (task_ == "xor") {
    return {{0.0f, 0.0f}, {0.0f, 1.0f}, {1.0f, 0.0f}, {1.0f, 1.0f}};
  }
  std::vector<std::vector<float>> out;
  out.reserve(episode_length_);
  for (std::size_t i = 0; i < episode_length_; ++i) {
    const float x =
        (2.0f * kPi * static_cast<float>(i)) / static_cast<float>(episode_length_);
    out.push_back({x, 1.0f});
  }
  return out;
}

float FunctionApproxEnv::target_of(const std::vector<float>& stimulus) const {
  if (task_ == "xor") {
    return xor_target(stimulus);
  }
  if (stimulus.empty()) {
    throw std::invalid_argument("sine stimulus empty");
  }
  return std::sin(stimulus[0]);
}

float FunctionApproxEnv::evaluate(float response,
                                  const std::vector<float>& stimulus) const {
  const float err = response - target_of(stimulus);
  return -(err * err);
}

}  // namespace evogen
