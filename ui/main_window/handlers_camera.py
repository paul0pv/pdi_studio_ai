# ui/main_window/handlers_camera.py

from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtCore import QDateTime
import cv2


def setup_camera_handlers(main_window):
    main_window.play_pause_button.clicked.connect(
        lambda: _toggle_camera_feed(main_window)
    )
    main_window.capture_button.clicked.connect(lambda: _capture_frame(main_window))
    main_window.camera_selector.camera_changed.connect(
        lambda _: _on_camera_selected(main_window)
    )


def _toggle_camera_feed(main_window):
    if main_window.camera_is_running:
        main_window.camera_feed.pause()
        main_window.play_pause_button.setText("Reproducir")
        main_window.camera_is_running = False
        main_window.show_status_message("Flujo de cámara pausado.")
    else:
        main_window.camera_feed.resume()
        main_window.play_pause_button.setText("Pausar")
        main_window.camera_is_running = True
        main_window.show_status_message("Flujo de cámara reanudado.")


def _capture_frame(main_window):
    frame = main_window.current_processed_frame
    if frame is None:
        main_window.show_status_message("⚠️ No hay fotogramas para capturar.")
        return

    timestamp = QDateTime.currentDateTime().toString("yyyyMMdd_hhmmsszzz")
    default_filename = f"capture_{timestamp}.png"
    file_path, _ = QFileDialog.getSaveFileName(
        main_window,
        "Guardar Imagen Capturada",
        default_filename,
        "PNG Images (*.png);;All Files (*)",
    )

    if file_path:
        if cv2.imwrite(file_path, frame):
            main_window.show_status_message(f"Imagen guardada en {file_path}")
        else:
            main_window.show_status_message("❌ Error al guardar la imagen.")
    else:
        main_window.show_status_message("Captura cancelada.")


def _on_camera_selected(main_window):
    try:
        index = int(main_window.camera_selector.currentText().split()[-1])
        main_window.camera_feed.switch_camera(index)
        main_window.show_status_message(f"🎥 Cámara cambiada a índice {index}")
    except Exception as e:
        main_window.show_status_message(f"❌ Error al cambiar de cámara: {e}")
