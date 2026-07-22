#include "environments/survival_arena_env.hpp"

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <random>
#include <stdexcept>

namespace evogen {

namespace {

constexpr float kFoodGain = 0.35f;
constexpr float kHazardHit = 0.4f;
constexpr float kAliveBonus = 0.01f;
constexpr std::size_t kStimDim = 8;

std::size_t idx(std::size_t w, int x, int y) {
  return static_cast<std::size_t>(y) * w + static_cast<std::size_t>(x);
}

}  // namespace

SurvivalArenaEnv::SurvivalArenaEnv(std::size_t grid_w, std::size_t grid_h,
                                   float food_density, float energy_drain,
                                   float hazard_rate, float start_energy,
                                   std::size_t episode_ticks)
    : grid_w_(grid_w),
      grid_h_(grid_h),
      food_density_(food_density),
      energy_drain_(energy_drain),
      hazard_rate_(hazard_rate),
      start_energy_(start_energy),
      episode_ticks_(episode_ticks) {
  if (grid_w_ == 0 || grid_h_ == 0) {
    throw std::invalid_argument("grid_w/grid_h must be > 0");
  }
  if (episode_ticks_ == 0) {
    throw std::invalid_argument("episode_ticks must be > 0");
  }
  if (start_energy_ <= 0.0f) {
    throw std::invalid_argument("start_energy must be > 0");
  }
}

void SurvivalArenaEnv::place_cells(std::uint64_t seed) {
  food_.assign(grid_w_ * grid_h_, 0.0f);
  hazard_.assign(grid_w_ * grid_h_, 0.0f);
  std::mt19937_64 eng(seed);
  std::uniform_real_distribution<float> u(0.0f, 1.0f);
  for (std::size_t i = 0; i < food_.size(); ++i) {
    if (u(eng) < food_density_) {
      food_[i] = 1.0f;
    }
    if (u(eng) < hazard_rate_) {
      hazard_[i] = 1.0f;
    }
  }
}

void SurvivalArenaEnv::reset_episode(std::uint64_t episode_seed) {
  place_cells(episode_seed);
  std::mt19937_64 eng(episode_seed ^ 0x9e3779b97f4a7c15ULL);
  x_ = static_cast<int>(eng() % grid_w_);
  y_ = static_cast<int>(eng() % grid_h_);
  energy_ = start_energy_;
  alive_ = true;
  ticks_done_ = 0;
  food_[idx(grid_w_, x_, y_)] = 0.0f;
  hazard_[idx(grid_w_, x_, y_)] = 0.0f;
}

bool SurvivalArenaEnv::episode_done() const {
  return !alive_ || ticks_done_ >= episode_ticks_;
}

bool SurvivalArenaEnv::in_bounds(int nx, int ny) const {
  return nx >= 0 && ny >= 0 && nx < static_cast<int>(grid_w_) &&
         ny < static_cast<int>(grid_h_);
}

float SurvivalArenaEnv::cell_food(int cx, int cy) const {
  if (!in_bounds(cx, cy)) {
    return 0.0f;
  }
  return food_[idx(grid_w_, cx, cy)];
}

float SurvivalArenaEnv::cell_hazard(int cx, int cy) const {
  if (!in_bounds(cx, cy)) {
    return 0.0f;
  }
  return hazard_[idx(grid_w_, cx, cy)];
}

std::vector<float> SurvivalArenaEnv::observe() const {
  return {energy_ / start_energy_,
          cell_food(x_, y_ - 1),
          cell_food(x_ + 1, y_),
          cell_food(x_, y_ + 1),
          cell_food(x_ - 1, y_),
          cell_hazard(x_, y_),
          season_,
          1.0f};
}

int SurvivalArenaEnv::action_from_response(float response) const {
  if (response > 1.0f) {
    return 0;  // N
  }
  if (response > 0.33f) {
    return 1;  // E
  }
  if (response > -0.33f) {
    return 4;  // stay
  }
  if (response > -1.0f) {
    return 3;  // W
  }
  return 2;  // S
}

float SurvivalArenaEnv::step(float response) {
  if (episode_done()) {
    return 0.0f;
  }
  const float before = energy_;
  energy_ -= energy_drain_;
  const int act = action_from_response(response);
  static const int dx[5] = {0, 1, 0, -1, 0};
  static const int dy[5] = {-1, 0, 1, 0, 0};
  const int nx = x_ + dx[act];
  const int ny = y_ + dy[act];
  if (in_bounds(nx, ny)) {
    x_ = nx;
    y_ = ny;
  }
  const std::size_t i = idx(grid_w_, x_, y_);
  if (food_[i] > 0.0f) {
    energy_ += kFoodGain;
    food_[i] = 0.0f;
  }
  if (hazard_[i] > 0.0f) {
    energy_ -= kHazardHit;
  }
  ++ticks_done_;
  if (energy_ <= 0.0f) {
    energy_ = 0.0f;
    alive_ = false;
    return energy_ - before;
  }
  return (energy_ - before) + kAliveBonus;
}

float SurvivalArenaEnv::target_of(const std::vector<float>& stimulus) const {
  if (stimulus.size() < kStimDim) {
    return 0.0f;
  }
  // Prefer move toward strongest adjacent food signal.
  const float foods[4] = {stimulus[1], stimulus[2], stimulus[3], stimulus[4]};
  int best = 4;
  float best_v = 0.0f;
  for (int a = 0; a < 4; ++a) {
    if (foods[a] > best_v) {
      best_v = foods[a];
      best = a;
    }
  }
  static const float bins[5] = {1.5f, 0.66f, -1.5f, -0.66f, 0.0f};
  return bins[best];
}

std::vector<std::vector<float>> SurvivalArenaEnv::episode() const {
  return {};
}

float SurvivalArenaEnv::evaluate(float response,
                                 const std::vector<float>& stimulus) const {
  (void)response;
  (void)stimulus;
  return 0.0f;
}

}  // namespace evogen
