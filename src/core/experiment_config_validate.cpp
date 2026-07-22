#include "core/experiment_config.hpp"

#include "core/technique.hpp"

#include <stdexcept>

namespace evogen {

namespace {

void validate_sizes(const ExperimentConfig& cfg) {
  if (cfg.population_size == 0) {
    throw std::invalid_argument("population_size must be > 0");
  }
  if (cfg.genome_size == 0) {
    throw std::invalid_argument("genome_size must be > 0");
  }
  if (cfg.max_generations < 0) {
    throw std::invalid_argument("max_generations must be >= 0");
  }
  if (cfg.episode_length == 0) {
    throw std::invalid_argument("episode_length must be > 0");
  }
}

void validate_environment(const ExperimentConfig& cfg) {
  if (cfg.environment != "function_approx" &&
      cfg.environment != "survival_arena") {
    throw std::invalid_argument(
        "environment must be function_approx or survival_arena");
  }
  if (cfg.environment == "function_approx" && cfg.function_task != "xor" &&
      cfg.function_task != "sine") {
    throw std::invalid_argument("function_task must be xor or sine");
  }
}

void validate_modes(const ExperimentConfig& cfg) {
  if (cfg.condition != "A" && cfg.condition != "B" && cfg.condition != "C") {
    throw std::invalid_argument("condition must be A, B, or C");
  }
  validate_environment(cfg);
  if (cfg.inheritance_mode != "Darwinian" &&
      cfg.inheritance_mode != "Lamarckian") {
    throw std::invalid_argument(
        "inheritance_mode must be Darwinian or Lamarckian");
  }
  if (!cfg.technique.empty() && !is_known_technique(cfg.technique)) {
    throw std::invalid_argument("unknown technique: " + cfg.technique);
  }
}

void validate_arena_grid(const ExperimentConfig& cfg) {
  if (cfg.grid_w == 0 || cfg.grid_h == 0) {
    throw std::invalid_argument("grid_w/grid_h must be > 0");
  }
  if (cfg.episode_ticks == 0) {
    throw std::invalid_argument("episode_ticks must be > 0");
  }
  if (cfg.start_energy <= 0.0f) {
    throw std::invalid_argument("start_energy must be > 0");
  }
}

void validate_arena_rates(const ExperimentConfig& cfg) {
  if (cfg.food_density < 0.0f || cfg.food_density > 1.0f) {
    throw std::invalid_argument("food_density must be in [0, 1]");
  }
  if (cfg.hazard_rate < 0.0f || cfg.hazard_rate > 1.0f) {
    throw std::invalid_argument("hazard_rate must be in [0, 1]");
  }
  if (cfg.energy_drain < 0.0f) {
    throw std::invalid_argument("energy_drain must be >= 0");
  }
}

void validate_arena(const ExperimentConfig& cfg) {
  if (cfg.environment != "survival_arena") {
    return;
  }
  validate_arena_grid(cfg);
  validate_arena_rates(cfg);
}

void validate_rates(const ExperimentConfig& cfg) {
  if (cfg.initial_mutation_rate < 0.0f || cfg.initial_mutation_rate > 1.0f) {
    throw std::invalid_argument("initial_mutation_rate must be in [0, 1]");
  }
  if (cfg.initial_learning_rate < 0.0f || cfg.initial_learning_rate > 1.0f) {
    throw std::invalid_argument("initial_learning_rate must be in [0, 1]");
  }
  if (cfg.generation_delay_ms < 0) {
    throw std::invalid_argument("generation_delay_ms must be >= 0");
  }
}

}  // namespace

void validate_experiment_config(const ExperimentConfig& cfg) {
  validate_sizes(cfg);
  validate_modes(cfg);
  validate_rates(cfg);
  validate_arena(cfg);
}

}  // namespace evogen
