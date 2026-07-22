#include "core/recorder.hpp"

#include <algorithm>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <nlohmann/json.hpp>
#include <stdexcept>

namespace evogen {

namespace {

float mean_pairwise_distance(const std::vector<Agent>& agents) {
  if (agents.size() < 2) {
    return 0.0f;
  }
  double sum = 0.0;
  std::size_t pairs = 0;
  for (std::size_t i = 0; i < agents.size(); ++i) {
    for (std::size_t j = i + 1; j < agents.size(); ++j) {
      const auto& a = agents[i].genotype().weights;
      const auto& b = agents[j].genotype().weights;
      double d = 0.0;
      for (std::size_t k = 0; k < a.size(); ++k) {
        const double diff = static_cast<double>(a[k] - b[k]);
        d += diff * diff;
      }
      sum += std::sqrt(d);
      ++pairs;
    }
  }
  return static_cast<float>(sum / static_cast<double>(pairs));
}

}  // namespace

GenerationMetrics compute_metrics(int generation, std::uint64_t seed,
                                  const std::string& condition,
                                  const std::vector<Agent>& agents) {
  GenerationMetrics m;
  m.generation = generation;
  m.seed = seed;
  m.condition = condition;
  float fit_sum = 0.0f;
  float fit_max = agents.front().fitness();
  float lr_sum = 0.0f;
  float mut_sum = 0.0f;
  for (const Agent& a : agents) {
    fit_sum += a.fitness();
    fit_max = std::max(fit_max, a.fitness());
    lr_sum += a.genotype().learning_rate;
    mut_sum += a.genotype().mutation_rate;
  }
  const float n = static_cast<float>(agents.size());
  m.fitness_mean = fit_sum / n;
  m.fitness_max = fit_max;
  m.learning_rate_mean = lr_sum / n;
  m.mutation_rate_mean = mut_sum / n;
  m.diversity_mean = mean_pairwise_distance(agents);
  return m;
}

Recorder::Recorder(std::string results_dir)
    : results_dir_(std::move(results_dir)) {
  std::filesystem::create_directories(results_dir_);
}

void Recorder::log_generation(const GenerationMetrics& metrics) const {
  nlohmann::json j = {{"generation", metrics.generation},
                      {"seed", metrics.seed},
                      {"condition", metrics.condition},
                      {"fitness_mean", metrics.fitness_mean},
                      {"fitness_max", metrics.fitness_max},
                      {"diversity_mean", metrics.diversity_mean},
                      {"learning_rate_mean", metrics.learning_rate_mean},
                      {"mutation_rate_mean", metrics.mutation_rate_mean}};
  const auto path =
      std::filesystem::path(results_dir_) / "metrics.jsonl";
  std::ofstream out(path, std::ios::app);
  if (!out) {
    throw std::runtime_error("cannot write metrics: " + path.string());
  }
  out << j.dump() << '\n';
}

}  // namespace evogen
