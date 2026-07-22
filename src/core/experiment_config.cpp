#include "core/experiment_config.hpp"

#include <fstream>
#include <nlohmann/json.hpp>
#include <stdexcept>

namespace evogen {

namespace {

void apply_identity(ExperimentConfig& cfg, const nlohmann::json& j) {
  if (j.contains("name")) cfg.name = j.at("name").get<std::string>();
  if (j.contains("condition")) cfg.condition = j.at("condition").get<std::string>();
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
}

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

void validate_modes_and_rates(const ExperimentConfig& cfg) {
  if (cfg.function_task != "xor" && cfg.function_task != "sine") {
    throw std::invalid_argument("function_task must be xor or sine");
  }
  if (cfg.inheritance_mode != "Darwinian" &&
      cfg.inheritance_mode != "Lamarckian") {
    throw std::invalid_argument(
        "inheritance_mode must be Darwinian or Lamarckian");
  }
  if (cfg.initial_mutation_rate < 0.0f || cfg.initial_mutation_rate > 1.0f) {
    throw std::invalid_argument("initial_mutation_rate must be in [0, 1]");
  }
  if (cfg.initial_learning_rate < 0.0f || cfg.initial_learning_rate > 1.0f) {
    throw std::invalid_argument("initial_learning_rate must be in [0, 1]");
  }
}

}  // namespace

ExperimentConfig load_experiment_config(const std::string& path) {
  std::ifstream in(path);
  if (!in) {
    throw std::runtime_error("cannot open config: " + path);
  }
  nlohmann::json j;
  in >> j;
  ExperimentConfig cfg;
  apply_identity(cfg, j);
  apply_sizes(cfg, j);
  apply_flags_and_rates(cfg, j);
  validate_experiment_config(cfg);
  return cfg;
}

void validate_experiment_config(const ExperimentConfig& cfg) {
  validate_sizes(cfg);
  validate_modes_and_rates(cfg);
}

}  // namespace evogen
