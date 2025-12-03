# Product Requirements Document (PRD)

**Product Name:** Drone Swarm Controller — Prototype GUI

# Product Requirements Document (PRD)

**Product Name:** Drone Swarm Controller — Prototype GUI

**Author:** KB-at-ASI
**Date:** 2025-12-03
**Version:** 0.2

---

## Purpose

Lightweight PySide6 GUI prototype for visualizing a small drone swarm, selecting mission locations on a static map image, and exercising UI interactions for future integration with flight-control code. The prototype is intentionally disconnected from `mavsdk`; the "Deploy" action is a stub that logs selections.

## Scope

Implemented features:

- Top map view with plotted drone markers and a lower-right inset showing live latitude/longitude under the cursor.
- Bottom `DroneListWidget` containing a full-width drone table, a `Deploy Swarm` button, and a status label for non-location messages.
- Click-to-select mission location: draws a mission circle and connecting lines from selected drones to the mission point.
- Mouse-wheel zoom (centered on cursor) with clamped zoom range.
- Vertical `QSplitter` between the map (top) and drone list (bottom); user can resize panes.

Excluded:

- Real drone communication and real telemetry streams (these are to be added later via an async adapter).

## Key Files / Components

- `src/gui/map_widget.py` — `MapWidget`: background image, plotting, lat/lon inset, zoom, and mission visuals.
- `src/gui/drone_list.py` — `DroneListWidget`: encapsulates the drone table (columns: `Name/ID`, `Role`, `Mode`), deploy button, and status label.
- `src/gui/main.py` — main window composition (vertical splitter, wiring signals).
- `src/run_gui.py` — launcher (defaults to `assets/demo_map.png` when present).
- `requirements.txt` — runtime dependencies (`PySide6`, optional `numpy`).

## User Interactions

- Hover map: lower-right inset shows latitude/longitude (map owns this display; the drone list status is reserved for mission/other messages).
- Wheel: zoom in/out (bounded zoom, centered under cursor).
- Click map: set mission location; map draws a circle and the `DroneListWidget` status updates with the mission coordinates.
- Select rows in the drone table: selected drones are highlighted on the map and lines are drawn from those drones to the mission point (if set).
- Deploy Swarm button: prints a stub message with selected drones and mission location to stdout.

## Data and Mapping

- Sample drones are hard-coded in `src/gui/main.py` and mirror positions used in `swarm_demo.py` for prototype purposes.
- `MapWidget.bounds` contains `(min_lat, max_lat, min_lon, max_lon)` and is used for a simple linear mapping between image pixels and lat/lon. Adjust these bounds to match your map image.

## How to Run (developer)

1. Create and activate a venv:

```bash
python3 -m venv .venv
source ./.venv/bin/activate
```

1. Install dependencies:

````bash
# Product Requirements Document (PRD)

**Product Name:** Drone Swarm Controller — Prototype GUI

**Author:** KB-at-ASI
**Date:** 2025-12-03
**Version:** 0.2

---

## Purpose

Lightweight PySide6 GUI prototype for visualizing a small drone swarm, selecting mission locations on a static map image, and exercising UI interactions for future integration with flight-control code. The prototype is intentionally disconnected from `mavsdk`; the "Deploy" action is a stub that logs selections.

## Scope

Implemented features:

- Top map view with plotted drone markers and a lower-right inset showing live latitude/longitude under the cursor.
- Bottom `DroneListWidget` containing a full-width drone table, a `Deploy Swarm` button, and a status label for non-location messages.
- Click-to-select mission location: draws a mission circle and connecting lines from selected drones to the mission point.
- Mouse-wheel zoom (centered on cursor) with clamped zoom range.
- Vertical `QSplitter` between the map (top) and drone list (bottom); user can resize panes.

Excluded:

- Real drone communication and real telemetry streams (these are to be added later via an async adapter).

## Key Files / Components

- `src/gui/map_widget.py` — `MapWidget`: background image, plotting, lat/lon inset, zoom, and mission visuals.
- `src/gui/drone_list.py` — `DroneListWidget`: encapsulates the drone table (columns: `Name/ID`, `Role`, `Mode`), deploy button, and status label.
- `src/gui/main.py` — main window composition (vertical splitter, wiring signals).
- `src/run_gui.py` — launcher (defaults to `assets/demo_map.png` when present).
- `requirements.txt` — runtime dependencies (`PySide6`, optional `numpy`).

## User Interactions

- Hover map: lower-right inset shows latitude/longitude (map owns this display; the drone list status is reserved for mission/other messages).
- Wheel: zoom in/out (bounded zoom, centered under cursor).
- Click map: set mission location; map draws a circle and the `DroneListWidget` status updates with the mission coordinates.
- Select rows in the drone table: selected drones are highlighted on the map and lines are drawn from those drones to the mission point (if set).
- Deploy Swarm button: prints a stub message with selected drones and mission location to stdout.

