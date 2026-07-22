# UC-003 — Observe live experiment (Web)

| Field | Value |
|-------|-------|
| Actor | Researcher (browser) |
| Goal | Watch fitness and controls without stopping the engine |
| Preconditions | Phase 05 server running; experiment started |
| Related | [API-CONTRACT.md](../API-CONTRACT.md) |

## Main flow

1. Open web dashboard (`http://127.0.0.1:8080/`).
2. Start experiment via control panel (`POST /experiments`).
3. Receive WebSocket generation events; charts update.
4. Pause / resume / stop via REST.

## Acceptance

GIVEN a running experiment  
WHEN a generation completes  
THEN a `generation` WS event arrives within **1 second** of completion (local host)

GIVEN a running paced experiment (`generation_delay_ms` > 0)  
WHEN the researcher pauses then resumes then stops  
THEN the process remains stable and status transitions as in [API-CONTRACT.md](../API-CONTRACT.md)
