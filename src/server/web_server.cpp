#include "server/web_server.hpp"

#include "core/experiment_config.hpp"
#include "server/http_util.hpp"

#include <stdexcept>

namespace evogen {

namespace {

void set_json(httplib::Response& res, int status, const nlohmann::json& body) {
  res.status = status;
  res.set_content(body.dump(), "application/json");
}

}  // namespace

WebServer::WebServer(WebServerOptions opts, ExperimentController& controller,
                     MetricsHub& hub)
    : opts_(std::move(opts)), controller_(controller), hub_(hub) {
  register_routes();
}

void WebServer::register_routes() {
  server_.Get("/health", [this](const httplib::Request&, httplib::Response& res) {
    set_json(res, 200,
             {{"status", "ok"}, {"version", opts_.version}});
  });

  server_.Post("/experiments", [this](const httplib::Request& req,
                                      httplib::Response& res) {
    try {
      const auto body = nlohmann::json::parse(req.body);
      const ExperimentConfig cfg = parse_experiment_config(body);
      set_json(res, 201, controller_.start(cfg));
    } catch (const nlohmann::json::exception& ex) {
      set_json(res, 400, error_body("invalid_json", ex.what()));
    } catch (const std::invalid_argument& ex) {
      set_json(res, 400, error_body("invalid_config", ex.what()));
    } catch (const std::runtime_error& ex) {
      set_json(res, 409, error_body("conflict", ex.what()));
    }
  });

  server_.Post("/experiments/:id/pause",
               [this](const httplib::Request& req, httplib::Response& res) {
                 const std::string id = req.path_params.at("id");
                 if (!controller_.pause(id)) {
                   set_json(res, 404, error_body("not_found", "cannot pause"));
                   return;
                 }
                 set_json(res, 200, {{"experiment_id", id}, {"status", "paused"}});
               });

  server_.Post("/experiments/:id/resume",
               [this](const httplib::Request& req, httplib::Response& res) {
                 const std::string id = req.path_params.at("id");
                 if (!controller_.resume(id)) {
                   set_json(res, 404, error_body("not_found", "cannot resume"));
                   return;
                 }
                 set_json(res, 200,
                          {{"experiment_id", id}, {"status", "running"}});
               });

  server_.Post("/experiments/:id/stop",
               [this](const httplib::Request& req, httplib::Response& res) {
                 const std::string id = req.path_params.at("id");
                 if (!controller_.stop(id)) {
                   set_json(res, 404, error_body("not_found", "cannot stop"));
                   return;
                 }
                 set_json(res, 200,
                          {{"experiment_id", id}, {"status", "stopped"}});
               });

  server_.Get("/experiments/:id",
              [this](const httplib::Request& req, httplib::Response& res) {
                try {
                  set_json(res, 200,
                           controller_.snapshot(req.path_params.at("id")));
                } catch (const std::runtime_error& ex) {
                  set_json(res, 404, error_body("not_found", ex.what()));
                }
              });

  server_.WebSocket("/ws/metrics",
                    [this](const httplib::Request&, httplib::ws::WebSocket& ws) {
                      hub_.add(&ws);
                      std::string msg;
                      while (ws.read(msg)) {
                        // Server-push only; ignore client payloads.
                      }
                      hub_.remove(&ws);
                    });

  server_.set_mount_point("/", opts_.web_root);
}

int WebServer::bind() {
  if (opts_.port == 0) {
    bound_port_ = server_.bind_to_any_port(opts_.bind_host);
  } else if (server_.bind_to_port(opts_.bind_host, opts_.port)) {
    bound_port_ = opts_.port;
  } else {
    bound_port_ = -1;
  }
  return bound_port_;
}

void WebServer::listen() {
  if (bound_port_ < 0 && bind() < 0) {
    throw std::runtime_error("failed to bind web server");
  }
  server_.listen_after_bind();
}

void WebServer::start_background() {
  if (bound_port_ < 0 && bind() < 0) {
    throw std::runtime_error("failed to bind web server");
  }
  listen_thread_ = std::thread([this] { server_.listen_after_bind(); });
  server_.wait_until_ready();
}

void WebServer::stop() {
  server_.stop();
  if (listen_thread_.joinable()) {
    listen_thread_.join();
  }
}

}  // namespace evogen
