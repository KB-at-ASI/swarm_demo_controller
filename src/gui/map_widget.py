import json
import os
from typing import List, Tuple
from controller.swarm_controller import SwarmController
from model.drone import Drone
import util.geo_tools as geo_tools

from PySide6.QtCore import Qt, Signal, QPointF
from PySide6.QtGui import QPixmap, QPen, QBrush, QColor, QPainter
from PySide6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QGraphicsEllipseItem,
    QGraphicsLineItem,
    QGraphicsTextItem,
    QLabel,
)


class LatLonLabel(QLabel):
    """A QLabel that displays lat/lon coordinates."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            "background: rgba(0,0,0,0.6); color: white; padding: 4px; border-radius: 4px;"
        )
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.hide()

    def set_lat_lon(self, lat, lon) -> None:
        if lat is None or lon is None:
            return
        self.setText(f"{lat:.6f}, {lon:.6f}")
        self.adjustSize()


class MapWidget(QGraphicsView):
    """A simple map widget that displays a background image, drone markers,

    The lat/lon mapping is an affine transformation, handled separately from the QGraphicsView.
    The QGraphicsView transformation is only for zooming/panning the view. The scene coordinates
    correspond directly to image pixel coordinates of the map image.
    """

    mouseMoved = Signal(float, float)
    locationSelected = Signal(float, float)

    def __init__(
        self,
        controller: SwarmController | None = None,
        parent=None,
    ):
        super().__init__(parent)
        # Use QPainter render hint for antialiasing (correct PySide6 API)
        self.setRenderHint(QPainter.Antialiasing)
        # Zoom state
        self._zoom = 1.0
        self._zoom_step = 1.15
        self._zoom_min = 0.2
        self._zoom_max = 5.0
        # Anchor zoom to the mouse cursor
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setMouseTracking(True)

        # always show scrollbars
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        # Floating lat/lon inset (lower-right). Use a QLabel overlay so it
        # doesn't scale with the scene or block mouse events.
        self.coord_label = LatLonLabel(self)

        # Map scene
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.pixmap_item: QGraphicsPixmapItem | None = None
        self.drones_items = {}  # name -> (ellipse, label)
        self.lines = []
        self.mission_circle = None
        self.mission_point = None

        # Default bounds (min_lat, max_lat, min_lon, max_lon)
        # These can be tuned to match the map image used.
        self.bounds = (32.0605, 32.0625, 118.7780, 118.7805)

        if controller.scenario_spec:
            self.load_scenario(controller.scenario_spec)
        else:
            # blank pixmap placeholder
            pix = QPixmap(800, 600)
            pix.fill(QColor("#f7f7f7"))
            self.set_pixmap(pix)
            self.img_to_latlon_mapping = geo_tools.default_affine_transform()

        for drone in controller.get_all_drones():
            drone.add_state_change_callback(self.drone_state_changed)

        if controller.scenario_spec.get("center_view_coordinates"):
            center_coords = controller.scenario_spec["center_view_coordinates"]
            center_lat = center_coords["lat"]
            center_lon = center_coords["lon"]
            centerPoint = self.latlon_to_point(center_lat, center_lon)
            self.centerOn(centerPoint)

    def load_scenario(self, scenario_spec: json) -> None:
        if scenario_spec.get("map_image"):
            image_path = scenario_spec["map_image"]
            if not os.path.isfile(image_path):
                raise ValueError("Image file does not exist")
            pixmap = QPixmap(image_path)
            self.set_pixmap(pixmap)

        if scenario_spec.get("pixel to lat/lon mapping"):
            # TODO: implement pixel to lat/lon mapping
            pt_pairs = scenario_spec["pixel to lat/lon mapping"]["point_pairs"]
            self.img_to_latlon_mapping = geo_tools.compute_affine_transform(pt_pairs)

    def set_pixmap(self, pix: QPixmap) -> None:
        self.scene.clear()
        self.pixmap_item = QGraphicsPixmapItem(pix)
        self.scene.addItem(self.pixmap_item)
        self.setSceneRect(self.pixmap_item.boundingRect())

    def set_bounds(
        self, min_lat: float, max_lat: float, min_lon: float, max_lon: float
    ) -> None:
        self.bounds = (min_lat, max_lat, min_lon, max_lon)

    def latlon_to_point(self, lat: float, lon: float) -> QPointF:
        x, y = geo_tools.latlon_to_img_x_y(self.img_to_latlon_mapping, lat, lon)
        return QPointF(x, y)

    def point_to_latlon(self, pt: QPointF) -> Tuple[float, float]:
        lat, lon = geo_tools.img_x_y_to_latlon(
            self.img_to_latlon_mapping, pt.x(), pt.y()
        )

        return lat, lon

    def drone_state_changed(self, drone: Drone) -> None:
        self.update_drone_marker(drone)

    def update_drone_marker(self, drone: Drone) -> None:
        # Remove previous drone items
        if drone.drone_id in self.drones_items:
            old_ellipse, old_label = self.drones_items[drone.drone_id]
            self.scene.removeItem(old_ellipse)
            self.scene.removeItem(old_label)

        pt = self.latlon_to_point(drone.lat, drone.lon)
        ellipse = QGraphicsEllipseItem(pt.x() - 6, pt.y() - 6, 12, 12)
        ellipse.setBrush(QBrush(QColor("#2b8cbe")))
        ellipse.setPen(QPen(Qt.black))
        label = QGraphicsTextItem()
        label.setHtml(
            f'<div style="color: black; font-size: 12px; background-color: white;">{drone.drone_id}</div>'
        )
        label.setPos(pt.x() + 8, pt.y() - 8)
        self.scene.addItem(ellipse)
        self.scene.addItem(label)
        self.drones_items[drone.drone_id] = (ellipse, label)

    def highlight_drones(self, names: List[str]) -> None:
        for name, (ellipse, label) in self.drones_items.items():
            if name in names:
                ellipse.setBrush(QBrush(QColor("#f03b20")))
            else:
                ellipse.setBrush(QBrush(QColor("#2b8cbe")))

    def clear_mission(self) -> None:
        if self.mission_circle:
            self.scene.removeItem(self.mission_circle)
            self.mission_circle = None
        for ln in self.lines:
            self.scene.removeItem(ln)
        self.lines.clear()

    def mouseMoveEvent(self, event):
        if not self.pixmap_item:
            return
        scene_pt = self.mapToScene(event.pos())
        lat, lon = self.point_to_latlon(scene_pt)
        # update inset label
        self.coord_label.set_lat_lon(lat, lon)
        self._reposition_latlon_label()
        self.coord_label.show()

        self.mouseMoved.emit(lat, lon)
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.pixmap_item:
            scene_pt = self.mapToScene(event.pos())
            lat, lon = self.point_to_latlon(scene_pt)
            self.clear_mission()
            # draw mission point
            self.mission_point = QGraphicsEllipseItem(
                scene_pt.x() - 4, scene_pt.y() - 4, 8, 8
            )
            self.mission_point.setBrush(QBrush(QColor("#4daf4a")))
            self.scene.addItem(self.mission_point)
            # draw mission circle (approx pixel radius)
            radius_px = 50
            self.mission_circle = QGraphicsEllipseItem(
                scene_pt.x() - radius_px,
                scene_pt.y() - radius_px,
                radius_px * 2,
                radius_px * 2,
            )
            pen = QPen(QColor("#4daf4a"))
            pen.setStyle(Qt.DashLine)
            self.mission_circle.setPen(pen)
            self.scene.addItem(self.mission_circle)
            self.locationSelected.emit(lat, lon)
        super().mousePressEvent(event)

    def leaveEvent(self, event):
        # Hide the inset when the cursor leaves the view
        try:
            self.coord_label.hide()
        except Exception:
            pass
        super().leaveEvent(event)

    def resizeEvent(self, event):
        # Keep the inset positioned in the lower-right when the view resizes
        super().resizeEvent(event)
        self._reposition_latlon_label()

    def _reposition_latlon_label(self):
        if self.coord_label and not self.coord_label.isHidden():
            margin = 8
            vw = self.viewport().width()
            vh = self.viewport().height()
            lw = self.coord_label.width()
            lh = self.coord_label.height()
            self.coord_label.move(vw - lw - margin, vh - lh - margin)

    def wheelEvent(self, event):
        """Zoom in/out with mouse wheel. Anchor is under mouse so zoom centers at cursor."""
        delta = event.angleDelta().y()
        if delta == 0:
            return

        if delta > 0:
            factor = self._zoom_step
        else:
            factor = 1 / self._zoom_step

        new_zoom = self._zoom * factor
        if new_zoom < self._zoom_min or new_zoom > self._zoom_max:
            return

        self._zoom = new_zoom
        self.scale(factor, factor)
        event.accept()

    def draw_lines_to_selected(self, selected_names: List[str]) -> None:
        self.clear_mission()
        # if mission point exists, leave it and draw lines
        if self.mission_point is None:
            return
        center = self.mission_point.rect().center()
        for name in selected_names:
            items = self.drones_items.get(name)
            if not items:
                continue
            ellipse, _ = items
            line = QGraphicsLineItem(
                ellipse.rect().center().x(),
                ellipse.rect().center().y(),
                center.x(),
                center.y(),
            )
            pen = QPen(QColor("#444444"))
            pen.setWidth(2)
            line.setPen(pen)
            self.scene.addItem(line)
            self.lines.append(line)
