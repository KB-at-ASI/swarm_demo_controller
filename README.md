# Swarm Demo Controller

## Description

This project is used to fly the drones set up in the `swarm_demo.sh` script of the [PX4-Autopilot project](https://github.com/KB-at-ASI/PX4-Autopilot).

## To set up

1. Create virtual environment

   ```bash
   python3 -m venv .venv
   ```

2. Enter virtual environment

   ```bash
   source ./.venv/bin/activate
   ```

3. Install mavsdk (See [mavsdk install guide](https://mavsdk.mavlink.io/main/en/cpp/guide/installation.html) for more info.)

   ```bash
   (.venv) pip3 install mavsdk
   ```

4. Run the swarm.sh script from the PX4 repo. Wait for QGC and Gazebo to start up and all drones to appear.

5. Run the swarm_demo

   ```bash
   (.venv) python3 swarm_demo.py
   ```
