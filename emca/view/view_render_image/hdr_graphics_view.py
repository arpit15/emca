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

from emca.core.hdr_graphics_view_base import HDRGraphicsViewBase
from PySide2.QtCore import QPoint, QRect, QSize, Signal
from PySide2.QtWidgets import QRubberBand
import logging


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from view.view_render_image.view_render_image import ViewRenderImage
else:
    from typing import Any as ViewRenderImage


class HDRGraphicsView(HDRGraphicsViewBase):

    """
        HDRGraphicsView
        Custom QGraphicsView which holds the rendered image and handles interactions
    """
    rectChanged = Signal(QRect)
    def __init__(self, parent : ViewRenderImage):
        HDRGraphicsViewBase.__init__(self)
        self._parent = parent
        self._old_scene_pos = QPoint()

        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.changeRubberBand = False

        self._rect_top_left = QPoint()
        self._rect_bot_right = QPoint()

    def mousePressEvent(self, q_mouse_event):
        """
        Handles a mouse press event, aves the current position.
        A request to the controller will only be send if the position will be the same after mouse btn release.
        :param q_mouse_event:
        :return:
        """
        global_pos = q_mouse_event.globalPos()
        self._rect_top_left = global_pos
        self._old_scene_pos = self.transform_to_scene_pos(global_pos)

        self.changeRubberBand = True

        # super().mousePressEvent(q_mouse_event)

    def mouseReleaseEvent(self, q_mouse_event):
        """
        Handles a mouse button release.
        Informs the controller if the position has not changed since the click.
        Otherwise the image will be moved.
        :param q_mouse_event:
        :return:
        """
        global_pos = q_mouse_event.globalPos()
        self._rect_bot_right = global_pos
        new_pos = self.transform_to_scene_pos(global_pos)
        if self._old_scene_pos == new_pos:
            pixel = self.transform_to_image_coordinate(q_mouse_event.globalPos())
            # instead of a single pixel iterate over all rect data
            if self.pixel_within_bounds(pixel):
                self._parent.request_pixel_data(pixel)

        self.changeRubberBand = False

        rect = QRect(
            self._rect_top_left, 
            self._rect_bot_right
        )
        self.rubberBand.setGeometry(rect)
        self.rectChanged.emit(self.rubberBand.geometry())
        self.rubberBand.show()

        # the following fails as the request is sent over a single connection
        # iterate over all the pixels and get their info
        # rect_size = rect.size()
        # for y in range(rect_size.height()):
        #     for x in range(rect_size.width()):
        #         currPt = QPoint(rect.topLeft().x() + x, rect.topLeft().y() + y)
        #         pixel = self.transform_to_image_coordinate(currPt)
        #         # instead of a single pixel iterate over all rect data
        #         if self.pixel_within_bounds(pixel):
        #             self._parent.request_pixel_data(pixel)

        # super().mouseReleaseEvent(q_mouse_event)

    def mouseMoveEvent(self, q_mouse_event):
        """
        Handles mouse move event
        :param q_mouse_event:
        :return:
        """
        image_coord = self.transform_to_image_coordinate(q_mouse_event.globalPos())
        text = '({},{})'.format(image_coord.x(), image_coord.y())
        self._parent.labelCurrentPos.setText(text)

        if self.changeRubberBand:
            self.rubberBand.setGeometry(QRect(self._old_scene_pos, q_mouse_event.pos()).normalized())
            self.rectChanged.emit(self.rubberBand.geometry())

        # super().mouseMoveEvent(q_mouse_event)

    def dropEvent(self, q_drop_event):
        try:
            super().dropEvent(q_drop_event)
            self._parent.enable_view(True)
            self._parent.save_last_rendered_image_filepath()
        except Exception as e:
            logging.error(e)

