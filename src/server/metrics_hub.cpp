#include "server/metrics_hub.hpp"

#include <algorithm>
#include <httplib.h>

namespace evogen {

void MetricsHub::add(httplib::ws::WebSocket* ws) {
  std::lock_guard<std::mutex> lock(mu_);
  clients_.push_back(ws);
}

void MetricsHub::remove(httplib::ws::WebSocket* ws) {
  std::lock_guard<std::mutex> lock(mu_);
  clients_.erase(std::remove(clients_.begin(), clients_.end(), ws),
                 clients_.end());
}

void MetricsHub::publish(const std::string& json_text) {
  std::vector<httplib::ws::WebSocket*> snapshot;
  {
    std::lock_guard<std::mutex> lock(mu_);
    snapshot = clients_;
  }
  std::vector<httplib::ws::WebSocket*> dead;
  for (httplib::ws::WebSocket* ws : snapshot) {
    if (!ws->is_open() || !ws->send(json_text)) {
      dead.push_back(ws);
    }
  }
  if (dead.empty()) {
    return;
  }
  std::lock_guard<std::mutex> lock(mu_);
  for (httplib::ws::WebSocket* ws : dead) {
    clients_.erase(std::remove(clients_.begin(), clients_.end(), ws),
                   clients_.end());
  }
}

std::size_t MetricsHub::client_count() const {
  std::lock_guard<std::mutex> lock(mu_);
  return clients_.size();
}

}  // namespace evogen
