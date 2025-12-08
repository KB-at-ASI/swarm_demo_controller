from enum import Enum, auto


class DroneStatus(Enum):
    DISCONNECTED = auto()
    CONNECTED = auto()
    ARMED = auto()
    AIRBORNE = auto()
    LANDING = auto()
    LANDED = auto()


class Drone(object):
    def __init__(self, drone_id: str, connection_url: str):
        self.drone_id = drone_id
        self.connection_url = connection_url
        self.role = None
        self.lat = None
        self.lon = None
        self.alt = None
        self.heading = None
        self.status: DroneStatus = DroneStatus.DISCONNECTED
        self.mavsdk_system = None  # to be set when connected
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
