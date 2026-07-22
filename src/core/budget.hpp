#pragma once

#include "core/experiment_config.hpp"
#include "environments/environment.hpp"

#include <chrono>
#include <cstdint>
#include <string>

namespace evogen {

using SteadyClock = std::chrono::steady_clock;

inline std::int64_t wall_ms_since(SteadyClock::time_point start) {
  return std::chrono::duration_cast<std::chrono::milliseconds>(
             SteadyClock::now() - start)
      .count();
}

/** Empty string = continue. Reasons: max_wall_ms | fitness_threshold. */
std::string stop_reason_after_gen(const ExperimentConfig& cfg,
                                  float fitness_mean, std::int64_t wall_ms);

/** True when this generation index is the drift flip point. */
bool is_drift_generation(const ExperimentConfig& cfg, int generation);

/** Flip season + hazard (and optional food) on the live environment. */
void apply_arena_drift(Environment& env, const ExperimentConfig& cfg);

}  // namespace evogen
