# image_viewer.py

import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QAction,
    QFileDialog,
    QWidget,
    QHBoxLayout,
)
from PyQt5.QtCore import Qt

from gl_widget import GLWidget  # Ensure gl_widget.py is in the same directory


class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pose Annotation Tool")
        self.setGeometry(100, 100, 1200, 800)

        # Central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Initialize OpenGL Widget
        self.gl_widget = GLWidget(self)
        self.layout.addWidget(self.gl_widget, 1)

        # Create the menu bar
        self.create_menu()

    def create_menu(self):
        menubar = self.menuBar()

        # Create 'File' menu
        file_menu = menubar.addMenu("File")

        # Create 'Load Image' action
        load_image_action = QAction("Load Image", self)
        load_image_action.setShortcut("Ctrl+O")
        load_image_action.setStatusTip("Load an image from file")
        load_image_action.triggered.connect(self.load_image)

        # Create 'Load 3D Model' action
        load_model_action = QAction("Load 3D Model", self)
        load_model_action.setShortcut("Ctrl+M")
        load_model_action.setStatusTip("Load a 3D .obj model")
        load_model_action.triggered.connect(self.load_model)

        # Create 'Exit' action
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.close)

        # Add actions to the 'File' menu
        file_menu.addAction(load_image_action)
        file_menu.addAction(load_model_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

    def load_image(self):
        # Open a file dialog to select an image
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)",
            options=options,
        )
        if file_path:
            # Load the image and set it as background
            self.gl_widget.load_image(file_path)
            self.statusBar().showMessage(f"Loaded image: {file_path}", 5000)

    def load_model(self):
        # Open a file dialog to select a .obj file
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load 3D Model",
            "",
            "OBJ Files (*.obj);;All Files (*)",
            options=options,
        )
        if file_path:
            self.gl_widget.load_model(file_path)
            self.statusBar().showMessage(f"Loaded 3D model: {file_path}", 5000)


def main():
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
