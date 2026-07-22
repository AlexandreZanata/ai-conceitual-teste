#include "core/experiment_config.hpp"

#include "core/technique.hpp"

#include <fstream>
#include <nlohmann/json.hpp>
#include <stdexcept>

namespace evogen {

namespace {

void apply_identity(ExperimentConfig& cfg, const nlohmann::json& j) {
  if (j.contains("name")) cfg.name = j.at("name").get<std::string>();
  if (j.contains("condition")) cfg.condition = j.at("condition").get<std::string>();
  if (j.contains("technique")) {
    cfg.technique = j.at("technique").get<std::string>();
  }
  if (j.contains("environment")) {
    cfg.environment = j.at("environment").get<std::string>();
  }
  if (j.contains("inheritance_mode")) {
    cfg.inheritance_mode = j.at("inheritance_mode").get<std::string>();
  }
}

void apply_sizes(ExperimentConfig& cfg, const nlohmann::json& j) {
  if (j.contains("population_size")) {
    cfg.population_size = j.at("population_size").get<std::size_t>();
  }
  if (j.contains("max_generations")) {
    cfg.max_generations = j.at("max_generations").get<int>();
  }
  if (j.contains("seed")) cfg.seed = j.at("seed").get<std::uint64_t>();
  if (j.contains("genome_size")) {
    cfg.genome_size = j.at("genome_size").get<std::size_t>();
  }
  if (j.contains("tournament_k")) {
    cfg.tournament_k = j.at("tournament_k").get<std::size_t>();
  }
  if (j.contains("elite_count")) {
    cfg.elite_count = j.at("elite_count").get<std::size_t>();
  }
  if (j.contains("episode_length")) {
    cfg.episode_length = j.at("episode_length").get<std::size_t>();
  }
}

void apply_flags_and_rates(ExperimentConfig& cfg, const nlohmann::json& j) {
  if (j.contains("enable_direct_learning")) {
    cfg.enable_direct_learning = j.at("enable_direct_learning").get<bool>();
  }
  if (j.contains("enable_genetic_reproduction")) {
    cfg.enable_genetic_reproduction =
        j.at("enable_genetic_reproduction").get<bool>();
  }
  if (j.contains("initial_mutation_rate")) {
    cfg.initial_mutation_rate = j.at("initial_mutation_rate").get<float>();
  }
  if (j.contains("initial_learning_rate")) {
    cfg.initial_learning_rate = j.at("initial_learning_rate").get<float>();
  }
  if (j.contains("function_task")) {
    cfg.function_task = j.at("function_task").get<std::string>();
  }
  if (j.contains("generation_delay_ms")) {
    cfg.generation_delay_ms = j.at("generation_delay_ms").get<int>();
  }
}

void apply_arena(ExperimentConfig& cfg, const nlohmann::json& j) {
  if (j.contains("grid_w")) cfg.grid_w = j.at("grid_w").get<std::size_t>();
  if (j.contains("grid_h")) cfg.grid_h = j.at("grid_h").get<std::size_t>();
  if (j.contains("food_density")) {
    cfg.food_density = j.at("food_density").get<float>();
  }
  if (j.contains("energy_drain")) {
    cfg.energy_drain = j.at("energy_drain").get<float>();
  }
  if (j.contains("hazard_rate")) {
    cfg.hazard_rate = j.at("hazard_rate").get<float>();
  }
  if (j.contains("start_energy")) {
    cfg.start_energy = j.at("start_energy").get<float>();
  }
  if (j.contains("episode_ticks")) {
    cfg.episode_ticks = j.at("episode_ticks").get<std::size_t>();
  }
}

void apply_budget(ExperimentConfig& cfg, const nlohmann::json& j) {
  if (j.contains("max_wall_ms")) {
    cfg.max_wall_ms = j.at("max_wall_ms").get<std::int64_t>();
  }
  if (j.contains("fitness_threshold")) {
    cfg.use_fitness_threshold = true;
    cfg.fitness_threshold = j.at("fitness_threshold").get<float>();
  }
  if (j.contains("enable_drift")) {
    cfg.enable_drift = j.at("enable_drift").get<bool>();
  }
  if (j.contains("drift_at_fraction")) {
    cfg.drift_at_fraction = j.at("drift_at_fraction").get<float>();
  }
  if (j.contains("post_drift_hazard_rate")) {
    cfg.post_drift_hazard_rate = j.at("post_drift_hazard_rate").get<float>();
  }
  if (j.contains("post_drift_food_density")) {
    cfg.post_drift_food_density = j.at("post_drift_food_density").get<float>();
  }
  if (j.contains("bench")) cfg.bench = j.at("bench").get<std::string>();
}

}  // namespace

void apply_condition_defaults(ExperimentConfig& cfg) {
  if (cfg.condition == "A") {
    cfg.enable_direct_learning = false;
    cfg.enable_genetic_reproduction = true;
  } else if (cfg.condition == "B") {
    cfg.enable_direct_learning = true;
    cfg.enable_genetic_reproduction = false;
  } else if (cfg.condition == "C") {
    cfg.enable_direct_learning = true;
    cfg.enable_genetic_reproduction = true;
  }
}

ExperimentConfig parse_experiment_config(const nlohmann::json& j) {
  ExperimentConfig cfg;
  apply_identity(cfg, j);
  apply_condition_defaults(cfg);
  apply_sizes(cfg, j);
  apply_flags_and_rates(cfg, j);
  apply_arena(cfg, j);
  apply_budget(cfg, j);
  apply_technique_defaults(cfg);
  validate_experiment_config(cfg);
  return cfg;
}

ExperimentConfig load_experiment_config(const std::string& path) {
  std::ifstream in(path);
  if (!in) {
    throw std::runtime_error("cannot open config: " + path);
  }
  nlohmann::json j;
  in >> j;
  return parse_experiment_config(j);
}

}  // namespace evogen
