import asyncio
from typing import List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLabel,
    QHeaderView,
    QSizePolicy,
    QHBoxLayout,
)


from controller.swarm_controller import SwarmController

from model.drone import Drone


class DroneListWidget(QWidget):
    """widget that contains the drone table, status, and deploy button.

    The table is configured to always fill the widget's width.
    """

    def __init__(self, controller: SwarmController | None = None, parent=None):
        super().__init__(parent)

        self.table = QTableWidget(0, 3)
        # remove row numbers
        self.table.verticalHeader().setVisible(False)
        self.table.setHorizontalHeaderLabels(["Vehicle ID", "Role", "Status"])
        header = self.table.horizontalHeader()
        # Make columns stretch to fill available width
        header.setSectionResizeMode(QHeaderView.Stretch)

        # Ensure the table expands with the widget
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Select by row
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        # set font color when selected to black
        # set selection color to light gray
        self.table.setStyleSheet(
            "QTableWidget::item:selected { color: black; background-color: lightgray; }"
        )

        # Make a bar of buttons
        button_bar = QWidget()
        button_layout = QHBoxLayout(button_bar)

        self.connect_btn = QPushButton("Connect All Drones")
        self.connect_btn.clicked.connect(self.on_connect_clicked)
        button_layout.addWidget(self.connect_btn)

        self.deploy_btn = QPushButton("Execute Mission")
        self.deploy_btn.clicked.connect(
            lambda: asyncio.ensure_future(self.on_deploy_clicked())
        )

        button_layout.addWidget(self.deploy_btn)

        self.status = QLabel("")

        layout = QVBoxLayout(self)
        layout.addWidget(self.table)
        layout.addWidget(button_bar)
        layout.addWidget(self.status, alignment=Qt.AlignRight)
        layout.setContentsMargins(4, 4, 4, 4)

        self.controller = controller
        for drone in controller.get_all_drones():
            drone.add_status_change_callback(self.drone_status_changed)
            self.table.insertRow(self.table.rowCount())
            row = self.table.rowCount() - 1
            self.table.setItem(row, 0, QTableWidgetItem(drone.drone_id))
            self.table.setItem(
                row, 1, QTableWidgetItem(drone.role if drone.role else "")
            )
            self.table.setItem(row, 2, QTableWidgetItem(drone.status.name))

    def drone_status_changed(self, drone: Drone, new_status) -> None:
        # find the row for this drone and update status
        for r in range(self.table.rowCount()):
            if self.table.item(r, 0).text() == drone.drone_id:
                self.table.setItem(r, 2, QTableWidgetItem(new_status.name))
                break
            else:
                pass

    def get_selected_drone_ids(self) -> List[str]:
        return [
            self.table.item(r, 0).text()
            for r in range(self.table.rowCount())
            if self.table.item(r, 0) and self.table.item(r, 0).isSelected()
        ]

    def on_connect_clicked(self) -> None:
        # selected = self.get_selected_drone_ids()
        # self.status.setText(f"Connect clicked for: {', '.join(selected)}")
        self.controller.connect_all_drones()

    async def on_deploy_clicked(self) -> None:
        self.status.setText("Deploy clicked")
        await self.controller.deploy_swarm()
