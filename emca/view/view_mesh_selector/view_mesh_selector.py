from PySide2.QtWidgets import QWidget, QCheckBox
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtCore import Qt
import logging

from emca.model.contribution_data import SampleContributionData

import typing
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from emca.controller.controller import Controller
else:
    from typing import Any as Controller

class MeshCheckBox(QCheckBox):
  def __init__(self, name, mesh, default_opacity, parent=None):
    self._mesh = mesh
    self._default_opacity = default_opacity
    super().__init__(name, parent=parent)

    self.state_changed(True)

  def state_changed(self, checked):
    if checked:
      self._mesh.opacity = self._default_opacity
    else:
      self._mesh.opacity = 0.0
      # need to manually update the scene
   
class ViewMeshSelector(QWidget):
  def __init__(self, parent=None) -> None:
    super().__init__(parent=parent)

    self._controller = None
    self._meshes = None
    self._meshbuttons = []
    self._visible = True

    self.layout = QVBoxLayout(self)

  def set_controller(self, controller : Controller):
    """
    Sets the connection to the controller
    """
    self._controller = controller

  @property
  def visible(self):
    return self._visible

  @visible.setter
  def visible(self, visible):
    self._visible = visible
    if self._visible:
      self.clear_meshes()
      self.set_meshes()
        
  def set_meshes(self):
    if self._controller is not None:
      scene_renderer = self._controller._view.view_render_scene.scene_renderer
      self._meshes = scene_renderer._meshes
      # setup a checkbox for each of them
      default_opacity = scene_renderer._scene_options.get("opacity", 0.25)
      for i, mesh in enumerate(self._meshes):
        btn = MeshCheckBox(f"Mesh {i}", mesh, default_opacity)
        btn.setCheckState(Qt.Checked)
        btn.toggled.connect(btn.state_changed)
        self.layout.addWidget(btn)
        self._meshbuttons.append(btn)

  def clear_meshes(self):
    self._meshes = []
    for btn in self._meshbuttons:
      self.layout.removeWidget(btn)
      # following does delete but doesn't make the button again
      btn.deleteLater()

    self._meshbuttons = []
    