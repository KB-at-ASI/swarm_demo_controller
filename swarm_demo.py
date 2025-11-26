#!/usr/bin/env python3

import asyncio
import logging

from mavsdk import System
from mavsdk.telemetry import Position
from mavsdk.action import OrbitYawBehavior

# configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def connect_drone(
    drone_name: str, system_address: str, drone_index: int
) -> System:
    # as seen at https://discuss.px4.io/t/mavsdk-multiple-drones-problem/44693/2
    # so I believe port 50051 is just a random starting port so that each System instance
    # uses a different port to avoid conflicts
    drone = System(port=50051 + drone_index)
    try:
        await asyncio.wait_for(drone.connect(system_address=system_address), timeout=3)
        logger.debug(f"Awaiting connection to {drone_name} at {system_address}")
    except asyncio.TimeoutError:
        logger.error(f"Error connecting to {drone_name} at {system_address}!")
        logger.error("X500 drone connection failed, aborting swarm demo.")
        exit(1)
    logger.debug(f"Connection await complete to {drone_name}.")

    async for state in drone.core.connection_state():
        logger.debug(f"Connection state for {drone_name}:")
        logger.debug(f"{state=}")
        if state.is_connected:
            logger.debug(f"Drone {drone_name} discovered!")
            break
    logger.debug(f"Connection state for drone {drone_name} complete.")

    logger.debug(
        f"Waiting for drone {drone_name} to have a global position estimate..."
    )
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            logger.debug(f"-- Global position estimate OK for drone {drone_name}")
            break

    logger.info(f"{drone_name} initialized, starting mission...")

    return drone


async def get_one_position(drone: System) -> Position:
    async for pos in drone.telemetry.position():
        return pos


async def get_one_heading(drone: System) -> float:
    async for heading in drone.telemetry.heading():
        return heading.heading_deg


# Move the drone to a specific location and wait until it arrives within specified tolerances
#
# Any parameters left as None will use the drone's current value for that parameter.
# E.g., to only change altitude, set latitude_deg, longitude_deg, and yaw_deg to None.
#
# Note: This function is needed because sending the action via mavsdk does not block until arrival
# so we need to implement our own wait logic
#
async def goto(
    drone: System,
    latitude_deg=None,
    longitude_deg=None,
    altitude_m=None,
    yaw_deg=None,
    latitude_epsilon: float = 0.000002,
    longitude_epsilon: float = 0.000002,
    altitude_epsilon: float = 0.5,
    yaw_epsilon: float = 5.0,
    check_freqency_sec: float = 1.0,
) -> None:
    # Fill out any None parameters with current drone values
    position = await get_one_position(drone)
    latitude_deg = latitude_deg if latitude_deg is not None else position.latitude_deg
    longitude_deg = (
        longitude_deg if longitude_deg is not None else position.longitude_deg
    )
    altitude_m = altitude_m if altitude_m is not None else position.absolute_altitude_m
    heading_deg = await get_one_heading(drone)
    yaw_deg = yaw_deg if yaw_deg is not None else heading_deg

    logger.debug(
        f"Going to lat={latitude_deg}, lon={longitude_deg}, alt={altitude_m}, yaw={yaw_deg}"
    )
    await drone.action.goto_location(
        latitude_deg=latitude_deg,
        longitude_deg=longitude_deg,
        absolute_altitude_m=altitude_m,
        yaw_deg=yaw_deg,
    )

    # Note: We need to get new telemetry streams inside the loop to avoid stale data
    while True:
        position = await get_one_position(drone)
        lat_diff = abs(position.latitude_deg - latitude_deg)
        lon_diff = abs(position.longitude_deg - longitude_deg)
        alt_diff = abs(position.absolute_altitude_m - altitude_m)
        heading_deg = await get_one_heading(drone)
        yaw_diff = abs(heading_deg - yaw_deg)
        logger.debug(
            f"Current position: lat={position.latitude_deg}, lon={position.longitude_deg}, alt={position.absolute_altitude_m}"
        )
        logger.debug(
            f"Differences: lat_diff={lat_diff}, lon_diff={lon_diff}, alt_diff={alt_diff}, yaw_diff={yaw_diff}"
        )
        if (
            lat_diff <= latitude_epsilon
            and lon_diff <= longitude_epsilon
            and alt_diff <= altitude_epsilon
            and yaw_diff <= yaw_epsilon
        ):
            logger.debug("Reached target location.")
            break
        await asyncio.sleep(check_freqency_sec)


async def vtol_mission(drone_vtol: System) -> None:
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


