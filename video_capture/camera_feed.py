# video_capture/camera_feed.py

import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal, QMutex  # Import QMutex for thread safety


class CameraFeed(QThread):
    # Define a signal that will emit a NumPy array (the captured frame)
    frame_ready = pyqtSignal(np.ndarray)

    def __init__(self, camera_index=0):
        """
        Initializes the CameraFeed thread.

        Args:
            camera_index (int): The index of the camera to use (e.g., 0 for default webcam).
        """
        super().__init__()
        self.camera_index = camera_index
        self.cap = None  # OpenCV VideoCapture object
        self._running = (
            True  # Flag to control the thread's loop (overall thread activity)
        )
        self._capturing = True  # Flag to control frame capturing within the loop
        self._mutex = QMutex()  # Mutex for _capturing flag access

    def run(self):
        """
        This method is executed when the thread starts.
        It continuously captures frames from the camera.
        """
        print(f"Attempting to open camera at index {self.camera_index}...")
        self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap.isOpened():
            print(f"Error: Could not open camera at index {self.camera_index}.")
            self._running = False  # Stop the thread if camera cannot be opened
            # Optionally, emit an error signal here
            return

        print("Camera opened successfully. Starting frame capture loop...")
        while self._running:
            self._mutex.lock()
            is_capturing = self._capturing
            self._mutex.unlock()

            if is_capturing:
                ret, frame = self.cap.read()  # Read a frame from the camera

                if ret:
                    # If frame is successfully read, emit it through the signal
                    self.frame_ready.emit(frame)
                else:
                    print(
                        "Warning: Could not read frame from camera. Attempting to re-open or stopping..."
                    )
                    if not self.cap.isOpened():
                        self._running = False
                        print("Camera lost connection. Stopping capture thread.")
                    break  # Exit loop on persistent failure
            else:
                # If paused, sleep a bit longer to reduce CPU usage
                self.msleep(100)  # Sleep for 100 milliseconds when paused

            # Give a small pause to allow other threads/events to process
            # This can help reduce CPU usage and keep the UI responsive.
            # Adjust based on desired frame rate and system performance.
            # self.msleep(1) # This small sleep is mostly for active capture, moved to 'else' above

        # Clean up resources when the loop finishes
        if self.cap:
            self.cap.release()
        print("CameraFeed thread stopped.")

    def stop(self):
        """
        Sets the internal flag to stop the thread's execution loop (terminates thread).
        """
        self._running = False
        # Do not wait() here, as it might cause a deadlock if called from main thread
        # and the run loop is stuck or waiting for something.
        # MainWindow.closeEvent should handle the wait().

    def stop_capture_loop(self):
        """Pauses the frame capturing without stopping the thread entirely."""
        self._mutex.lock()
        self._capturing = False
        self._mutex.unlock()
        print("CameraFeed: Capture loop paused.")

    def start_capture_loop(self):
        """Resumes the frame capturing."""
        self._mutex.lock()
        self._capturing = True
        self._mutex.unlock()
        print("CameraFeed: Capture loop resumed.")
