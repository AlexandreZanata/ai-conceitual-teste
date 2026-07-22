#pragma once

#include <mutex>
#include <string>
#include <vector>

namespace httplib {
namespace ws {
class WebSocket;
}
}  // namespace httplib

namespace evogen {

/** Fan-out of generation JSON events to active WebSocket clients. */
class MetricsHub {
 public:
  void add(httplib::ws::WebSocket* ws);
  void remove(httplib::ws::WebSocket* ws);
  void publish(const std::string& json_text);
  std::size_t client_count() const;

 private:
  mutable std::mutex mu_;
  std::vector<httplib::ws::WebSocket*> clients_;
};

}  // namespace evogen
