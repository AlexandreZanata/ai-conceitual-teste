#include "core/experiment_config.hpp"
#include "core/generation_loop.hpp"
#include "core/population.hpp"
#include "core/recorder.hpp"
#include "core/rng.hpp"
#include "core/technique.hpp"
#include "environments/env_factory.hpp"
#include "server/run_web_server.hpp"

#include <cstdlib>
#include <iostream>
#include <stdexcept>
#include <string>

#ifndef EVOGEN_DEFAULT_WEB_ROOT
#define EVOGEN_DEFAULT_WEB_ROOT "web"
#endif

namespace {

void print_help() {
  std::cout
      << "EvoGen " << EVOGEN_VERSION << " — evolutionary research CLI\n"
      << "Usage:\n"
      << "  evogen --config <path> [--technique ID] [--generations N]\n"
      << "  evogen --technique <R0|A|B|C|C-L|A+> [--generations N]\n"
      << "  evogen --serve [--port N] [--bind HOST] [--web-root DIR]\n"
      << "  evogen --help | --version\n";
}

struct CliArgs {
  std::string config_path;
  std::string technique;
  int generations{-1};
  std::string results_dir{"results"};
  bool help{false};
  bool version{false};
  bool serve{false};
  int port{8080};
  std::string bind_host{"127.0.0.1"};
  std::string web_root{EVOGEN_DEFAULT_WEB_ROOT};
};

bool take_value(int& i, int argc, char** argv, std::string& out) {
  if (i + 1 >= argc) {
    return false;
  }
  out = argv[++i];
  return true;
}

bool apply_flag(const std::string& a, CliArgs& args) {
  if (a == "--help" || a == "-h") {
    args.help = true;
    return true;
  }
  if (a == "--version") {
    args.version = true;
    return true;
  }
  if (a == "--serve") {
    args.serve = true;
    return true;
  }
  return false;
}

void require_value(int& i, int argc, char** argv, std::string& out,
                   const char* flag) {
  if (!take_value(i, argc, argv, out)) {
    throw std::runtime_error(std::string(flag) + " needs a value");
  }
}

void apply_valued_option(const std::string& a, int& i, int argc, char** argv,
                         CliArgs& args) {
  if (a == "--config") {
    require_value(i, argc, argv, args.config_path, "--config");
  } else if (a == "--technique") {
    require_value(i, argc, argv, args.technique, "--technique");
  } else if (a == "--results") {
    require_value(i, argc, argv, args.results_dir, "--results");
  } else if (a == "--bind") {
    require_value(i, argc, argv, args.bind_host, "--bind");
  } else if (a == "--web-root") {
    require_value(i, argc, argv, args.web_root, "--web-root");
  } else if (a == "--generations") {
    std::string raw;
    require_value(i, argc, argv, raw, "--generations");
    args.generations = std::stoi(raw);
  } else if (a == "--port") {
    std::string raw;
    require_value(i, argc, argv, raw, "--port");
    args.port = std::stoi(raw);
  } else {
    throw std::runtime_error("unknown argument: " + a);
  }
}

void apply_option(const std::string& a, int& i, int argc, char** argv,
                  CliArgs& args) {
  if (!apply_flag(a, args)) {
    apply_valued_option(a, i, argc, argv, args);
  }
}

CliArgs parse_args(int argc, char** argv) {
  CliArgs args;
  for (int i = 1; i < argc; ++i) {
    apply_option(argv[i], i, argc, argv, args);
  }
  return args;
}

void apply_cli_technique(evogen::ExperimentConfig& cfg,
                         const std::string& technique) {
  if (technique.empty()) {
    return;
  }
  cfg.technique = technique;
  evogen::apply_technique_defaults(cfg);
  evogen::validate_experiment_config(cfg);
}

int run_from_config(const CliArgs& args) {
  std::string path = args.config_path;
  if (path.empty() && !args.technique.empty()) {
    path = "experiments/survival/" + args.technique + ".json";
  }
  auto cfg = evogen::load_experiment_config(path);
  apply_cli_technique(cfg, args.technique);
  std::cout << "seed=" << cfg.seed << " condition=" << cfg.condition
            << " technique=" << cfg.technique << " name=" << cfg.name << '\n';
  evogen::Rng rng(cfg.seed);
  auto population = evogen::Population::create_random(cfg, rng);
  auto env = evogen::make_environment(cfg);
  evogen::Recorder recorder(args.results_dir);
  const auto result =
      evogen::run_generations(population, *env, cfg, recorder, args.generations);
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
    if (args.serve) {
      evogen::ServeArgs serve;
      serve.bind_host = args.bind_host;
      serve.port = args.port;
      serve.web_root = args.web_root;
      serve.results_dir = args.results_dir;
      return evogen::run_web_server(serve, EVOGEN_VERSION);
    }
    if (args.config_path.empty() && args.technique.empty()) {
      std::cerr << "error: --config or --technique is required\n";
      print_help();
      return 1;
    }
    return run_from_config(args);
  } catch (const std::exception& ex) {
    std::cerr << "error: " << ex.what() << '\n';
    return 1;
  }
}
