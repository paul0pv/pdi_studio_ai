# test_camera_feed.py
import cv2
import numpy as np
import time
from video_capture.camera_feed import CameraFeed
from PyQt6.QtWidgets import QApplication  # Needed for QApplication loop

print("--- Testing video_capture/camera_feed.py ---")

# QApplication is needed even if we don't have a full UI,
# because QThread (which CameraFeed inherits) relies on QApplication's event loop.
app = QApplication([])


def receive_frame(frame: np.ndarray):
    """Simple function to receive and display frames."""
    if frame is not None:
        print(f"Received frame with shape: {frame.shape}")
        cv2.imshow("Camera Feed Test", frame)
        cv2.waitKey(1)  # Needed for imshow to update


# Create an instance of CameraFeed
camera_test = CameraFeed(camera_index=0)  # Use 0 for default webcam

# Connect the signal to our receiving function
camera_test.frame_ready.connect(receive_frame)

# Start the camera thread
camera_test.start()
print("CameraFeed thread started. Waiting for frames...")

# Run the QApplication event loop for a few seconds to let the thread run
# In a real app, this would be app.exec()
try:
    for i in range(100):  # Run for approx. 100 * 1ms = 100ms * some_fps
        QApplication.processEvents()  # Process events in main thread (for signals to work)
        time.sleep(0.1)  # Simulate main thread doing other work
    print("\nSimulated 10 seconds of capture. Now stopping...")

except KeyboardInterrupt:
    print("\nTest interrupted by user.")
finally:
    # Stop the camera thread cleanly
    camera_test.stop()
    camera_test.wait()  # Wait for the thread to finish execution
    cv2.destroyAllWindows()
    print("CameraFeed test finished.")
    app.quit()  # Exit the QApplication
