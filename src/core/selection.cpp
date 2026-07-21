#include "core/selection.hpp"

#include <stdexcept>

namespace evogen {

std::size_t tournament_pick(const std::vector<Agent>& agents, std::size_t k,
                            Rng& rng) {
  if (agents.empty()) {
    throw std::invalid_argument("tournament_pick: empty population");
  }
  if (k == 0) {
    k = 1;
  }
  std::size_t best = rng.index(agents.size());
  for (std::size_t i = 1; i < k; ++i) {
    const std::size_t cand = rng.index(agents.size());
    if (agents[cand].fitness() > agents[best].fitness()) {
      best = cand;
    }
  }
  return best;
}

std::vector<std::size_t> select_parents(const std::vector<Agent>& agents,
                                        std::size_t count, std::size_t k,
                                        Rng& rng) {
  std::vector<std::size_t> parents;
  parents.reserve(count);
  for (std::size_t i = 0; i < count; ++i) {
    parents.push_back(tournament_pick(agents, k, rng));
  }
  return parents;
}

}  // namespace evogen
