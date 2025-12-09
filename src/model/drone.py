import asyncio
from enum import Enum, auto

from mavsdk.telemetry import Position

from mavsdk import System as MAVSDKSystem


class DroneStatus(Enum):
    DISCONNECTED = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    ARMED = auto()
    AIRBORNE = auto()
    LANDING = auto()
    LANDED = auto()


class Drone(object):
    def __init__(self, drone_id: str, connection_url: str, role: str | None = None):
        # drone_id must be unique per drone
        self.drone_id: str = drone_id
        self.connection_url: str = connection_url
        self.role = role if role is not None else "UNASSIGNED"
        self.lat: float | None = None
        self.lon: float | None = None
        self.alt: float | None = None
        self.heading: float | None = None
        self.status: DroneStatus = DroneStatus.DISCONNECTED
        self.mavsdk_system: MAVSDKSystem = None  # to be set when connected
        self.status_change_callbacks = []
        self.state_change_callbacks = []
        self._state_update_task = None
        self._state_update_rate = 0.5  # seconds

    def add_status_change_callback(self, callback_fn) -> None:
        self.status_change_callbacks.append(callback_fn)

    def add_state_change_callback(self, callback_fn) -> None:
        self.state_change_callbacks.append(callback_fn)

    def set_status(self, new_status: DroneStatus) -> None:
        self.status = new_status
        for callback in self.status_change_callbacks:
            callback(self, new_status)

    def set_state(
        self,
        lat: float | None,
        lon: float | None,
        alt: float | None,
        heading: float | None,
    ) -> None:
        self.lat = lat if lat is not None else self.lat
        self.lon = lon if lon is not None else self.lon
        self.alt = alt if alt is not None else self.alt
        self.heading = heading if heading is not None else self.heading
        for callback in self.state_change_callbacks:
            callback(self)

    async def initialize_state(self) -> None:
        pos = await self.get_one_position()
        heading = await self.get_one_heading()
        self.set_state(
            lat=pos.latitude_deg if pos else None,
            lon=pos.longitude_deg if pos else None,
            alt=pos.absolute_altitude_m if pos else None,
            heading=heading,
        )

    def get_state_update_rate(self) -> float | None:
        if self._state_update_rate is None:
            return None
        return self._state_update_rate

    def set_state_update_rate(self, rate_seconds: float) -> None:
        self._state_update_rate = rate_seconds

    def start_periodic_state_update(self) -> None:
        if self._state_update_task is None:
            self._state_update_task = asyncio.create_task(self._periodic_state_update())

    def stop_periodic_state_update(self) -> None:
        if self._state_update_task is not None:
            self._state_update_task.cancel()
            self._state_update_task = None

    async def _periodic_state_update(self) -> None:
        while True:
            pos = await self.get_one_position()
            heading = await self.get_one_heading()
            self.set_state(
                lat=pos.latitude_deg if pos else None,
                lon=pos.longitude_deg if pos else None,
                alt=pos.absolute_altitude_m if pos else None,
                heading=heading,
            )

            if self.drone_id == "lipan":
                fwmetrics = await self.get_fixedwing_metrics()
                print(f"Fixed wing metrics: {fwmetrics}")

            await asyncio.sleep(self._state_update_rate)

    async def get_one_position(self) -> Position:
        if self.mavsdk_system is None:
            return None

        async for pos in self.mavsdk_system.telemetry.position():
            return pos

    async def get_one_heading(self) -> float:
        if self.mavsdk_system is None:
            return None

        async for heading in self.mavsdk_system.telemetry.heading():
            return heading.heading_deg

    async def get_fixedwing_metrics(self) -> dict:
        if self.mavsdk_system is None:
            return {}
        async for (
            fixed_wing_metrics
        ) in self.mavsdk_system.telemetry.fixedwing_metrics():
            return fixed_wing_metrics
