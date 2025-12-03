<!-- Copilot/AI agent instructions for the Swarm Demo Controller repo -->

# Copilot instructions — Swarm Demo Controller

This file gives concise, actionable guidance so an AI coding agent can be productive immediately in this repository.

- Project focus: small Python-based MAVSDK swarm demo (`swarm_demo.py`) with a PRD for a separate PySide6 GUI prototype (`prd.md`).
- Primary language: Python (requires Python ≥ 3.10).

Quick dev commands

- Create venv: `python3 -m venv .venv`
- Activate: `source ./.venv/bin/activate`
- Install runtime deps (example): `pip3 install mavsdk`
- Run demo: `python3 swarm_demo.py`

High-level architecture & intent

- `swarm_demo.py` is an asyncio-driven MAVSDK script that connects to multiple simulated drones, coordinates missions concurrently, and uses an internal `Sim` container and `DroneStatus` enum to synchronize behavior across tasks.
- `prd.md` describes a GUI prototype (PySide6). The GUI is not present in code — if you add it, keep GUI code separate (for example a `gui/` package) and integrate via an async adapter or `qasync` (do not block the asyncio event loop).

Key patterns to preserve (do not refactor away without reason)

- Async-first: use `asyncio` tasks, `async/await`, and `asyncio.Condition` for per-drone synchronization (`sim.status_conditions`). Example: `set_drone_status(sim, drone, status)` and `wait_for_drone_status(...)`.
- Connection/addressing pattern: drones are connected with unique UDP addresses and the code uses a port-offset pattern for local System instances:
  - Example instantiation: `connect_drone("x500", "udp://0.0.0.0:14540", 0)`
  - Note: `System(port=50051 + drone_index)` is intentionally used to avoid gRPC port conflicts.
- Movement/waiting encapsulation: `drone_goto(...)` sends `action.goto_location(...)` and polls telemetry until position/yaw tolerances are met — preserve this waiting logic when changing motion behavior.
- Telemetry helpers: `get_one_position(drone)` and `get_one_heading(drone)` are used to fetch a single telemetry sample; reuse them rather than duplicating streaming logic.

Where to look for examples

- `swarm_demo.py`: mission tasks (`vtol_mission`, `x3_mission`, `x500_mission`, `xlab550_mission`), connection logic (`connect_drone`), and the orchestrator `run_swarm_demo()`.
- `README.md`: minimal setup instructions (venv, `mavsdk`, run script) — mirror these commands when writing contribution or test instructions.
- `prd.md`: explains intended GUI features (map, drone table, deploy button) — useful if implementing GUI work.

- Integration & external dependencies
- Runtime: `mavsdk` (Python). Tests and CI are not present.
- External runtime expectation: PX4/QGroundControl/Gazebo simulation started separately (see `README.md` step to run `swarm.sh` in PX4 repo) — the script expects the PX4 instances to be reachable at UDP ports 14540-14543.

Guidance for changes and PRs

- Avoid blocking calls in mission code — keep `async`/`await` semantics intact.
- If adding a GUI, do not import `mavsdk` directly into UI callbacks; expose an async adapter (module) that the UI can call into via `asyncio.create_task` or `qasync` integration.
- When adding new drone behaviors, use `DroneStatus` and `set_drone_status`/`wait_for_drone_status` for synchronization instead of ad-hoc sleeps.

Good first edits for an AI helper

- Add a `requirements.txt` with pinned `mavsdk` and optional `PySide6` to make environment setup reproducible.
- Add basic CI that checks `python -m pyflakes` or `python -m pytest` if tests are added.

If anything in this file is ambiguous or you need more specifics (e.g., expected PX4 launch procedure, additional dependencies, or a preferred location for a GUI package), ask the repo owner before making large structural changes.

Files referenced: `swarm_demo.py`, `README.md`, `prd.md`
