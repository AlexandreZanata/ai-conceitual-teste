#pragma once

#include "core/experiment_config.hpp"
#include "core/recorder.hpp"
#include "server/metrics_hub.hpp"

#include <atomic>
#include <condition_variable>
#include <mutex>
#include <nlohmann/json.hpp>
#include <string>
#include <thread>

namespace evogen {

enum class ExperimentStatus { Idle, Running, Paused, Completed, Stopped };

std::string to_string(ExperimentStatus status);

class ExperimentController {
 public:
  ExperimentController(MetricsHub& hub, std::string results_dir);
  ~ExperimentController();

  ExperimentController(const ExperimentController&) = delete;
  ExperimentController& operator=(const ExperimentController&) = delete;

  nlohmann::json start(const ExperimentConfig& cfg);
  bool pause(const std::string& id);
  bool resume(const std::string& id);
  bool stop(const std::string& id);
  nlohmann::json snapshot(const std::string& id) const;

 private:
  void join_worker();
  void run_worker(ExperimentConfig cfg, std::string id);
  void wait_if_paused(std::unique_lock<std::mutex>& lock);

  MetricsHub& hub_;
  std::string results_dir_;
  mutable std::mutex mu_;
  std::condition_variable cv_;
  std::thread worker_;
  std::string active_id_;
  ExperimentStatus status_{ExperimentStatus::Idle};
  ExperimentConfig config_;
  GenerationMetrics latest_{};
  int current_generation_{-1};
  std::atomic<bool> stop_requested_{false};
};

}  // namespace evogen
