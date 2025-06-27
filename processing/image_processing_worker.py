# processing/image_processing_worker.py
import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal, QMutex
from processing.image_processor import (
    ImageProcessor,
)  # Import the existing ImageProcessor


class ImageProcessingWorker(QThread):
    """
    A QThread subclass to handle the image processing pipeline in a separate thread,
    preventing the main UI thread from freezing.
    """

    processed_frame_ready = pyqtSignal(
        np.ndarray, np.ndarray
    )  # Emits (processed_color_frame, histogram_data)
    error_occurred = pyqtSignal(str)  # For general errors

    def __init__(self, image_processor: ImageProcessor, parent=None):
        super().__init__(parent)
        self._image_processor = image_processor
        self._frame_queue = []  # Queue to hold incoming frames
        self._mutex = QMutex()  # Mutex for thread-safe access to the queue
        self._running = True

    def run(self):
        """
        The main loop of the worker thread. It continuously processes frames
        from the queue.
        """
        print("ImageProcessingWorker: Thread started.")
        while self._running:
            frame = None
            self._mutex.lock()
            if self._frame_queue:
                frame = self._frame_queue.pop(0)  # Get the oldest frame
            self._mutex.unlock()

            if frame is not None:
                try:
                    # Process the frame using the ImageProcessor
                    processed_frame = self._image_processor.process_frame(frame)

                    # Calculate histogram from the processed frame (converted to grayscale if needed)
                    if len(processed_frame.shape) == 3:  # If color
                        processed_grayscale_for_hist = cv2.cvtColor(
                            processed_frame, cv2.COLOR_BGR2GRAY
                        )
                    else:  # Already grayscale
                        processed_grayscale_for_hist = processed_frame

                    hist_data = self._image_processor.get_histogram_data(
                        processed_grayscale_for_hist
                    )

                    # Emit the processed frame and histogram data
                    self.processed_frame_ready.emit(processed_frame, hist_data)
                except Exception as e:
                    self.error_occurred.emit(f"Error processing frame: {e}")
                    print(f"ImageProcessingWorker Error: {e}")
            else:
                self.msleep(
                    1
                )  # Sleep briefly if no frames to process to avoid busy-waiting

        print("ImageProcessingWorker: Thread stopped.")

    def enqueue_frame(self, frame: np.ndarray):
        """
        Adds a new frame to the processing queue. Called from the main thread.
        """
        self._mutex.lock()
        # Optionally, clear the queue before adding new frame to prioritize latest frames
        # This prevents backlog if processing is slower than capture
        if len(self._frame_queue) > 1:  # Keep only the very latest frame if backlog
            self._frame_queue.clear()
        self._frame_queue.append(frame)
        self._mutex.unlock()

    def set_pipeline_config(self, pipeline_config: list):
        """
        Updates the image processor's pipeline configuration.
        This method is safe to call from the main thread as it just calls a setter.
        """
        self._image_processor.set_pipeline(pipeline_config)

    def stop(self):
        """
        Stops the worker thread's execution loop.
        """
        self._running = False
        self.wait()  # Wait for the thread to finish its current task and exit
