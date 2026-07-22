#pragma once

#include "server/experiment_controller.hpp"
#include "server/metrics_hub.hpp"

#include <httplib.h>
#include <string>
#include <thread>

namespace evogen {

struct WebServerOptions {
  std::string bind_host{"127.0.0.1"};
  int port{8080};
  std::string web_root{"web"};
  std::string results_dir{"results"};
  std::string version{"0.1.0"};
};

class WebServer {
 public:
  WebServer(WebServerOptions opts, ExperimentController& controller,
            MetricsHub& hub);

  /** Bind host:port (port 0 → ephemeral). Returns bound port or -1. */
  int bind();
  void listen();
  void start_background();
  void stop();
  int bound_port() const { return bound_port_; }
  bool is_running() const { return server_.is_running(); }

 private:
  void register_routes();

  WebServerOptions opts_;
  ExperimentController& controller_;
  MetricsHub& hub_;
  httplib::Server server_;
  std::thread listen_thread_;
  int bound_port_{-1};
};

}  // namespace evogen
