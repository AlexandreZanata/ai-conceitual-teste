#pragma once

#include "core/experiment_config.hpp"
#include "core/population.hpp"
#include "core/recorder.hpp"
#include "environments/environment.hpp"

namespace evogen {

struct RunResult {
  GenerationMetrics last;
  int generations_run{0};
};

/** Evaluate population for N generations; direct_learn is no-op in phase 03. */
RunResult run_generations(Population& population, Environment& env,
                          const ExperimentConfig& cfg, Recorder& recorder,
                          int generations);

}  // namespace evogen
