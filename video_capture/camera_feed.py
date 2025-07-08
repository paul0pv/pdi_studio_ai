# video_capture/camera_feed.py

import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition


class CameraFeed(QThread):
    frame_ready = pyqtSignal(np.ndarray)

    def __init__(self, camera_index=1, max_retries=3, frame_delay_ms=10):
        super().__init__()
        self.camera_index = camera_index
        self._mutex = QMutex()
        self._condition = QWaitCondition()
        self._running = True
        self._capturing = True
        self._latest_frame = None
        self.max_retries = max_retries
        self.frame_delay_ms = frame_delay_ms

    def run(self):
        retry_count = 0
        while self._running and retry_count < self.max_retries:
            self._mutex.lock()
            if not self._capturing:
                self._condition.wait(self._mutex)
            self._mutex.unlock()

            cap = cv2.VideoCapture(self.camera_index)
            if not cap.isOpened():
                print(
                    f"[CameraFeed] ❌ No se pudo abrir la cámara {self.camera_index}. Reintentando..."
                )
                retry_count += 1
                self.msleep(500)
                continue

            print(f"[CameraFeed] ✅ Cámara {self.camera_index} abierta correctamente.")
            retry_count = 0  # Reset if correctly opened

            while self._running:
                self._mutex.lock()
                capturing = self._capturing
                self._mutex.unlock()

                if not capturing:
                    break

                ret, frame = cap.read()
                if not ret or frame is None:
                    print(
                        "[CameraFeed] ⚠️ Fallo al leer frame. Intentando reconectar..."
                    )
                    break

                self._mutex.lock()
                self._latest_frame = frame.copy()
                self._mutex.unlock()

                self.frame_ready.emit(frame)
                self.msleep(self.frame_delay_ms)

            cap.release()
            self.msleep(100)

        print(
            "[CameraFeed] 🛑 Finalizado por máximo reintentos."
            if retry_count >= self.max_retries
            else "[CameraFeed] 🧩 Detenido por usuario."
        )

    def stop(self):
        self._mutex.lock()
        self._running = False
        self._condition.wakeAll()
        self._mutex.unlock()

    def pause(self):
        self._mutex.lock()
        self._capturing = False
        self._mutex.unlock()

    def resume(self):
        self._mutex.lock()
        self._capturing = True
        self._condition.wakeAll()
        self._mutex.unlock()

    def switch_camera(self, new_index: int):
        print(f"[CameraFeed] 🔄 Cambiando a cámara {new_index}")
        self.pause()
        self.camera_index = new_index
        self.resume()

    def get_latest_frame(self):
        self._mutex.lock()
        frame = self._latest_frame.copy() if self._latest_frame is not None else None
        self._mutex.unlock()
        return frame
