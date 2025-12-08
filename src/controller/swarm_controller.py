import asyncio
import json
import logging
from typing import List
from model.drone import Drone, DroneStatus
from mavsdk.telemetry import Position

from mavsdk import System

# TODO: Separate mavsdk specifics from controller logic

# configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SwarmController:
    def __init__(self, scenario_spec: str | None = None):
        self.drones = {}
        if scenario_spec:
            self.load_scenario(scenario_spec)

    def load_scenario(self, scenario_spec_path: str) -> None:
        self.scenario_spec = json.loads(open(scenario_spec_path).read())
        if self.scenario_spec.get("drones"):
            for drone_spec in self.scenario_spec["drones"]:
                drone = Drone(
                    drone_id=drone_spec["id"],
                    connection_url=drone_spec["url"],
                )
                self.add_drone(drone)

    def add_drone(self, drone: Drone) -> Drone:
        if drone.drone_id in self.drones:
            logger.error(f"Drone with ID {drone.drone_id} already exists! Skipping.")
            return None
        self.drones[drone.drone_id] = drone
        return drone

    def get_drone_by_id(self, drone_id: str) -> Drone:
        for drone in self.drones.values():
            if drone.drone_id == drone_id:
                return drone
        return None

    def get_drone_index(self, drone: Drone) -> int:
        for index, d in enumerate(self.drones.values()):
            if d == drone:
                return index
        return -1

    def get_all_drones(self) -> List[Drone]:
        return list(self.drones.values())

    def connect_drones_by_ids(self, drone_ids: List[str]) -> None:
        for drone_id in drone_ids:
            asyncio.create_task(self.connect_drone(self.drones[drone_id]))

    def connect_all_drones(self) -> None:
        for drone in self.drones.values():
            try:
                asyncio.create_task(self.connect_drone(drone))
            except Exception as e:
                logger.error(f"Failed to connect to drone {drone.drone_id}: {e}")

    async def connect_drone(self, drone: Drone) -> System:
        # as seen at https://discuss.px4.io/t/mavsdk-multiple-drones-problem/44693/2
        # so I believe port 50051 is just a random starting port so that each System instance
        # uses a different port to avoid conflicts
        drone_system = System(port=50051 + self.get_drone_index(drone))
        system_address = drone.connection_url
        drone_name = drone.drone_id

        try:
            await asyncio.wait_for(
                drone_system.connect(system_address=system_address), timeout=3
            )
            logger.debug(f"Awaiting connection to {drone_name} at {system_address}")
        except asyncio.TimeoutError:
            logger.error(f"Error connecting to {drone_name} at {system_address}!")
            logger.error(f"{drone_name} connection failed!")
            raise Exception(f"Error connecting to {drone_name}.")
        logger.debug(f"Connection await complete to {drone_name}.")

        async for state in drone_system.core.connection_state():
            logger.debug(f"Connection state for {drone_name}:")
            logger.debug(f"{state=}")
            if state.is_connected:
                logger.debug(f"Drone {drone_name} discovered!")
                break
            else:
                logger.error(f"Error awaiting connection state for {drone_name}!")
                logger.error(f"{drone_name} connection failed!")
                raise Exception(f"Error connecting to {drone_name}.")
        logger.debug(f"Connection state for drone {drone_name} complete.")

        logger.debug(
            f"Waiting for drone {drone_name} to have a global position estimate..."
        )
        async for health in drone_system.telemetry.health():
            if health.is_global_position_ok and health.is_home_position_ok:
                logger.debug(f"-- Global position estimate OK for drone {drone_name}")
                break

        drone.mavsdk_system = drone_system
        drone.set_status(DroneStatus.CONNECTED)
        return drone_system
