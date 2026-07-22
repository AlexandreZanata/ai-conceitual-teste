#include <catch2/catch_test_macros.hpp>

#include "server/experiment_controller.hpp"
#include "server/metrics_hub.hpp"
#include "server/web_server.hpp"

#include <chrono>
#include <filesystem>
#include <httplib.h>
#include <nlohmann/json.hpp>
#include <string>
#include <thread>

namespace {

struct TestServer {
  evogen::MetricsHub hub;
  evogen::ExperimentController controller;
  evogen::WebServer server;
  int port{-1};

  TestServer()
      : controller(hub, results_dir()),
        server(make_opts(), controller, hub) {
    port = server.bind();
    REQUIRE(port > 0);
    server.start_background();
  }

  ~TestServer() { server.stop(); }

  static std::string results_dir() {
    const auto dir =
        std::filesystem::temp_directory_path() / "evogen_web_test";
    std::filesystem::remove_all(dir);
    return dir.string();
  }

  static evogen::WebServerOptions make_opts() {
    evogen::WebServerOptions opts;
    opts.bind_host = "127.0.0.1";
    opts.port = 0;
    opts.web_root = EVOGEN_TEST_WEB_ROOT;
    opts.version = "0.1.0-test";
    return opts;
  }

  std::string base() const { return "http://127.0.0.1:" + std::to_string(port); }
};

}  // namespace

// Contract: docs/API-CONTRACT.md GET /health
TEST_CASE("given_server_when_get_health_then_ok", "[web][health]") {
  TestServer ts;
  httplib::Client cli(ts.base());
  const auto res = cli.Get("/health");
  REQUIRE(res);
  REQUIRE(res->status == 200);
  REQUIRE(res->body.find("\"status\":\"ok\"") != std::string::npos);
  REQUIRE(res->body.find("version") != std::string::npos);
}

// Contract: docs/API-CONTRACT.md static web/
TEST_CASE("given_server_when_get_index_then_html", "[web][static]") {
  TestServer ts;
  httplib::Client cli(ts.base());
  const auto res = cli.Get("/");
  REQUIRE(res);
  REQUIRE(res->status == 200);
  REQUIRE(res->body.find("EvoGen") != std::string::npos);
}

// Contract: API-CONTRACT + UC-003 — start and WS generation event
TEST_CASE("given_start_when_generation_then_ws_event", "[web][ws][UC-003]") {
  TestServer ts;
  httplib::ws::WebSocketClient ws("ws://127.0.0.1:" + std::to_string(ts.port) +
                                  "/ws/metrics");
  ws.set_read_timeout(5, 0);
  REQUIRE(ws.connect());

  httplib::Client cli(ts.base());
  const std::string body = R"({
    "condition":"A","environment":"function_approx","function_task":"xor",
    "episode_length":4,"population_size":6,"max_generations":3,"seed":3,
    "inheritance_mode":"Darwinian","initial_mutation_rate":0.05,
    "initial_learning_rate":0.0,"genome_size":4,"generation_delay_ms":30
  })";
  const auto started = cli.Post("/experiments", body, "application/json");
  REQUIRE(started);
  REQUIRE(started->status == 201);

  std::string msg;
  bool got_generation = false;
  for (int i = 0; i < 5; ++i) {
    if (ws.read(msg) && msg.find("\"type\":\"generation\"") != std::string::npos) {
      got_generation = true;
      break;
    }
  }
  REQUIRE(got_generation);
  REQUIRE(msg.find("fitness_mean") != std::string::npos);
  REQUIRE(msg.find("experiment_id") != std::string::npos);

  const auto id_json = nlohmann::json::parse(started->body);
  const std::string id = id_json.at("experiment_id").get<std::string>();
  const auto stopped = cli.Post("/experiments/" + id + "/stop", "",
                                "application/json");
  REQUIRE(stopped);
  REQUIRE(stopped->status == 200);
  ws.close();
}

// Contract: lifecycle via REST
TEST_CASE("given_experiment_when_pause_resume_stop_then_ok", "[web][lifecycle]") {
  TestServer ts;
  httplib::Client cli(ts.base());
  const std::string body = R"({
    "condition":"A","function_task":"xor","episode_length":4,
    "population_size":6,"max_generations":50,"seed":11,"genome_size":4,
    "generation_delay_ms":40
  })";
  const auto started = cli.Post("/experiments", body, "application/json");
  REQUIRE(started);
  REQUIRE(started->status == 201);
  const std::string id =
      nlohmann::json::parse(started->body).at("experiment_id").get<std::string>();

  const auto pause_res = cli.Post("/experiments/" + id + "/pause", "",
                                  "application/json");
  REQUIRE(pause_res);
  REQUIRE(pause_res->status == 200);
  REQUIRE(cli.Post("/experiments/" + id + "/resume", "", "application/json")
              ->status == 200);
  REQUIRE(cli.Post("/experiments/" + id + "/stop", "", "application/json")
              ->status == 200);
}
