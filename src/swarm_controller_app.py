#!/usr/bin/env python3
"""Run the Swarm Demo Controller GUI prototype.

Usage:
    python3 swarm_controller.py [optional-map-image-path]

"""

import sys

from controller.swarm_controller import SwarmController
from gui.main_window import run
import os


DEFAULT_MAP = os.path.join(
    os.path.dirname(__file__), "..", "assets", "demo_scenario.json"
)


if __name__ == "__main__":
    # Use provided image path if given, otherwise try the bundled assets/demo_map.png
    scenario_spec_path = sys.argv[1] if len(sys.argv) > 1 else None
    if scenario_spec_path is None and os.path.exists(DEFAULT_MAP):
        scenario_spec_path = os.path.normpath(DEFAULT_MAP)

    controller: SwarmController = SwarmController(scenario_spec_path)
    run(controller)
