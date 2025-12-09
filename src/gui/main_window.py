import sys

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

from .map_widget import MapWidget
from .drone_table_widget import DroneListWidget


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

        # register close event to handle application exit
        self.closeEvent = self.on_close

    def on_close(self, event):
        QApplication.instance().quit()

    def on_map_resize(self, event):
        super().resizeEvent(event)

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
        self.drone_list_widget = DroneListWidget(controller)

        splitter.addWidget(self.map_widget)
        splitter.addWidget(self.drone_list_widget)

        # Prefer map larger than the drone list initially
        # reasonable defaults for demo
        splitter.setSizes([806, 240])

        layout = QHBoxLayout(self)
        layout.addWidget(splitter)

        # connect events
        # map widget shows lat/lon inset itself; keep the signal connected only
        # for optional future uses but do not update the drone_list status here.
        self.map_widget.mouseMoved.connect(self.on_mouse_moved)
        self.map_widget.locationSelected.connect(self.on_location_selected)
        # connect selection and deploy signals from the DroneListWidget
        self.drone_list_widget.table.itemSelectionChanged.connect(
            self.on_selection_changed
        )

    def on_mouse_moved(self, lat: float, lon: float) -> None:
        # This handler is kept as a no-op so
        # other components can still listen to the signal if needed.
        return

    def on_location_selected(self, lat: float, lon: float) -> None:
        self.drone_list_widget.status.setText(
            f"Mission location set: {lat:.6f}, {lon:.6f}"
        )
        # draw lines to current selection
        self.on_selection_changed()

    def on_selection_changed(self) -> None:
        selected = self.drone_list_widget.get_selected_drone_ids()
        self.map_widget.highlight_drones(selected)


def run(controller: SwarmController | None = None) -> None:
    app = QApplication(sys.argv)
    w = MainWindow(controller)
    w.app = app
    w.show()
    QtAsyncio.run(handle_sigint=True)


if __name__ == "__main__":
    img = None
    if len(sys.argv) > 1:
        img = sys.argv[1]
    run(img)
