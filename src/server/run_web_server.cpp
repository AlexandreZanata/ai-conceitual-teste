#include "server/run_web_server.hpp"

#include "server/experiment_controller.hpp"
#include "server/metrics_hub.hpp"
#include "server/web_server.hpp"

#include <iostream>

namespace evogen {

int run_web_server(const ServeArgs& args, const std::string& version) {
  MetricsHub hub;
  ExperimentController controller(hub, args.results_dir);
  WebServerOptions opts;
  opts.bind_host = args.bind_host;
  opts.port = args.port;
  opts.web_root = args.web_root;
  opts.results_dir = args.results_dir;
  opts.version = version;
  WebServer server(opts, controller, hub);
  std::cout << "EvoGen web listening on http://" << opts.bind_host << ':'
            << opts.port << " web_root=" << opts.web_root << '\n';
  server.listen();
  return 0;
}

}  // namespace evogen
