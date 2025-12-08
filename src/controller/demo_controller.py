#!/usr/bin/env python3

import asyncio
import logging

from enum import Enum, auto

# from mavsdk import System
from mavsdk.telemetry import Position
from mavsdk.action import OrbitYawBehavior

from model.drone import Drone

# configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DroneStatus(Enum):
    DISCONNECTED = auto()
    CONNECTED = auto()
    ARMED = auto()
    IN_AIR = auto()
    ABOVE_LAUNCH_SITE = auto()
    ABOVE_FIRESTATION = auto()
    LOOKING_AT_FIRESTATION = auto()
    IN_FIRESTATION = auto()
    LANDING = auto()
    LANDED = auto()


class DemoController(object):
    def __init__(self):
        self.status = {}
        self.status_conditions = {}

    def get_drone_status(self, drone: Drone) -> DroneStatus:
        return self.status.get(drone)

    async def set_drone_status(self, drone: Drone, status: DroneStatus) -> None:
        if drone not in self.status_conditions:
            self.status_conditions[drone] = asyncio.Condition()
        condition = self.status_conditions[drone]
        async with condition:
            self.status[drone] = status
            condition.notify_all()

    async def wait_for_drone_status(self, drone: Drone, target: DroneStatus) -> None:
        condition = self.status_conditions[drone]
        async with condition:
            await condition.wait_for(lambda: self.status[drone] == target)

    async def get_one_position(self, drone: Drone) -> Position:
        async for pos in drone.mavsdk_system.telemetry.position():
            return pos

    async def get_one_heading(self, drone: Drone) -> float:
        async for heading in drone.mavsdk_system.telemetry.heading():
            return heading.heading_deg

    # Move a drone to a specific location and wait until it arrives within specified tolerances
    #
    # Any parameters left as None will use the drone's current value for that parameter.
    # E.g., to only change altitude, set latitude_deg, longitude_deg, and yaw_deg to None.
    #
    # Note: This function is needed because sending the action via mavsdk does not block until arrival
    # so we need to implement our own wait logic
    #
    async def drone_goto(
        self,
        drone: Drone,
        latitude_deg=None,
        longitude_deg=None,
        altitude_m=None,
        yaw_deg=None,
        latitude_epsilon: float = 0.000002,
        longitude_epsilon: float = 0.000002,
        altitude_epsilon: float = 0.5,
        yaw_epsilon: float = 5.0,
        check_freqency_sec: float = 1.0,
        status_at_completion: DroneStatus = None,
    ) -> None:
        # Fill out any None parameters with current drone values
        position = await self.get_one_position(drone)
        latitude_deg = (
            latitude_deg if latitude_deg is not None else position.latitude_deg
        )
        longitude_deg = (
            longitude_deg if longitude_deg is not None else position.longitude_deg
        )
        altitude_m = (
            altitude_m if altitude_m is not None else position.absolute_altitude_m
        )
        heading_deg = await self.get_one_heading(drone)
        yaw_deg = yaw_deg if yaw_deg is not None else heading_deg

        logger.debug(
            f"Going to lat={latitude_deg}, lon={longitude_deg}, alt={altitude_m}, yaw={yaw_deg}"
        )
        await drone.mavsdk_system.action.goto_location(
            latitude_deg=latitude_deg,
            longitude_deg=longitude_deg,
            absolute_altitude_m=altitude_m,
            yaw_deg=yaw_deg,
        )

        # Note: We need to get new telemetry streams inside the loop to avoid stale data
        while True:
            position = await self.get_one_position(drone)
            lat_diff = abs(position.latitude_deg - latitude_deg)
            lon_diff = abs(position.longitude_deg - longitude_deg)
            alt_diff = abs(position.absolute_altitude_m - altitude_m)
            heading_deg = await self.get_one_heading(drone)
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
                logger.debug("Reached target location and orientation.")
                if status_at_completion is not None:
                    await self.set_drone_status(drone, status_at_completion)
                break
            await asyncio.sleep(check_freqency_sec)

    async def comms_drone_mission(self, drone: Drone) -> None:
        logger.info("comms_drone: Arming")
        await drone.mavsdk_system.action.arm()
        await self.set_drone_status(drone, DroneStatus.ARMED)

        logger.info("comms_drone: Taking Off")
        await drone.mavsdk_system.action.takeoff()
        await self.set_drone_status(drone, DroneStatus.IN_AIR)
        # The VTOL can go to specific locations, the fixed wing drone cannot

        # await drone_goto(
        #     sim,
        #     sim.comms_drone,
        #     altitude_m=30.0,
        #     yaw_deg=240.0,
        #     status_at_completion=DroneStatus.ABOVE_LAUNCH_SITE,
        # )

        # logger.info("comms_drone: Flying to firestation")
        # await drone_goto(
        #     sim,
        #     sim.comms_drone,
        #     latitude_deg=32.061531,
        #     longitude_deg=118.779481,
        #     status_at_completion=DroneStatus.ABOVE_FIRESTATION,
        # )

        logger.info("comms_drone: Entering orbit over firestation")
        await drone.mavsdk_system.action.do_orbit(
            radius_m=18,
            velocity_ms=2,
            yaw_behavior=OrbitYawBehavior.HOLD_FRONT_TANGENT_TO_CIRCLE,
            latitude_deg=32.061467,
            longitude_deg=118.779284,
            absolute_altitude_m=30.0,
        )

    async def x3_mission(self, drone: Drone) -> None:
        # Wait for VTOL to be in position above firestation
        # await wait_for_drone_status(sim, sim.xlab550, DroneStatus.LOOKING_AT_FIRESTATION)
        # Update: We want to show drones acting concurrently, so don't wait for VTOL

        # wait for a short time
        await asyncio.sleep(15)

        logger.info("x3: Arming")
        await drone.mavsdk_system.action.arm()
        await self.set_drone_status(drone, DroneStatus.ARMED)

        logger.info("x3: Taking Off")
        await drone.mavsdk_system.action.takeoff()
        await self.set_drone_status(drone, DroneStatus.IN_AIR)

        await self.drone_goto(
            drone,
            altitude_m=25.0,
            status_at_completion=DroneStatus.ABOVE_LAUNCH_SITE,
        )

        logger.info("x3 fly to firestation")
        await self.drone_goto(
            drone,
            latitude_deg=32.061566,
            longitude_deg=118.779284,
            altitude_m=30.0,
            yaw_deg=120.0,
            status_at_completion=DroneStatus.ABOVE_FIRESTATION,
        )

        logger.info("x3 look in firestation")
        await self.drone_goto(
            drone,
            latitude_deg=32.061566,
            longitude_deg=118.779284,
            altitude_m=3.0,
            yaw_deg=200.0,
            status_at_completion=DroneStatus.LOOKING_AT_FIRESTATION,
        )

        logger.info("x3 fly in firestation")
        await self.drone_goto(
            drone,
            latitude_deg=32.061467,
            longitude_deg=118.779241,
            altitude_m=3.0,
            yaw_deg=200.0,
            status_at_completion=DroneStatus.IN_FIRESTATION,
        )

        logger.info("x3 look around firestation")
        await self.drone_goto(
            drone,
            yaw_deg=300.0,
        )

        await asyncio.sleep(10)

        logger.info("x3 look around firestation")
        await self.drone_goto(
            drone,
            yaw_deg=60.0,
        )

        await asyncio.sleep(10)
        logger.info("x3 look around firestation")
        await self.drone_goto(
            drone,
            altitude_m=3.0,
            yaw_deg=170.0,
        )

        await asyncio.sleep(10)

        logger.info("x3 fly out firestation")
        await self.drone_goto(
            drone,
            latitude_deg=32.061398,
            longitude_deg=118.779249,
            altitude_m=2.6,
            yaw_deg=170.0,
            status_at_completion=DroneStatus.LOOKING_AT_FIRESTATION,
        )

        await asyncio.sleep(15)

        await drone.mavsdk_system.action.return_to_launch()

        logger.info("x3 returning to land")

    async def x500_mission(self, drone: Drone) -> None:
        # Wait for VTOL to be in position above firestation
        # await wait_for_drone_status(sim, sim.vtol, DroneStatus.ABOVE_FIRESTATION)
        # Update: We want to show drones acting concurrently, so don't wait for VTOL

        # wait for a short time
        # await asyncio.sleep(10)

        logger.info("x500 Arming")
        await drone.mavsdk_system.action.arm()
        await self.set_drone_status(drone, DroneStatus.ARMED)

        logger.info("x500 Taking Off")
        await drone.mavsdk_system.action.takeoff()
        await self.set_drone_status(drone, DroneStatus.IN_AIR)
        await self.drone_goto(
            drone,
            altitude_m=25.0,
            status_at_completion=DroneStatus.ABOVE_LAUNCH_SITE,
        )

        logger.info("x500 fly to firestation")
        await self.drone_goto(
            drone,
            latitude_deg=32.061566,
            longitude_deg=118.779284,
            altitude_m=30.0,
            yaw_deg=120.0,
            status_at_completion=DroneStatus.ABOVE_FIRESTATION,
        )

        logger.info("x500 look in firestation")
        await self.drone_goto(
            drone,
            latitude_deg=32.061453,
            longitude_deg=118.779477,
            altitude_m=3.2,
            yaw_deg=270.0,
            status_at_completion=DroneStatus.LOOKING_AT_FIRESTATION,
        )

    async def xlab550_mission(self, drone: Drone) -> None:
        # Wait for VTOL to be in position above firestation
        # await wait_for_drone_status(sim, sim.vtol, DroneStatus.ABOVE_FIRESTATION)
        # Update: We want to show drones acting concurrently, so don't wait for VTOL

        # wait for a short time
        await asyncio.sleep(10)

        logger.info("xlab550: Arming")
        await drone.mavsdk_system.action.arm()
        await self.set_drone_status(drone, DroneStatus.ARMED)

        logger.info("xlab550: Taking Off")
        await drone.mavsdk_system.action.takeoff()
        await self.set_drone_status(drone, DroneStatus.IN_AIR)
        logger.info("xlab550: Climbing to 30m")
        await self.drone_goto(
            drone,
            altitude_m=30.0,
            status_at_completion=DroneStatus.ABOVE_LAUNCH_SITE,
        )

        logger.info("xlab550: Turn to look towards firestation")
        await self.drone_goto(drone, yaw_deg=300.0)

        logger.info("xlab550: fly to firestation")
        await self.drone_goto(
            drone,
            latitude_deg=32.061265,
            longitude_deg=118.779401,
            status_at_completion=DroneStatus.ABOVE_FIRESTATION,
        )

        logger.info("xlab550: look at firestation")
        await self.drone_goto(
            drone,
            altitude_m=9.0,
            yaw_deg=320.0,
            status_at_completion=DroneStatus.LOOKING_AT_FIRESTATION,
        )
