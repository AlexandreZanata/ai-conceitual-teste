# UC-003 — Observe live experiment (Web)

| Field | Value |
|-------|-------|
| Actor | Researcher (browser) |
| Goal | Watch fitness and controls without stopping the engine |
| Preconditions | Phase 05 server running; experiment started |
| Related | [API-CONTRACT.md](../API-CONTRACT.md) |

## Main flow

1. Open web dashboard.
2. Start experiment via control panel (POST /experiments).
3. Receive WebSocket generation events; charts update.
4. Pause / resume / stop via REST.

## Acceptance

GIVEN a running experiment  
WHEN a generation completes  
THEN a `generation` WS event arrives within the UI update budget defined in phase 05 TASKS
