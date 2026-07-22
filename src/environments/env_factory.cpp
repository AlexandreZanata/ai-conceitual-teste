#include "environments/env_factory.hpp"

#include "environments/function_approx_env.hpp"
#include "environments/survival_arena_env.hpp"

#include <stdexcept>

namespace evogen {

std::unique_ptr<Environment> make_environment(const ExperimentConfig& cfg) {
  if (cfg.environment == "function_approx") {
    return std::make_unique<FunctionApproxEnv>(cfg.function_task,
                                               cfg.episode_length);
  }
  if (cfg.environment == "survival_arena") {
    return std::make_unique<SurvivalArenaEnv>(
        cfg.grid_w, cfg.grid_h, cfg.food_density, cfg.energy_drain,
        cfg.hazard_rate, cfg.start_energy, cfg.episode_ticks);
  }
  throw std::invalid_argument("unknown environment: " + cfg.environment);
}

}  // namespace evogen
