# gl_widget.py

from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtGui import QImage
from PyQt5.QtCore import Qt
from OpenGL.GL import *
from OpenGL.GLU import *
import pywavefront
import numpy as np


class GLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)
        self.image = None
        self.texture_id = None
        self.model = None
        self.object_rot = [0, 0, 0]  # Rotation angles for the 3D object
        self.object_trans = [0, 0, 0]  # Translation along X, Y, Z
        self.object_scale = 1.0        # Uniform scaling factor
        self.last_pos = None

    def load_image(self, image_path):
        self.image = QImage(image_path)
        self.update()

    def load_model(self, obj_path):
        try:
            # Load the model with collect_faces=True to ensure faces are loaded
            self.model = pywavefront.Wavefront(obj_path, collect_faces=True)
            self.update()
        except Exception as e:
            print(f"Failed to load model: {e}")

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glClearColor(0.0, 0.0, 0.0, 1.0)

    def resizeGL(self, w, h):
        if h == 0:
            h = 1
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        # Set perspective projection
        gluPerspective(45, w / h, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Position the camera
        gluLookAt(0, 0, 5,   # Eye position
                  0, 0, 0,   # Look at
                  0, 1, 0)   # Up vector

        # Draw the background image as a textured quad
        if self.image:
            self.draw_background()

        # Apply translation, scaling, and rotation to the 3D model
        glTranslatef(self.object_trans[0], self.object_trans[1], self.object_trans[2])
        glScalef(self.object_scale, self.object_scale, self.object_scale)
        glRotatef(self.object_rot[0], 1, 0, 0)
        glRotatef(self.object_rot[1], 0, 1, 0)
        glRotatef(self.object_rot[2], 0, 0, 1)

        # Draw the 3D model
        if self.model:
            self.draw_model()

    def draw_background(self):
        # Delete existing texture to prevent memory leaks
        if self.texture_id:
            glDeleteTextures([self.texture_id])

        # Convert the QImage to a format suitable for OpenGL and flip it vertically
        # This compensates for the Y-axis difference between Qt and OpenGL
        image = self.image.convertToFormat(QImage.Format_RGBA8888).mirrored(False, True)

        width = image.width()
        height = image.height()
        img_data = image.bits().asstring(width * height * 4)

        # Generate a new texture ID
        self.texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)

        # Set texture parameters
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glEnable(GL_TEXTURE_2D)
        glDisable(GL_DEPTH_TEST)  # Disable depth testing to render the background first

        # Save current projection and modelview matrices
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()

        # Set orthographic projection to stretch the image to fill the window
        glOrtho(-1, 1, -1, 1, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # Render a quad covering the viewport with the image texture
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-1, -1, -1)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(1, -1, -1)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(1, 1, -1)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(-1, 1, -1)
        glEnd()

        # Restore previous projection and modelview matrices
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

        glEnable(GL_DEPTH_TEST)  # Re-enable depth testing
        glDisable(GL_TEXTURE_2D)

    def draw_model(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glColor3f(0.8, 0.8, 0.8)  # Set model color

        # Position lights
        glLightfv(GL_LIGHT0, GL_POSITION, [10, 10, 10, 1])
        glLightfv(GL_LIGHT1, GL_POSITION, [-10, -10, 10, 1])

        for name, mesh in self.model.meshes.items():
            glBegin(GL_TRIANGLES)
            for face in mesh.faces:
                for vertex in face:
                    # Each vertex can be a tuple of (vertex_index, texture_index, normal_index)
                    if isinstance(vertex, tuple):
                        vertex_index, tex_index, normal_index = vertex
                    else:
                        # If the face only contains vertex indices
                        vertex_index = vertex
                        normal_index = None

                    # If normals are available, set them
                    if normal_index is not None and normal_index < len(self.model.parser.normals):
                        normal = self.model.parser.normals[normal_index]
                        glNormal3f(normal[0], normal[1], normal[2])
                    else:
                        # If no normals are present, set a default normal
                        glNormal3f(0.0, 0.0, 1.0)

                    # Get the vertex coordinates
                    vertex_coords = self.model.vertices[vertex_index]
                    glVertex3f(vertex_coords[0], vertex_coords[1], vertex_coords[2])
            glEnd()

        glDisable(GL_LIGHTING)

    def mousePressEvent(self, event):
        self.last_pos = event.pos()

    def mouseMoveEvent(self, event):
        if not self.last_pos:
            return

        dx = event.x() - self.last_pos.x()
        dy = event.y() - self.last_pos.y()

        if event.buttons() & Qt.LeftButton:
            self.object_rot[0] += dy
            self.object_rot[1] += dx
        elif event.buttons() & Qt.RightButton:
            self.object_trans[0] += dx * 0.01
            self.object_trans[1] -= dy * 0.01

        self.update()
        self.last_pos = event.pos()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.object_scale += delta * 0.001
        self.object_scale = max(0.1, self.object_scale)  # Prevent negative or zero scaling
        self.update()
