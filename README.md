# To set up

1. Create virtual environment

```
python3 -m venv .venv
```

2. Enter virtual environment

```
source ./.venv/bin/activate
```

3. Install mavsdk
   (See https://mavsdk.mavlink.io/main/en/cpp/guide/installation.html for more info.)

```
pip3 install mavsdk
```

4. Run the swarm.sh script from the PX4 repo. Wait for QGC and Gazebo to start up and all drones to appear.

5. Run the swarm_demo

```
python3 swarm_demo.py
```
