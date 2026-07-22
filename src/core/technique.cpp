#include "core/technique.hpp"

#include <stdexcept>

namespace evogen {

bool is_known_technique(const std::string& id) {
  return id == "R0" || id == "A" || id == "B" || id == "C" || id == "C-L" ||
         id == "A+";
}

void apply_technique_defaults(ExperimentConfig& cfg) {
  if (cfg.technique.empty()) {
    return;
  }
  if (!is_known_technique(cfg.technique)) {
    throw std::invalid_argument("unknown technique: " + cfg.technique);
  }
  cfg.inheritance_mode = "Darwinian";
  cfg.elite_count = 1;
  if (cfg.technique == "R0") {
    cfg.condition = "A";
    cfg.enable_genetic_reproduction = false;
    cfg.enable_direct_learning = false;
    cfg.initial_mutation_rate = 0.0f;
    cfg.initial_learning_rate = 0.0f;
    return;
  }
  if (cfg.technique == "A") {
    cfg.condition = "A";
    cfg.enable_genetic_reproduction = true;
    cfg.enable_direct_learning = false;
    cfg.initial_mutation_rate = 0.05f;
    cfg.initial_learning_rate = 0.0f;
    return;
  }
  if (cfg.technique == "B") {
    cfg.condition = "B";
    cfg.enable_genetic_reproduction = false;
    cfg.enable_direct_learning = true;
    cfg.initial_mutation_rate = 0.0f;
    cfg.initial_learning_rate = 0.01f;
    return;
  }
  if (cfg.technique == "C") {
    cfg.condition = "C";
    cfg.enable_genetic_reproduction = true;
    cfg.enable_direct_learning = true;
    cfg.initial_mutation_rate = 0.05f;
    cfg.initial_learning_rate = 0.01f;
    return;
  }
  if (cfg.technique == "C-L") {
    cfg.condition = "C";
    cfg.enable_genetic_reproduction = true;
    cfg.enable_direct_learning = true;
    cfg.inheritance_mode = "Lamarckian";
    cfg.initial_mutation_rate = 0.05f;
    cfg.initial_learning_rate = 0.01f;
    return;
  }
  // A+: genetic + strong elitism (diversity stress — fewer unique lineages)
  cfg.condition = "A";
  cfg.enable_genetic_reproduction = true;
  cfg.enable_direct_learning = false;
  cfg.elite_count = 5;
  cfg.initial_mutation_rate = 0.05f;
  cfg.initial_learning_rate = 0.0f;
}

}  // namespace evogen
