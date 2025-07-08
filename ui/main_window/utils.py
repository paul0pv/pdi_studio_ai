# ui/main_window/utils.py

from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import QMessageBox
import numpy as np
from PyQt6.QtCore import QDateTime


def convert_frame_to_qimage(frame: np.ndarray) -> QImage:
    h, w = frame.shape[:2]
    if len(frame.shape) == 3:
        from cv2 import cvtColor, COLOR_BGR2RGB

        rgb = cvtColor(frame, COLOR_BGR2RGB)
        return QImage(rgb.data, w, h, 3 * w, QImage.Format.Format_RGB888)
    else:
        return QImage(frame.data, w, h, w, QImage.Format.Format_Grayscale8)


def get_timestamp_filename(prefix="capture") -> str:
    timestamp = QDateTime.currentDateTime().toString("yyyyMMdd_hhmmsszzz")
    return f"{prefix}_{timestamp}.png"


def show_error_dialog(parent, message: str):
    QMessageBox.critical(parent, "Error", message)
