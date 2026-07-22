#include "core/budget.hpp"

#include <algorithm>
#include <cmath>

namespace evogen {

std::string stop_reason_after_gen(const ExperimentConfig& cfg,
                                  float fitness_mean, std::int64_t wall_ms) {
  if (cfg.use_fitness_threshold &&
      fitness_mean >= cfg.fitness_threshold) {
    return "fitness_threshold";
  }
  if (cfg.max_wall_ms > 0 && wall_ms >= cfg.max_wall_ms) {
    return "max_wall_ms";
  }
  return {};
}

bool is_drift_generation(const ExperimentConfig& cfg, int generation) {
  if (!cfg.enable_drift || cfg.max_generations <= 0) {
    return false;
  }
  const int flip_at =
      static_cast<int>(std::floor(cfg.drift_at_fraction *
                                  static_cast<float>(cfg.max_generations)));
  return generation == flip_at;
}

void apply_arena_drift(Environment& env, const ExperimentConfig& cfg) {
  env.set_season(1.0f - env.season());
  const float next_hazard =
      cfg.post_drift_hazard_rate >= 0.0f
          ? cfg.post_drift_hazard_rate
          : std::min(1.0f, env.hazard_rate() * 2.0f);
  env.set_hazard_rate(next_hazard);
  if (cfg.post_drift_food_density >= 0.0f) {
    env.set_food_density(cfg.post_drift_food_density);
  }
}

}  // namespace evogen
