#pragma once

#include <string>

namespace evogen {

struct ServeArgs {
  std::string bind_host{"127.0.0.1"};
  int port{8080};
  std::string web_root;
  std::string results_dir{"results"};
};

int run_web_server(const ServeArgs& args, const std::string& version);

}  // namespace evogen
