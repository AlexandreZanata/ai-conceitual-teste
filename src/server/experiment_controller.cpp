#include "server/experiment_controller.hpp"

#include <atomic>
#include <random>
#include <sstream>
#include <stdexcept>
#include <thread>

namespace evogen {

namespace {

std::string make_experiment_id() {
  static std::atomic<std::uint64_t> seq{0};
  std::mt19937_64 rng{std::random_device{}()};
  std::ostringstream out;
  out << std::hex << rng() << '-' << seq.fetch_add(1);
  return out.str();
}

}  // namespace

std::string to_string(ExperimentStatus status) {
  switch (status) {
    case ExperimentStatus::Idle:
      return "idle";
    case ExperimentStatus::Running:
      return "running";
    case ExperimentStatus::Paused:
      return "paused";
    case ExperimentStatus::Completed:
      return "completed";
    case ExperimentStatus::Stopped:
      return "stopped";
  }
  return "idle";
}

ExperimentController::ExperimentController(MetricsHub& hub,
                                           std::string results_dir)
    : hub_(hub), results_dir_(std::move(results_dir)) {}

ExperimentController::~ExperimentController() {
  stop_requested_ = true;
  cv_.notify_all();
  join_worker();
}

void ExperimentController::join_worker() {
  if (worker_.joinable()) {
    worker_.join();
  }
}

void ExperimentController::wait_if_paused(std::unique_lock<std::mutex>& lock) {
  cv_.wait(lock, [this] {
    return status_ != ExperimentStatus::Paused || stop_requested_;
  });
}

nlohmann::json ExperimentController::start(const ExperimentConfig& cfg) {
  std::lock_guard<std::mutex> lock(mu_);
  if (status_ == ExperimentStatus::Running ||
      status_ == ExperimentStatus::Paused) {
    throw std::runtime_error("experiment already active");
  }
  join_worker();
  active_id_ = make_experiment_id();
  config_ = cfg;
  current_generation_ = -1;
  latest_ = {};
  stop_requested_ = false;
  status_ = ExperimentStatus::Running;
  worker_ = std::thread(&ExperimentController::run_worker, this, cfg,
                        active_id_);
  return {{"experiment_id", active_id_}, {"status", "running"}};
}

bool ExperimentController::pause(const std::string& id) {
  std::lock_guard<std::mutex> lock(mu_);
  if (id != active_id_) {
    return false;
  }
  if (status_ == ExperimentStatus::Paused) {
    return true;
  }
  if (status_ != ExperimentStatus::Running) {
    return false;
  }
  status_ = ExperimentStatus::Paused;
  return true;
}

bool ExperimentController::resume(const std::string& id) {
  std::lock_guard<std::mutex> lock(mu_);
  if (id != active_id_) {
    return false;
  }
  if (status_ == ExperimentStatus::Running) {
    return true;
  }
  if (status_ != ExperimentStatus::Paused) {
    return false;
  }
  status_ = ExperimentStatus::Running;
  cv_.notify_all();
  return true;
}

bool ExperimentController::stop(const std::string& id) {
  {
    std::lock_guard<std::mutex> lock(mu_);
    if (id != active_id_) {
      return false;
    }
    if (status_ == ExperimentStatus::Stopped ||
        status_ == ExperimentStatus::Completed) {
      return true;
    }
    if (status_ != ExperimentStatus::Running &&
        status_ != ExperimentStatus::Paused) {
      return false;
    }
    stop_requested_ = true;
    status_ = ExperimentStatus::Stopped;
  }
  cv_.notify_all();
  join_worker();
  return true;
}

nlohmann::json ExperimentController::snapshot(const std::string& id) const {
  std::lock_guard<std::mutex> lock(mu_);
  if (active_id_.empty() || id != active_id_) {
    throw std::runtime_error("experiment not found");
  }
  return {{"experiment_id", active_id_},
          {"status", to_string(status_)},
          {"generation", current_generation_},
          {"fitness_mean", latest_.fitness_mean},
          {"fitness_max", latest_.fitness_max},
          {"diversity_mean", latest_.diversity_mean},
          {"learning_rate_mean", latest_.learning_rate_mean},
          {"alive_mean", latest_.alive_mean},
          {"condition", config_.condition},
          {"seed", config_.seed}};
}

}  // namespace evogen
