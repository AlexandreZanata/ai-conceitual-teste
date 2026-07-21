#pragma once

#include "core/agent.hpp"
#include "core/rng.hpp"

#include <vector>

namespace evogen {

/** Tournament selection (Mitchell/Goldberg-style GA baseline). */
std::size_t tournament_pick(const std::vector<Agent>& agents, std::size_t k,
                            Rng& rng);

std::vector<std::size_t> select_parents(const std::vector<Agent>& agents,
                                        std::size_t count, std::size_t k,
                                        Rng& rng);

}  // namespace evogen
