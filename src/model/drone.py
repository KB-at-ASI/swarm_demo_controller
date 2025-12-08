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
        self.status_listeners = []
        self.state_listeners = []

    def add_status_listener(self, listener) -> None:
        self.status_listeners.append(listener)

    def add_state_listener(self, listener) -> None:
        self.state_listeners.append(listener)

    def set_status(self, new_status: DroneStatus) -> None:
        self.status = new_status
        for listener in self.status_listeners:
            listener.drone_status_changed(self, new_status)

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
        for listener in self.state_listeners:
            listener.drone_state_changed(self)

    async def initialize_state(self) -> None:
        pos = await self.get_one_position()
        heading = await self.get_one_heading()
        self.set_state(
            lat=pos.latitude_deg if pos else None,
            lon=pos.longitude_deg if pos else None,
            alt=pos.absolute_altitude_m if pos else None,
            heading=heading,
        )

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
