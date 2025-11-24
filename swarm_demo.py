#!/usr/bin/env python3

import asyncio
import logging

from mavsdk import System
from mavsdk.action import OrbitYawBehavior

# configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def connect_drone(drone_name: str, system_address: str, drone_index: int) -> System:
    # as seen at https://discuss.px4.io/t/mavsdk-multiple-drones-problem/44693/2
    # so I believe port 50051 is just a random starting port so that each System instance
    # uses a different port to avoid conflicts
    drone = System(port=50051 + drone_index)
    try:
      await asyncio.wait_for(drone.connect(system_address=system_address), timeout=3)
      logger.info(f"Awaiting connection to {drone_name} at {system_address}")
    except asyncio.TimeoutError:
      logger.error(f"Error connecting to {drone_name} at {system_address}!")
      return None
    logger.info("Connection await complete to {drone_name}.")

    async for state in drone.core.connection_state():
        logger.debug(f"Connection state for {drone_name}:")
        logger.debug(f"{state=}")
        if state.is_connected:
            logger.debug(f"Drone {drone_name} discovered!")
            break
    logger.info(f"Connection state for drone {drone_name} complete.")

    logger.info(f"Waiting for drone {drone_name} to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            logger.debug(f"-- Global position estimate OK for drone {drone_name}")
            break

    return drone


async def vtol_mission(drone_vtol: System):
    logger.info("-- Arming")
    await drone_vtol.action.arm()

    logger.info("--- Taking Off")
    await drone_vtol.action.set_takeoff_altitude(30.0)
    await drone_vtol.action.takeoff()
    await asyncio.sleep(10)

    # This action automatically flies the drone to the orbit radius
    await drone_vtol.action.do_orbit(
        radius_m=18,
        velocity_ms=2,
        yaw_behavior=OrbitYawBehavior.HOLD_FRONT_TANGENT_TO_CIRCLE,
        latitude_deg=32.061467,
        longitude_deg=118.779284,
        absolute_altitude_m=30.0,
    )

    asyncio.sleep(15)


async def x500_mission(drone_x500: System):
    logger.info("-- Arming")
    await drone_x500.action.arm()

    logger.info("--- Taking Off")
    await drone_x500.action.set_takeoff_altitude(25.0)
    await drone_x500.action.takeoff()
    await asyncio.sleep(10)

    logger.info(f"fly to firestation")
    await drone_x500.action.goto_location(
        latitude_deg=32.061566,
        longitude_deg=118.779284,
        absolute_altitude_m=30.0,
        yaw_deg=120.0
    )    
    await asyncio.sleep(30)

    logger.info(f"look in firestation")
    await drone_x500.action.goto_location(
        latitude_deg=32.061566,
        longitude_deg=118.779284,
        absolute_altitude_m=2.8,
        yaw_deg=200.0
    )

    await asyncio.sleep(30)

    logger.info(f"fly in firestation")
    await drone_x500.action.goto_location(
        latitude_deg=32.061467,
        longitude_deg=118.779241,
        absolute_altitude_m=3.0,
        yaw_deg=200.0
    )

    logger.info(f"look around firestation")
    await drone_x500.action.goto_location(
        latitude_deg=32.061467,
        longitude_deg=118.779241,
        absolute_altitude_m=3.0,
        yaw_deg=300.0
    )

    await asyncio.sleep(10)

    await drone_x500.action.goto_location(
        latitude_deg=32.061467,
        longitude_deg=118.779241,
        absolute_altitude_m=3.0,
        yaw_deg=60.0
    )

    await asyncio.sleep(10)

    await drone_x500.action.goto_location(
        latitude_deg=32.061464,
        longitude_deg=118.779241,
        absolute_altitude_m=2.8,
        yaw_deg=170.0
    )

    await asyncio.sleep(10)

    logger.info(f"fly out firestation")
    await drone_x500.action.goto_location(
        latitude_deg=32.061398,
        longitude_deg=118.779249,
        absolute_altitude_m=2.6,
        yaw_deg=170.0
    )

    await asyncio.sleep(15)

    await drone_x500.action.return_to_launch()

    logger.info("--- Landing")


async def run_swarm_demo():
    
    # Connect to all drones
    drone_x500 = await connect_drone("x500", "udp://0.0.0.0:14540", 0)
    if drone_x500 is None:
        logger.error("X500 drone connection failed, aborting swarm demo.")
        return
    else:
        logger.info("X500 initialized, starting mission...")

    drone_vtol = await connect_drone("vtol", "udp://0.0.0.0:14541", 1)
    if drone_vtol is None:
        logger.error("VTOL drone connection failed, aborting swarm demo.")
        return
    else:
        logger.info("VTOL initialized, starting mission...")

    await vtol_mission(drone_vtol)
    await x500_mission(drone_x500)


if __name__ == "__main__":
    asyncio.run(run_swarm_demo())