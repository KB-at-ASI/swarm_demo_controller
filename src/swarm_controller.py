#!/usr/bin/env python3
"""Run the Swarm Demo Controller GUI prototype.

Usage:
    python3 swarm_controller.py [optional-map-image-path]

"""

import sys

from gui.main import run
import os


DEFAULT_MAP = os.path.join(os.path.dirname(__file__), "..", "assets", "demo_map.png")


if __name__ == "__main__":
    # Use provided image path if given, otherwise try the bundled assets/demo_map.png
    img = sys.argv[1] if len(sys.argv) > 1 else None
    if img is None and os.path.exists(DEFAULT_MAP):
        img = os.path.normpath(DEFAULT_MAP)
    run(img)