## Data and Mapping

- Sample drones are hard-coded in `src/gui/main.py` and mirror positions used in `swarm_demo.py` for prototype purposes.
- `MapWidget.bounds` contains `(min_lat, max_lat, min_lon, max_lon)` and is used for a simple linear mapping between image pixels and lat/lon. Adjust these bounds to match your map image.

## How to Run (developer)

1. Create and activate a venv:

```bash
python3 -m venv .venv
source ./.venv/bin/activate
````

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the GUI (defaults to `assets/demo_map.png` if present):

```bash
python3 src/run_gui.py
```

## Developer Notes / Conventions

- Keep UI code async-friendly. If integrating `mavsdk`, implement an async adapter module and call it from the GUI using `asyncio.create_task` or `qasync` so the Qt event loop is not blocked.
- Preserve `MapWidget`'s separation between motion visualization and control logic when porting mission behaviors.
- Use `DroneListWidget.populate()` to update the table; the widget configures columns to stretch and fill available width.

## Next Improvements

- Wire an async adapter to call real `mavsdk` missions (non-blocking).
- Persist splitter sizes and user preferences between runs.
- Support georeferenced maps and better map projections (instead of simple linear mapping).
- Add unit/UI tests and a small CI job running a static checker.

---

## Purpose

Lightweight PySide6 GUI prototype for visualizing a small drone swarm, selecting mission locations on a static map image, and exercising UI interactions for future integration with real flight-control code. This prototype is intentionally disconnected from `mavsdk` — the "Deploy" action is a stub that logs selections.

## Scope

Implemented prototype features:

- Top map view with plotted drone markers and a lower-right inset showing live lat/lon under the cursor.
- Bottom `DroneListWidget` containing a full-width drone table, a `Deploy Swarm` button, and a status label for non-location messages.
- Click-to-select mission location: draws a mission circle and connecting lines from selected drones to the mission point.
- Mouse-wheel zoom (centered on cursor).
- A vertical `QSplitter` between the map (top) and drone list (bottom); user can resize panes.

Excluded: real drone communication and real telemetry streams (these will be added later via an async adapter).

## Key Files / Components

- `src/gui/map_widget.py`: `MapWidget` — background image, plotting, lat/lon inset, zoom, mission visuals.
- `src/gui/drone_list.py`: `DroneListWidget` — encapsulates the drone table (columns: `Name/ID`, `Role`, `Mode`), deploy button, and a status label.
- `src/gui/main.py`: main window composition (vertical splitter, wiring signals).
- `src/run_gui.py`: launcher that defaults to `assets/demo_map.png` when available.
- `requirements.txt`: runtime dependencies (`PySide6`, optional `numpy`).

## User Interactions

- Hover map: lower-right inset shows latitude/longitude (does not update the drone list status).
- Wheel: zoom in/out (bounded zoom range).
- Click map: set mission location; a circle is drawn and `DroneListWidget` status shows the mission coordinates.
- Select rows in the drone table: selected drones are highlighted on the map and lines are drawn from those drones to the mission point (if set).
- Deploy Swarm button: prints a stub message with selected drones and mission location to stdout.

## Data and Mapping

- Sample drones are hard-coded in `src/gui/main.py` and correspond to coordinates used in `swarm_demo.py`.
- `MapWidget.bounds` contains `(min_lat, max_lat, min_lon, max_lon)` and is used for linear mapping between image pixels and lat/lon. Adjust these values to fit your map image.

## How to Run (developer)

1. Create and activate a venv:

```
python3 -m venv .venv
source ./.venv/bin/activate
```

2. Install dependencies:

```
pip install -r requirements.txt
```

3. Run the GUI (defaults to `assets/demo_map.png` if present):

```
python3 src/run_gui.py
```

## Developer Notes / Conventions

- Keep UI code async-friendly: if integrating `mavsdk`, implement an async adapter module and call it from the GUI using `asyncio.create_task` or `qasync` to avoid blocking the Qt event loop.
- Preserve `MapWidget`'s `drone_goto`-style waiting logic when porting mission behaviors into the app — the prototype separates motion visualization from control logic.
- Use `DroneListWidget.populate()` to update the table; the widget ensures columns stretch to fill available width.

## Next Improvements

- Wire an async adapter to call actual `mavsdk` missions (non-blocking).
- Add persistent splitter sizes and user preferences.
- Support georeferenced maps and better map projections (instead of linear mapping).
- Add unit/UI tests and a small CI job running a static checker.
