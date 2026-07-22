#pragma once

#include "core/experiment_config.hpp"
#include "core/population.hpp"
#include "core/recorder.hpp"
#include "core/rng.hpp"
#include "environments/environment.hpp"

namespace evogen {

struct RunResult {
  GenerationMetrics last;
  int generations_run{0};
};

/** One generation: evaluate all agents, metrics, then evolve. */
GenerationMetrics step_generation(Population& population, Environment& env,
                                  const ExperimentConfig& cfg, Rng& rng,
                                  int generation);

/** Evaluate population for N generations (CLI path). */
RunResult run_generations(Population& population, Environment& env,
                          const ExperimentConfig& cfg, Recorder& recorder,
                          int generations);

}  // namespace evogen
