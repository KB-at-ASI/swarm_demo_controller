#!/usr/bin/env python3

import asyncio
from mavsdk import System
from mavsdk.action import OrbitYawBehavior


async def run():
    drone_vtol = System()
    await drone_vtol.connect(system_address="udpin://0.0.0.0:14541")

    print("Waiting for drone to connect...")
    async for state in drone_vtol.core.connection_state():
        if state.is_connected:
            print("Drone discovered!")
            break

    print("Waiting for drone to have a global position estimate...")
    async for health in drone_vtol.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position estimate OK")
            break

    position = await drone_vtol.telemetry.position().__aiter__().__anext__()
    orbit_height = position.absolute_altitude_m + 15
    yaw_behavior = OrbitYawBehavior.HOLD_FRONT_TANGENT_TO_CIRCLE

    print("-- Arming")
    await drone_vtol.action.arm()

    print("--- Taking Off")
    await drone_vtol.action.set_takeoff_altitude(30.0)
    await drone_vtol.action.takeoff()
    await asyncio.sleep(10)

    print(f"Do orbit at {orbit_height}m height from the ground")
    await drone_vtol.action.do_orbit(
        radius_m=10,
        velocity_ms=2,
        yaw_behavior=yaw_behavior,
        latitude_deg=32.061467,
        longitude_deg=118.779284,
        absolute_altitude_m=30.0,
    )
    await asyncio.sleep(60)


async def run_x500():
    drone_x500 = System()
    await drone_x500.connect(system_address="udpin://0.0.0.0:14540")

    print("Waiting for drone to connect...")
    async for state in drone_x500.core.connection_state():
        if state.is_connected:
            print("Drone discovered!")
            break

    print("Waiting for drone to have a global position estimate...")
    async for health in drone_x500.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position estimate OK")
            break

    print("-- Arming")
    await drone_x500.action.arm()

    print("--- Taking Off")
    await drone_x500.action.set_takeoff_altitude(25.0)
    await drone_x500.action.takeoff()
    await asyncio.sleep(10)

    print(f"fly to firestation")
    await drone_x500.action.goto_location(
        latitude_deg=32.061566,
        longitude_deg=118.779284,
        absolute_altitude_m=30.0,
        yaw_deg=120.0
    )    
    await asyncio.sleep(30)

    print(f"look in firestation")
    await drone_x500.action.goto_location(
        latitude_deg=32.061566,
        longitude_deg=118.779284,
        absolute_altitude_m=2.8,
        yaw_deg=200.0
    )

    await asyncio.sleep(30)

    print(f"fly in firestation")
    await drone_x500.action.goto_location(
        latitude_deg=32.061467,
        longitude_deg=118.779241,
        absolute_altitude_m=3.0,
        yaw_deg=200.0
    )

    print(f"look around firestation")
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

    print(f"fly out firestation")
    await drone_x500.action.goto_location(
        latitude_deg=32.061398,
        longitude_deg=118.779249,
        absolute_altitude_m=2.6,
        yaw_deg=170.0
    )

    await asyncio.sleep(30)

    await drone_x500.action.return_to_launch()

    print("--- Landing")


if __name__ == "__main__":
    asyncio.run(run())