#!/usr/bin/env python3
"""Run the Swarm Demo Controller GUI prototype.

Usage:
    python3 swarm_controller.py [optional-scenario-file]

"""

import sys

from controller.swarm_controller import SwarmController
from gui.main_window import run
from utils.file_utils import resolve_file_path


if __name__ == "__main__":
    DEFAULT_SCENARIO_FILE = "assets/demo_scenario.json"

    # Use provided image path if given, otherwise try the bundled assets/demo_map.png
    scenario_spec_path = sys.argv[1] if len(sys.argv) > 1 else None

    if scenario_spec_path is None:
        scenario_spec_path = DEFAULT_SCENARIO_FILE

    scenario_spec_path = resolve_file_path(scenario_spec_path)

    controller: SwarmController = SwarmController(scenario_spec_path)
    run(controller)
