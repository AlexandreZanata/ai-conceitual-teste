#include "core/experiment_config.hpp"
#include "core/generation_loop.hpp"
#include "core/population.hpp"
#include "core/recorder.hpp"
#include "core/rng.hpp"
#include "environments/function_approx_env.hpp"

#include <cstdlib>
#include <iostream>
#include <stdexcept>
#include <string>

namespace {

void print_help() {
  std::cout
      << "EvoGen " << EVOGEN_VERSION << " — evolutionary research CLI\n"
      << "Usage:\n"
      << "  evogen --config <path> [--generations N] [--results DIR]\n"
      << "  evogen --help\n"
      << "  evogen --version\n";
}

struct CliArgs {
  std::string config_path;
  int generations{-1};
  std::string results_dir{"results"};
  bool help{false};
  bool version{false};
};

bool take_value(int& i, int argc, char** argv, std::string& out) {
  if (i + 1 >= argc) {
    return false;
  }
  out = argv[++i];
  return true;
}

void apply_flag(const std::string& a, CliArgs& args) {
  if (a == "--help" || a == "-h") {
    args.help = true;
  } else if (a == "--version") {
    args.version = true;
  } else {
    throw std::runtime_error("unknown argument: " + a);
  }
}

void apply_option(const std::string& a, int& i, int argc, char** argv,
                  CliArgs& args) {
  if (a == "--config") {
    if (!take_value(i, argc, argv, args.config_path)) {
      throw std::runtime_error("--config needs a path");
    }
  } else if (a == "--generations") {
    std::string raw;
    if (!take_value(i, argc, argv, raw)) {
      throw std::runtime_error("--generations needs an int");
    }
    args.generations = std::stoi(raw);
  } else if (a == "--results") {
    if (!take_value(i, argc, argv, args.results_dir)) {
      throw std::runtime_error("--results needs a directory");
    }
  } else {
    apply_flag(a, args);
  }
}

CliArgs parse_args(int argc, char** argv) {
  CliArgs args;
  for (int i = 1; i < argc; ++i) {
    apply_option(argv[i], i, argc, argv, args);
  }
  return args;
}

int run_from_config(const CliArgs& args) {
  auto cfg = evogen::load_experiment_config(args.config_path);
  std::cout << "seed=" << cfg.seed << " condition=" << cfg.condition
            << " name=" << cfg.name << '\n';
  evogen::Rng rng(cfg.seed);
  auto population = evogen::Population::create_random(cfg, rng);
  evogen::FunctionApproxEnv env(cfg.function_task, cfg.episode_length);
  evogen::Recorder recorder(args.results_dir);
  const auto result =
      evogen::run_generations(population, env, cfg, recorder, args.generations);
  std::cout << "done generations_run=" << result.generations_run
            << " fitness_mean=" << result.last.fitness_mean
            << " fitness_max=" << result.last.fitness_max << '\n';
  return 0;
}

}  // namespace

int main(int argc, char** argv) {
  try {
    const CliArgs args = parse_args(argc, argv);
    if (args.help) {
      print_help();
      return 0;
    }
    if (args.version) {
      std::cout << EVOGEN_VERSION << '\n';
      return 0;
    }
    if (args.config_path.empty()) {
      std::cerr << "error: --config is required\n";
      print_help();
      return 1;
    }
    return run_from_config(args);
  } catch (const std::exception& ex) {
    std::cerr << "error: " << ex.what() << '\n';
    return 1;
  }
}
