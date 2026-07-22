#pragma once

#include <nlohmann/json.hpp>
#include <string>

namespace evogen {

inline nlohmann::json error_body(const std::string& code,
                                 const std::string& message) {
  return {{"error", {{"code", code}, {"message", message}}}};
}

}  // namespace evogen
