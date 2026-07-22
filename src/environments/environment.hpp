#pragma once

#include <cstdint>
#include <vector>

namespace evogen {

/**
 * Environment port: batch (T1) or interactive (T2 survival) episodes.
 * Reward formula is defined by each concrete environment.
 */
class Environment {
 public:
  virtual ~Environment() = default;

  /** Batch path (function approx): full stimulus list upfront. */
  virtual std::vector<std::vector<float>> episode() const = 0;
  virtual float target_of(const std::vector<float>& stimulus) const = 0;
  virtual float evaluate(float response,
                         const std::vector<float>& stimulus) const = 0;

  /** Interactive path (survival arena). Defaults keep T1 unchanged. */
  virtual bool interactive() const { return false; }
  virtual void reset_episode(std::uint64_t episode_seed) { (void)episode_seed; }
  virtual bool episode_done() const { return true; }
  virtual std::vector<float> observe() const { return {}; }
  virtual float step(float response) {
    (void)response;
    return 0.0f;
  }
  virtual bool agent_alive() const { return true; }

  /** T3 / TB-DRIFT knobs (no-op on batch T1 environments). */
  virtual void set_season(float season) { (void)season; }
  virtual float season() const { return 0.0f; }
  virtual void set_hazard_rate(float rate) { (void)rate; }
  virtual float hazard_rate() const { return 0.0f; }
  virtual void set_food_density(float density) { (void)density; }
  virtual float food_density() const { return 0.0f; }
};

}  // namespace evogen