async def x3_mission(drone_x3: System) -> None:
    await asyncio.sleep(120)

    logger.info("-- Arming")
    await drone_x3.action.arm()

    logger.info("--- Taking Off")
    await drone_x3.action.set_takeoff_altitude(25.0)
    await drone_x3.action.takeoff()
    await asyncio.sleep(10)

    logger.info("fly to firestation")
    await drone_x3.action.goto_location(
        latitude_deg=32.061566,
        longitude_deg=118.779284,
        absolute_altitude_m=30.0,
        yaw_deg=120.0,
    )
    await asyncio.sleep(30)

    logger.info("look in firestation")
    await drone_x3.action.goto_location(
        latitude_deg=32.061566,
        longitude_deg=118.779284,
        absolute_altitude_m=2.8,
        yaw_deg=200.0,
    )

    await asyncio.sleep(30)

    logger.info("fly in firestation")
    await drone_x3.action.goto_location(
        latitude_deg=32.061467,
        longitude_deg=118.779241,
        absolute_altitude_m=3.0,
        yaw_deg=200.0,
    )

    logger.info("look around firestation")
    await drone_x3.action.goto_location(
        latitude_deg=32.061467,
        longitude_deg=118.779241,
        absolute_altitude_m=3.0,
        yaw_deg=300.0,
    )

    await asyncio.sleep(10)

    await drone_x3.action.goto_location(
        latitude_deg=32.061467,
        longitude_deg=118.779241,
        absolute_altitude_m=3.0,
        yaw_deg=60.0,
    )

    await asyncio.sleep(10)

    await drone_x3.action.goto_location(
        latitude_deg=32.061464,
        longitude_deg=118.779241,
        absolute_altitude_m=2.8,
        yaw_deg=170.0,
    )

    await asyncio.sleep(10)

    logger.info("fly out firestation")
    await drone_x3.action.goto_location(
        latitude_deg=32.061398,
        longitude_deg=118.779249,
        absolute_altitude_m=2.6,
        yaw_deg=170.0,
    )

    await asyncio.sleep(15)

    await drone_x3.action.return_to_launch()

    logger.info("--- Landing")


async def x500_mission(drone_x500: System) -> None:
    await asyncio.sleep(60)

    logger.info("-- Arming")
    await drone_x500.action.arm()

    logger.info("--- Taking Off")
    await drone_x500.action.set_takeoff_altitude(25.0)
    await drone_x500.action.takeoff()
    await asyncio.sleep(10)

    logger.info("fly to firestation")
    await drone_x500.action.goto_location(
        latitude_deg=32.061566,
        longitude_deg=118.779284,
        absolute_altitude_m=30.0,
        yaw_deg=120.0,
    )
    await asyncio.sleep(30)

    logger.info("x500 look in firestation")
    await drone_x500.action.goto_location(
        latitude_deg=32.061453,
        longitude_deg=118.779477,
        absolute_altitude_m=3.2,
        yaw_deg=270.0,
    )


async def xlab550_mission(drone_xlab550: System) -> None:
    logger.info("xlab550: Arming")
    await drone_xlab550.action.arm()

    logger.info("xlab550: Taking Off")
    await drone_xlab550.action.set_takeoff_altitude(3.0)
    await drone_xlab550.action.takeoff()
    await asyncio.sleep(10)

    logger.info("xlab550: Climbing to 30m")
    await goto(drone_xlab550, altitude_m=30.0)

    logger.info("xlab550: Turn to look towards firestation")
    await goto(drone_xlab550, yaw_deg=300.0)

    logger.info("xlab550: fly to firestation")
    await goto(
        drone_xlab550,
        latitude_deg=32.061265,
        longitude_deg=118.779401,
    )

    logger.info("xlab550: look at firestation")
    await goto(drone_xlab550, altitude_m=9.0, yaw_deg=320.0)


async def run_swarm_demo() -> None:
    # Connect to all drones
    drone_x500_task = asyncio.create_task(
        connect_drone("x500", "udp://0.0.0.0:14540", 0)
    )
    drone_vtol_task = asyncio.create_task(
        connect_drone("vtol", "udp://0.0.0.0:14541", 1)
    )
    drone_xlab550_task = asyncio.create_task(
        connect_drone("xlab550", "udp://0.0.0.0:14542", 2)
    )
    drone_x3_task = asyncio.create_task(connect_drone("x3", "udp://0.0.0.0:14543", 3))

    drone_x500, drone_vtol, drone_xlab550, drone_x3 = await asyncio.gather(
        drone_x500_task, drone_vtol_task, drone_xlab550_task, drone_x3_task
    )

    await xlab550_mission(drone_xlab550)

    # Run missions concurrently
    # drone_vtol_mission_task = asyncio.create_task(vtol_mission(drone_vtol))
    # drone_x500_mission_task = asyncio.create_task(x500_mission(drone_x500))
    # drone_x3_mission_task = asyncio.create_task(x3_mission(drone_x3))
    # drone_xlab550_mission_task = asyncio.create_task(xlab550_mission(drone_xlab550))

    # await asyncio.gather(
    #     drone_vtol_mission_task,
    #     drone_x500_mission_task,
    #     drone_x3_mission_task,
    #     drone_xlab550_mission_task
    # )


if __name__ == "__main__":
    asyncio.run(run_swarm_demo())
