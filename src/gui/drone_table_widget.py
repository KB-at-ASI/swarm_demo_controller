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
)

from .map_widget import Drone


class DroneListWidget(QWidget):
    """widget that contains the drone table, status, and deploy button.

    The table is configured to always fill the widget's width.
    """

    def __init__(self, parent=None):
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

        self.deploy_btn = QPushButton("Deploy Swarm")
        self.status = QLabel("")

        layout = QVBoxLayout(self)
        layout.addWidget(self.table)
        layout.addWidget(self.deploy_btn)
        layout.addWidget(self.status, alignment=Qt.AlignRight)
        layout.setContentsMargins(4, 4, 4, 4)

    def populate(self, drones: List[Drone]) -> None:
        self.table.setRowCount(len(drones))
        for i, d in enumerate(drones):
            self.table.setItem(i, 0, QTableWidgetItem(d.name))
            self.table.setItem(i, 1, QTableWidgetItem(d.role))
            self.table.setItem(i, 2, QTableWidgetItem(d.mode))

    def selected_names(self) -> List[str]:
        return [
            self.table.item(r, 0).text()
            for r in range(self.table.rowCount())
            if self.table.item(r, 0) and self.table.item(r, 0).isSelected()
        ]
