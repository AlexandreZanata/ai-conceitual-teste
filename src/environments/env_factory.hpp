#pragma once

#include "core/experiment_config.hpp"
#include "environments/environment.hpp"

#include <memory>

namespace evogen {

/** Build Environment from config (`function_approx` | `survival_arena`). */
std::unique_ptr<Environment> make_environment(const ExperimentConfig& cfg);

}  // namespace evogen
