"""
    MIT License

    Copyright (c) 2020 Christoph Kreisl
    Copyright (c) 2021 Lukas Ruppert

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""

from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QGraphicsPixmapItem
from PySide2.QtWidgets import QGraphicsScene
from PySide2.QtWidgets import QGraphicsView
from PySide2.QtCore import QPoint
from PySide2.QtCore import Qt
import math
import logging

from .hdr_image import HDRImage

class HDRGraphicsViewBase(QGraphicsView):

    def __init__(self):
        QGraphicsView.__init__(self)
        # allow drag n drop events
        self.setAcceptDrops(True)
        # keep track of mouse moving within area
        self.setMouseTracking(True)
        # important for mouse tracking and later pixel selection
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self._hdri = HDRImage()
        self._scene = QGraphicsScene()
        self._scale_factor = 1.15
        # self._pixmap_item = QGraphicsPixmapItem()
        self._pixmap_item = None
        self.setScene(self._scene)

    @property
    def hdr_image(self) -> HDRImage:
        return self._hdri

    @property
    def pixmap(self) -> QPixmap:
        """
        Returns the rendered image as pixmap
        """
        return self._hdri.pixmap

    @property
    def pixmap_item(self):
        return self._pixmap_item

    def mousePressEvent(self, q_mouse_event):
        super().mousePressEvent(q_mouse_event)

    def mouseReleaseEvent(self, q_mouse_event):
        super().mouseReleaseEvent(q_mouse_event)

    def mouseMoveEvent(self, q_mouse_event):
        super().mouseMoveEvent(q_mouse_event)

    def dragMoveEvent(self, q_drag_move_event):
        """
        Nothing to-do here, has to be implemented for drag and drop
        :param q_drag_move_event:
        :return:
        """
        # nothing to-do here
        pass

    def dragEnterEvent(self, q_drag_enter_event):
        """
        Handles drag enter event for drag and drop of exr images
        :param q_drag_enter_event:
        :return:
        """
        if q_drag_enter_event.mimeData().hasFormat('text/plain'):
            q_drag_enter_event.acceptProposedAction()

    def dropEvent(self, q_drop_event):
        """
        Handles drop events, will load and display an exr image
        :param q_drop_event:
        :return:
        """
        if q_drop_event.mimeData().hasUrls():
            q_url = q_drop_event.mimeData().urls()[0]
            path = str(q_url.path())
            if path.endswith('.exr'):
                self.load_hdr_image(path)

    # def wheelEvent(self, q_wheel_event):
    #     """
    #     Handles the mouse wheel event for zooming in and out
    #     :param q_wheel_event:
    #     :return:
    #     """
    #     angle_delta = q_wheel_event.angleDelta()
    #     old_pos = self.mapToScene(q_wheel_event.pos())
    #     if angle_delta.y() > 0:
    #         self.scale(self._scale_factor,
    #                    self._scale_factor)
    #     else:
    #         self.scale(1 / self._scale_factor,
    #                    1 / self._scale_factor)
    #     new_pos = self.mapToScene(q_wheel_event.pos())
    #     delta = new_pos - old_pos
    #     self.translate(delta.x(), delta.y())
    #     q_wheel_event.accept()

    def set_falsecolor(self, falsecolor : bool):
        self._hdri.falsecolor = falsecolor
        self.display_image(self.pixmap)

    def set_plusminus(self, plusminus : bool):
        self._hdri.plusminus = plusminus
        self.display_image(self.pixmap)

    def set_show_ref(self, show_ref : bool):
        self._hdri.show_ref = show_ref
        self.display_image(self.pixmap)

    def transform_to_image_coordinate(self, pos : QPoint) -> QPoint:
        """
        Transforms the selected position into image coordinates space
        """
        if self._pixmap_item is None:
            return QPoint(0, 0)
        local_pos = self.mapFromGlobal(pos)
        scene_pos = self.mapToScene(local_pos)
        item_local_pos = self._pixmap_item.mapFromScene(scene_pos)
        x = math.floor(item_local_pos.x())
        y = math.floor(item_local_pos.y())
        return QPoint(x, y)

    def transform_to_scene_pos(self, pos : QPoint) -> QPoint:
        """
        Transforms a point into scene space
        """
        local_pos = self.mapFromGlobal(pos)
        scene_pos = self.mapToScene(local_pos)
        x = math.floor(scene_pos.x())
        y = math.floor(scene_pos.y())
        return QPoint(x, y)

    def pixel_within_bounds(self, pixel : QPoint) -> bool:
        """
        Checks if the selected pixel is within the image ranges,
        returns false if no image is available or the coordinates are out of range
        """
        if not self._hdri.is_pixmap_set():
            return False

        if self._hdri:
            pixmap = self._hdri.pixmap
            b1 = pixel.x() >= 0 and pixel.y() >= 0
            b2 = pixel.x() < pixmap.width() and pixel.y() < pixmap.height()
            return b1 and b2
        return False

    def display_image(self, pixmap : QPixmap):
        """
        Displays the image within the view
        """
        if len(self._scene.items()) > 0 and self._pixmap_item:
            self._pixmap_item.setPixmap(pixmap)
        else:
            item = self._scene.addPixmap(pixmap)
            item.setFlag(QGraphicsPixmapItem.ItemIsMovable)
            self.fitInView(item, Qt.KeepAspectRatio)
            self._pixmap_item = item
        # make sure the image fills the viewport
        self.reset()

    def update_image(self, pixmap : QPixmap):
        """
        Updates the render image in the view
        """
        items_list = self._scene.items()
        for item in items_list:
            if isinstance(item, QGraphicsPixmapItem):
                item.setPixmap(pixmap)

    # FIXME: have a separate function for loading the reference image
    def load_hdr_image(self, filepath, reference : bool = False) -> bool:
        """
        Loads a hdr (exr) image from a given filepath or bytestream
        Returns true if the image was successfully loaded
        :param filepath: string
        :return:
        """
        success = self._hdri.load_exr(filepath, reference)
        self.display_image(self._hdri.pixmap)
        return success

    def update_exposure(self, value : float):
        """
        Updates the exposure of the image, informs the HDRImage class.
        """
        self._hdri.exposure = value
        self.update_image(self._hdri.pixmap)

    def reset(self):
        """
        Resets the image view. Image sets to fit in view.
        """
        if self._pixmap_item:
            self.fitInView(self._pixmap_item, Qt.KeepAspectRatio)
            self._scene.setSceneRect(self._scene.itemsBoundingRect())

    def clear(self):
        self._scene.clear()
        self._pixmap_item = None
