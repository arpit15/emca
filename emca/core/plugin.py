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

from PySide2.QtWidgets import QWidget
from enum import Enum
import numpy as np
import abc
import typing
from ..model.pixel_data import PixelData

from ..renderer.scene_renderer import SceneRenderer
from ..stream.stream import Stream


class PluginType(Enum):
    """
    PluginType

    CORE_PLUGIN:
        works on local client render data received by server (default data)

    SERVER_PLUGIN:
        This plugin type needs server support which means a server plugin must be enabled.
        The plugin is enabled if a server plugin is added and available.
        Server plugins can request from the server for additional data types.
    """
    CORE_PLUGIN     = 0
    SERVER_PLUGIN   = 1


class Plugin(QWidget):
    """
    Plugin interface, inherits from QWidget

    The plugin interface can be used to visualizes own generated data sets.
    It can request own data from the server interface or work on the current render data,
    to visualize other aspects which are not implemented yet.

    New plugins are loaded via Plugins/__init__.py,
    therefore import new plugins there and add the class name to __all__ list.
    """

    def __init__(self, name, flag, plugin_type=PluginType.CORE_PLUGIN):
        QWidget.__init__(self, parent=None)
        self._name = name
        self._flag = flag
        self._plugin_type = plugin_type
        self._scene_renderer = None

    @property
    def flag(self) -> int:
        """
        Returns the unique identifier of the plugin
        :return: flag (unique identifier)
        """
        return self._flag

    @property
    def name(self) -> str:
        """
        Returns the name of the plugin
        :return: plugin name
        """
        return self._name

    @property
    def plugin_type(self) -> PluginType:
        """
        Returns the PluginType
        :return: PluginType.CORE_PLUGIN | PluginType.SERVER_PLUGIN
        """
        return self._plugin_type

    @property
    def scene_renderer(self) -> SceneRenderer:
        """
        Return the renderer
        Allows plugin full control of renderer
        Plugin itself has to handle add / remove of items
        """
        return self._scene_renderer

    @scene_renderer.setter
    def scene_renderer(self, scene_renderer : SceneRenderer):
        """
        Sets the renderer
        Allows plugin full control of renderer
        Plugin itself has to handle add / remove of items
        """
        self._scene_renderer = scene_renderer

    def send_update_path_indices(self, indices : np.ndarray, add_item : bool):
        """
        This function gets overwritten by the plugin view container,
        which will connect this function with the controller
        """

    def send_select_path(self, path_idx : typing.Optional[int]):
        """
        This function gets overwritten by the plugin view container,
        which will connect this function with the controller
        """

    def send_select_intersection(self, path_idx : typing.Optional[int], its_idx : typing.Optional[int]):
        """
        This function gets overwritten by the plugin view container,
        which will connect this function with the controller
        """

    @abc.abstractmethod
    def apply_theme(self, theme):
        """
        Apply the current theme 'light' | 'dark' to the plugins view
        :param: theme (dark|light)
        :return:
        """

    @abc.abstractmethod
    def init_pixel_data(self, pixel_data : PixelData):
        """
        Apply current pixel render data to plugins
        """

    @abc.abstractmethod
    def prepare_new_data(self):
        """
        Resets all views and prepares class for new incoming pixel data package
        """

    @abc.abstractmethod
    def update_path_indices(self, indices : np.ndarray):
        """
        Sends list of path indices to all views to update selected paths
        """

    @abc.abstractmethod
    def select_path(self, path_idx : typing.Optional[int]):
        """
        Will be called if a path element is selected within the view
        """

    @abc.abstractmethod
    def select_intersection(self, path_idx : typing.Optional[int], its_idx : typing.Optional[int]):
        """
        Will be called if a intersection element is selected within the view
        """

    @abc.abstractmethod
    def serialize(self, stream : Stream):
        """
        Send data to server
        """

    @abc.abstractmethod
    def deserialize(self, stream : Stream):
        """
        Receive data from server
        Will be handled within an extra thread,
        therefore do not update Qt view elements within this function
        """

    @abc.abstractmethod
    def update_view(self):
        """
        This function will be called after deserialize is finished
        It will update all data within the view
        """
