# ui/widgets/preview_window.py

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
import cv2
import numpy as np


class PreviewWindow(QWidget):
    def __init__(
        self,
        original_frame: np.ndarray,
        processed_frame: np.ndarray,
        on_apply_callback=None,
    ):
        super().__init__()
        self.setWindowTitle("Comparación: Original vs Procesado")
        self.setMinimumSize(900, 500)
        self.on_apply_callback = on_apply_callback

        layout = QVBoxLayout()
        image_layout = QHBoxLayout()

        self.original_label = QLabel("Original")
        self.original_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.original_label.setPixmap(self._convert_frame_to_pixmap(original_frame))

        self.processed_label = QLabel("Procesado")
        self.processed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.processed_label.setPixmap(self._convert_frame_to_pixmap(processed_frame))

        image_layout.addWidget(self.original_label)
        image_layout.addWidget(self.processed_label)

        # Botones
        self.apply_button = QPushButton("Aplicar esta Pipeline")
        self.apply_button.clicked.connect(self._apply_pipeline)

        self.close_button = QPushButton("Cerrar")
        self.close_button.clicked.connect(self.close)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.close_button)

        layout.addLayout(image_layout)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def _convert_frame_to_pixmap(self, frame: np.ndarray) -> QPixmap:
        if len(frame.shape) == 3:
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            q_image = QImage(
                rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888
            )
        else:
            h, w = frame.shape
            q_image = QImage(frame.data, w, h, w, QImage.Format.Format_Grayscale8)

        return QPixmap.fromImage(q_image).scaled(
            420,
            420,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

    def _apply_pipeline(self):
        if self.on_apply_callback:
            self.on_apply_callback()
        self.close()
