# ui/main_window/layout_video.py

from PyQt6.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QFrame,
)
from PyQt6.QtCore import Qt
from ui.widgets.camera_selector import CameraSelectorWidget


def build_video_area(main_window):
    def on_camera_selected(index):
        main_window.camera_feed.switch_camera(index)
        main_window.show_status_message(f"🎥 Cámara cambiada a índice {index}")

    layout = QVBoxLayout()
    main_window.video_label = QLabel("Esperando flujo de video...")
    main_window.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    main_window.video_label.setFixedSize(640, 480)
    main_window.video_label.setFrameShape(QFrame.Shape.Box)
    layout.addWidget(main_window.video_label)

    controls = QHBoxLayout()
    main_window.play_pause_button = QPushButton("Pausar")
    main_window.capture_button = QPushButton("Capturar Imagen")
    main_window.camera_selector = CameraSelectorWidget(on_camera_selected)
    controls.addWidget(main_window.camera_selector)

    controls.addWidget(main_window.play_pause_button)
    controls.addWidget(main_window.capture_button)

    layout.addLayout(controls)
    return layout
