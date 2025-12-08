import sys
from typing import List

from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QHBoxLayout,
    QSplitter,
)

import PySide6.QtAsyncio as QtAsyncio
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMessageBox

from controller.swarm_controller import SwarmController

from .map_widget import MapWidget, Drone
from .drone_table_widget import DroneListWidget


# def make_sample_drones() -> List[Drone]:
#     # Hard-coded sample drones (matches positions used in `swarm_demo.py` area)
#     return [
#         Drone("x500", "SURVEILLANCE", "DISARMED", 32.061566, 118.779284),
#         Drone("vtol", "COMMS", "DISARMED", 32.061531, 118.779481),
#         Drone("xlab550", "SURVEILLANCE", "DISARMED", 32.061265, 118.779401),
#         Drone("x3", "INSPECTION", "DISARMED", 32.061398, 118.779249),
#     ]


class MainWindow(QMainWindow):
    def __init__(
        self,
        controller: SwarmController | None = None,
    ):
        super().__init__()
        self.setWindowTitle("Swarm Controller")
        self.resize(1270, 1056)

        self.createMenuBar()

        self.central_widget = CentralWidget(controller)
        self.setCentralWidget(self.central_widget)

        # register resize event to handle map resizing
        self.resizeEvent = self.on_map_resize

    def on_map_resize(self, event):
        super().resizeEvent(event)
        print(f"MainWindow resized  to: {self.size()}")

    def createMenuBar(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        about_action = QAction("About", self)
        about_action.triggered.connect(
            lambda: QMessageBox.information(
                self,
                "About",
                "Swarm Demo Controller\nPrototype GUI\nAirSpace Innovation",
            )
        )
        quit_action = QAction("Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(QApplication.instance().quit)
        file_menu.addAction(about_action)
        file_menu.addSeparator()
        file_menu.addAction(quit_action)


class CentralWidget(QWidget):
    def __init__(self, controller: SwarmController | None = None):
        super().__init__()

        # Use a vertical splitter so user can resize top (map) and bottom (drone list)
        splitter = QSplitter(Qt.Vertical)

        # Top: map
        self.map_widget = MapWidget(controller)

        # Bottom: DroneListWidget encapsulates table, status, and deploy button
        drone_list_widget = DroneListWidget(controller)

        splitter.addWidget(self.map_widget)
        splitter.addWidget(drone_list_widget)

        # Prefer map larger than the drone list initially
        # reasonable defaults for demo
        splitter.setSizes([806, 208])

        layout = QHBoxLayout(self)
        layout.addWidget(splitter)

        # populate drones
        # self.drones = make_sample_drones()
        # drone_list_widget.populate(self.drones)

        # TODO: populate map with drones
        # self.map_widget.set_drones(self.drones)

        # connect events
        # map widget shows lat/lon inset itself; keep the signal connected only
        # for optional future uses but do not update the drone_list status here.
        self.map_widget.mouseMoved.connect(self.on_mouse_moved)
        self.map_widget.locationSelected.connect(self.on_location_selected)
        # connect selection and deploy signals from the DroneListWidget
        drone_list_widget.table.itemSelectionChanged.connect(self.on_selection_changed)
        drone_list_widget.deploy_btn.clicked.connect(self.on_deploy)
        # expose for use in other methods
        self.drone_list = drone_list_widget

    def _populate_table(self, drones):
        # kept for compatibility (not used currently)
        self.drone_list.populate(drones)

    def on_mouse_moved(self, lat: float, lon: float) -> None:
        # This handler is kept as a no-op so
        # other components can still listen to the signal if needed.
        return

    def on_location_selected(self, lat: float, lon: float) -> None:
        self.drone_list.status.setText(f"Mission location set: {lat:.6f}, {lon:.6f}")
        # draw lines to current selection
        self.on_selection_changed()

    def on_selection_changed(self) -> None:
        selected = self.drone_list.get_selected_drone_ids()
        self.map_widget.highlight_drones(selected)
        self.map_widget.draw_lines_to_selected(selected)

    def on_deploy(self) -> None:
        selected = self.drone_list.get_selected_drone_ids()
        # get mission location (if any)
        if self.map_widget.mission_point:
            center = self.map_widget.mission_point.rect().center()
            mission_lat, mission_lon = self.map_widget.point_to_latlon(center)
        else:
            mission_lat = mission_lon = None

        print(
            "DEPLOY STUB: selected_drones=",
            selected,
            "mission_location=",
            (mission_lat, mission_lon),
        )


def run(controller: SwarmController | None = None) -> None:
    app = QApplication(sys.argv)
    w = MainWindow(controller)
    w.show()
    QtAsyncio.run(handle_sigint=True)


if __name__ == "__main__":
    img = None
    if len(sys.argv) > 1:
        img = sys.argv[1]
    run(img)
