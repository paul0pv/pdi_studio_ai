from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox
from PyQt6.QtCore import pyqtSignal
from video_capture.camera_utils import list_available_cameras


class CameraSelectorWidget(QWidget):
    camera_changed = pyqtSignal(int)

    def __init__(self, on_camera_selected_callback=None, parent=None):
        super().__init__(parent)
        self.on_camera_selected = on_camera_selected_callback

        self.combo = QComboBox()
        self.combo.currentIndexChanged.connect(self._emit_camera_changed)

        layout = QHBoxLayout()
        layout.addWidget(QLabel("Cámara:"))
        layout.addWidget(self.combo)
        self.setLayout(layout)

        self.refresh_camera_list()

    def refresh_camera_list(self):
        self.combo.clear()
        cameras = list_available_cameras()
        if not cameras:
            self.combo.addItem("No disponible")
            self.combo.setEnabled(False)
        else:
            for index in cameras:
                self.combo.addItem(f"Cam {index}", userData=index)
            self.combo.setEnabled(True)

    def _emit_camera_changed(self, index):
        cam_index = self.combo.itemData(index)
        if cam_index is not None:
            if self.on_camera_selected:
                self.on_camera_selected(cam_index)
            self.camera_changed.emit(cam_index)


#    def _on_selection_changed(self, index):
#        cam_index = self.combo.currentData()
#        if cam_index is not None:
#            self.on_camera_selected(cam_index)
