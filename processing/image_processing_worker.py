# processing/image_processing_worker.py

import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal, QMutex
from processing.image_processor import ImageProcessor


class ImageProcessingWorker(QThread):
    """
    Hilo dedicado al procesamiento de imágenes en segundo plano.
    Utiliza un ImageProcessor y emite señales con los resultados.
    """

    processed_frame_ready = pyqtSignal(np.ndarray, np.ndarray)
    error_occurred = pyqtSignal(str)

    def __init__(
        self, image_processor: ImageProcessor, parent=None, max_queue_size: int = 2
    ):
        super().__init__(parent)
        self._image_processor = image_processor
        self._frame_queue = []
        self._mutex = QMutex()
        self._running = True
        self._max_queue_size = max_queue_size

    def run(self):
        print("[ImageProcessingWorker] Hilo iniciado.")
        while self._running:
            frame = self._dequeue_frame()
            if frame is not None:
                self._process_frame(frame)
            else:
                self.msleep(1)
        print("[ImageProcessingWorker] Hilo detenido.")

    def _dequeue_frame(self) -> np.ndarray:
        self._mutex.lock()
        frame = self._frame_queue.pop(0) if self._frame_queue else None
        self._mutex.unlock()
        return frame

    def _process_frame(self, frame: np.ndarray):
        try:
            processed = self._image_processor.process_frame(frame)

            if len(processed.shape) == 3:
                gray = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
            else:
                gray = processed

            hist = self._image_processor.get_histogram_data(gray)
            self.processed_frame_ready.emit(processed, hist)

        except Exception as e:
            self.error_occurred.emit(f"❌ Error procesando frame: {e}")
            print(f"[ImageProcessingWorker] Error: {e}")

    def enqueue_frame(self, frame: np.ndarray):
        self._mutex.lock()
        if len(self._frame_queue) >= self._max_queue_size:
            self._frame_queue.clear()
        self._frame_queue.append(frame)
        self._mutex.unlock()

    def set_pipeline_config(self, pipeline_config: list):
        self._image_processor.set_pipeline(pipeline_config)

    def stop(self):
        self._running = False
        self.wait()
