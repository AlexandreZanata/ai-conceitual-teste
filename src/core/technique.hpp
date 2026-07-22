#pragma once

#include "core/experiment_config.hpp"

#include <string>

namespace evogen {

/** Known technique IDs: R0, A, B, C, C-L, A+. Empty technique is allowed. */
bool is_known_technique(const std::string& id);

/**
 * Map technique ID → flags (genetic/direct/inheritance/elite/rates + condition).
 * Throws std::invalid_argument on unknown non-empty id.
 */
void apply_technique_defaults(ExperimentConfig& cfg);

}  // namespace evogen
