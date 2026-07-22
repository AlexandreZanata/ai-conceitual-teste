#pragma once

#include "environments/environment.hpp"

#include <cstddef>
#include <cstdint>
#include <vector>

namespace evogen {

/**
 * T2 Trait Forge Arena — survival grid (phase 06).
 *
 * Rules (immutable):
 *   - Agent stays in bounds (wall = no move).
 *   - Each tick drains `energy_drain`; death at energy ≤ 0 ends episode.
 *   - Food cell: +food_gain energy, food removed; hazard cell: −hazard_hit.
 *   - Actions: discrete 5-way from scalar response (N, E, S, W, stay).
 *
 * Variables (config): grid_w/h, food_density, energy_drain, hazard_rate,
 *   start_energy, episode_ticks.
 *
 * Reward: Δenergy this tick + small alive bonus (0.01) while alive.
 * Direct-learn target: preferred response bin toward nearest visible food.
 *
 * Stimulus (8 dims): energy_norm, food_N/E/S/W, hazard_here, season_stub, bias.
 */
class SurvivalArenaEnv final : public Environment {
 public:
  SurvivalArenaEnv(std::size_t grid_w, std::size_t grid_h, float food_density,
                   float energy_drain, float hazard_rate, float start_energy,
                   std::size_t episode_ticks);

  bool interactive() const override { return true; }
  void reset_episode(std::uint64_t episode_seed) override;
  bool episode_done() const override;
  std::vector<float> observe() const override;
  float step(float response) override;
  bool agent_alive() const override { return alive_; }

  std::vector<std::vector<float>> episode() const override;
  float target_of(const std::vector<float>& stimulus) const override;
  float evaluate(float response,
                 const std::vector<float>& stimulus) const override;

  float energy() const { return energy_; }
  int x() const { return x_; }
  int y() const { return y_; }
  std::size_t ticks_done() const { return ticks_done_; }

  void set_season(float season) override { season_ = season; }
  float season() const override { return season_; }
  void set_hazard_rate(float rate) override { hazard_rate_ = rate; }
  float hazard_rate() const override { return hazard_rate_; }
  void set_food_density(float density) override { food_density_ = density; }
  float food_density() const override { return food_density_; }

 private:
  int action_from_response(float response) const;
  void place_cells(std::uint64_t seed);
  bool in_bounds(int nx, int ny) const;
  float cell_food(int cx, int cy) const;
  float cell_hazard(int cx, int cy) const;

  std::size_t grid_w_;
  std::size_t grid_h_;
  float food_density_;
  float energy_drain_;
  float hazard_rate_;
  float start_energy_;
  std::size_t episode_ticks_;
  std::vector<float> food_;
  std::vector<float> hazard_;
  int x_{0};
  int y_{0};
  float energy_{0};
  bool alive_{true};
  std::size_t ticks_done_{0};
  float season_{0.0f};
};

}  // namespace evogen
