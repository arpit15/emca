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

import typing
from ..stream.stream import Stream
from ..core.color import Color4f
from ..core.point import Point3f
from ..core.messages import ShapeType

import numpy as np

class MeshData(object):

    """
        MeshData
        This class represents one three-dimensional mesh object,
        consisting of vertices and triangle indices a specular and diffuse color.
    """

    def __init__(self):
        self._vertex_count = 0
        self._vertices = np.array([], 'f')

        self._triangle_count = 0
        self._triangles = np.array([], 'q')

        self._face_color_count = 0
        self._face_colors = None

        self._specular_color = Color4f()
        self._diffuse_color = Color4f()

    def deserialize(self, stream : Stream):
        """
        Deserialize a Mesh object from the socket stream.
        :param stream:
        :return:
        """

        self._vertex_count = stream.read_uint()
        self._vertices = np.array(stream.read_float_array(self._vertex_count*3), dtype=np.float32, copy=False)

        self._triangle_count = stream.read_uint()
        triangle_indices = np.array(stream.read_uint_array(self._triangle_count*3), dtype=np.uint32, copy=False)
        # vtk needs to know for each face that it has 3 vertices and they need to be 64bit signed ints
        self._triangles = np.array(np.concatenate([np.full([self._triangle_count, 1], 3, dtype=np.uint32),
                            triangle_indices.reshape([self._triangle_count, 3])], axis=1).flatten(), 'q')

        self._face_color_count = stream.read_uint()
        # face colors are optional
        if self._face_color_count > 0:
            self._face_colors = np.array(stream.read_float_array(self._face_color_count*3), dtype=np.float32, copy=False)

        # usually, each mesh just provides a diffuse color and a specular color
        self._diffuse_color = stream.read_color4f()
        self._specular_color = stream.read_color4f()


    @property
    def shape_type(self):
        return ShapeType.TriangleMesh

    @property
    def vertex_count(self) -> int:
        """
        Returns the amount of vertices of this mesh
        """
        return self._vertex_count

    @property
    def vertices(self) -> np.ndarray:
        """
        Returns a list containing all vertices (point3f numpy array)
        :return: np.array[point3f]
        """
        return self._vertices

    @property
    def face_colors(self) -> typing.Optional[np.ndarray]:
        """
        Returns a list containing all vertex colors (point3f numpy array)
        :return: np.array[point3f] or None
        """
        return self._face_colors

    @property
    def triangle_count(self) -> int:
        """
        Returns the amount of triangles
        """
        return self._triangle_count

    @property
    def triangles(self) -> np.ndarray:
        """
        Returns a list containing all triangles indices (point3i numpy array)
        :return: np.array[point3i,...]
        """
        return self._triangles

    @property
    def specular_color(self) -> Color4f:
        """
        Returns the specular color of the mesh object
        """
        return self._specular_color

    @property
    def diffuse_color(self) -> Color4f:
        """
        Returns the diffuse color of the mesh object
        """
        return self._diffuse_color

    def to_string(self) -> str:
        """
        Returns a string containing all information about the Mesh object
        """
        return 'vertexCount = {} \n' \
               'triangleCount = {} \n' \
               'specularColor = {} \n' \
               'diffuseColor = {} \n'.format(self._vertex_count,
                                             self._triangle_count,
                                             self._specular_color.to_string(),
                                             self._diffuse_color.to_string())


class SphereData(object):

    """
        SphereData
        This class represents one three-dimensional sphere object,
    """

    def __init__(self):
        self._radius = 1.0
        self._center = Point3f()
        self._specular_color = Color4f()
        self._diffuse_color = Color4f()

    def deserialize(self, stream : Stream):
        """
        Deserialize a Sphere object from the socket stream.
        :param stream:
        :return:
        """
        self._radius = stream.read_float()
        self._center = stream.read_point3f()
        self._diffuse_color = stream.read_color4f()
        self._specular_color = stream.read_color4f()

    @property
    def shape_type(self):
        return ShapeType.SphereMesh

    @property
    def radius(self) -> float:
        """
        Returns the radius of the sphere
        """
        return self._radius

    @property
    def center(self) -> Point3f:
        """
        Return the center point of the sphere
        """
        return self._center

    @property
    def specular_color(self) -> Color4f:
        """
        Returns the specular color of the mesh object
        """
        return self._specular_color

    @property
    def diffuse_color(self) -> Color4f:
        """
        Returns the diffuse color of the mesh object
        """
        return self._diffuse_color

    def to_string(self) -> str:
        """
        Returns a string containing all information about the Mesh object
        """
        return 'radius = {} \n' \
               'center = {} \n' \
               'specularColor = {} \n' \
               'diffuseColor = {} \n'.format(self._radius,
                                             self._center,
                                             self._specular_color.to_string(),
                                             self._diffuse_color.to_string())


class ShapeData(object):

    """
        ShapeData
        Holds all Mesh objects which are in the 3D scene
    """

    def __init__(self):
        self._meshes = []

    def deserialize(self, stream : Stream):
        """
        Deserializes a mesh object from the socket stream and appends it to the overall mesh list
        :param stream:
        :return:
        """
        shape_type = stream.read_short()
        # logging.info("ShapeType: {}".format(shape_type))
        if shape_type == ShapeType.TriangleMesh.value:
            mesh = MeshData()
            mesh.deserialize(stream)
            self._meshes.append(mesh)
        elif shape_type == ShapeType.SphereMesh.value:
            sphere = SphereData()
            sphere.deserialize(stream)
            self._meshes.append(sphere)

    @property
    def mesh_count(self) -> int:
        """
        Returns the amount of objects in the 3D scene
        """
        return len(self._meshes)

    @property
    def meshes(self) -> typing.List[typing.Union[MeshData, SphereData]]:
        """
        Returns the list of objects
        :return: list[mesh,...]
        """
        return self._meshes

    def to_string(self) -> str:
        """
        Returns a string with information about all mesh objects
        """
        oss = 'meshCount = {} \n'.format(len(self._meshes))
        for mesh in self._meshes:
            oss = oss + "Mesh = { \n" + mesh.to_string() + "} \n \n"
        return oss

    def clear(self):
        """
        Clears the list of all mesh objects
        """
        self._meshes.clear()
