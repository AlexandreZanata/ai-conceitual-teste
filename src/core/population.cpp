#include "core/population.hpp"

#include "core/crossover.hpp"
#include "core/mutation.hpp"
#include "core/selection.hpp"

#include <algorithm>
#include <numeric>
#include <stdexcept>
#include <utility>

namespace evogen {

Population::Population(std::vector<Agent> agents) : agents_(std::move(agents)) {
  if (agents_.empty()) {
    throw std::invalid_argument("Population requires at least one agent");
  }
}

Population Population::create_random(const ExperimentConfig& cfg, Rng& rng) {
  std::vector<Agent> agents;
  agents.reserve(cfg.population_size);
  for (std::size_t i = 0; i < cfg.population_size; ++i) {
    agents.emplace_back(rng.make_genome(cfg.genome_size, cfg.initial_mutation_rate,
                                        cfg.initial_learning_rate));
  }
  return Population(std::move(agents));
}

void Population::evolve(const ExperimentConfig& cfg, Rng& rng) {
  if (!cfg.enable_genetic_reproduction) {
    return;
  }
  const std::size_t n = agents_.size();
  std::vector<std::size_t> order(n);
  std::iota(order.begin(), order.end(), 0);
  std::sort(order.begin(), order.end(), [this](std::size_t a, std::size_t b) {
    return agents_[a].fitness() > agents_[b].fitness();
  });

  std::vector<Agent> next;
  next.reserve(n);
  const std::size_t elites = std::min(cfg.elite_count, n);
  for (std::size_t i = 0; i < elites; ++i) {
    next.push_back(agents_[order[i]]);
    next.back().reset_fitness();
  }
  while (next.size() < n) {
    const auto p1 = tournament_pick(agents_, cfg.tournament_k, rng);
    const auto p2 = tournament_pick(agents_, cfg.tournament_k, rng);
    Genome child =
        uniform_crossover(agents_[p1].genome(), agents_[p2].genome(), rng);
    mutate_genome(child, rng);
    next.emplace_back(std::move(child));
  }
  agents_ = std::move(next);
}

}  // namespace evogen
