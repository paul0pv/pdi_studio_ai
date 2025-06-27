# test_image_processor.py
import cv2
import numpy as np
from processing.image_processor import ImageProcessor  # Import the class

print("--- Testing processing/image_processor.py ---")

try:
    original_image = cv2.imread("test_image.jpg")
    if original_image is None:
        raise FileNotFoundError(
            "test_image.jpg not found. Please provide a test image."
        )
    print("Test image loaded successfully.")
except FileNotFoundError as e:
    print(f"Error: {e}")
    print(
        "Please create or place 'test_image.jpg' in the same directory as 'test_image_processor.py'."
    )
    exit()
except Exception as e:
    print(f"An error occurred while loading the image: {e}")
    exit()

processor = ImageProcessor()
cv2.imshow("Original Image", original_image)
cv2.waitKey(1)

# --- Test add_filter and initial pipeline processing ---
print("\nStep 1: Adding Grayscale and Gaussian Blur.")
processor.add_filter("grayscale")
processor.add_filter("gaussian_blur", {"ksize": 11})
processed_image = processor.process_frame(original_image)
cv2.imshow("Pipeline: Grayscale + Gaussian (k=11)", processed_image)
cv2.waitKey(1)
print("Current Pipeline:", processor.pipeline)

# --- Test update_filter_params ---
print("\nStep 2: Updating Gaussian Blur ksize.")
# Assuming Gaussian Blur is at index 1 (0: grayscale, 1: gaussian_blur)
processor.update_filter_params(1, {"ksize": 25})
processed_image = processor.process_frame(original_image)
cv2.imshow("Pipeline: Grayscale + Gaussian (k=25)", processed_image)
cv2.waitKey(1)
print("Current Pipeline:", processor.pipeline)

# --- Test add another filter (Canny) ---
print("\nStep 3: Adding Canny Edge Detection.")
processor.add_filter(
    "canny_edge_detection", {"low_threshold": 30, "high_threshold": 100}
)
processed_image = processor.process_frame(original_image)
cv2.imshow("Pipeline: Grayscale + Gaussian + Canny", processed_image)
cv2.waitKey(1)
print("Current Pipeline:", processor.pipeline)

# --- Test remove_filter ---
print("\nStep 4: Removing Gaussian Blur (index 1).")
processor.remove_filter(1)  # Should remove Gaussian Blur
processed_image = processor.process_frame(original_image)
cv2.imshow("Pipeline: Grayscale + Canny (Gaussian removed)", processed_image)
cv2.waitKey(1)
print("Current Pipeline:", processor.pipeline)

# --- Test toggle_filter_enabled ---
print("\nStep 5: Disabling Grayscale (index 0).")
processor.toggle_filter_enabled(0, False)  # Disable grayscale
processed_image = processor.process_frame(original_image)
cv2.imshow(
    "Pipeline: Canny only (Grayscale disabled)", processed_image
)  # Should show color Canny if input is color
cv2.waitKey(1)
print("Current Pipeline:", processor.pipeline)

print("\nStep 6: Re-enabling Grayscale (index 0).")
processor.toggle_filter_enabled(0, True)  # Re-enable grayscale
processed_image = processor.process_frame(original_image)
cv2.imshow("Pipeline: Grayscale + Canny (Grayscale enabled again)", processed_image)
cv2.waitKey(1)
print("Current Pipeline:", processor.pipeline)

# --- Test move_filter ---
print("\nStep 7: Moving Canny Edge Detection up (index 1 to 0).")
# Canny is at index 1, Grayscale at 0
processor.move_filter(1, "up")  # Move Canny from index 1 to 0
processed_image = processor.process_frame(original_image)
cv2.imshow("Pipeline: Canny + Grayscale (Canny moved up)", processed_image)
cv2.waitKey(1)
print("Current Pipeline:", processor.pipeline)


# --- Test get_histogram_data ---
print("\nTesting Histogram Data Retrieval...")
hist_data = processor.get_histogram_data(original_image)
print(f"Histogram data shape: {hist_data.shape}, sum: {np.sum(hist_data)}")
# Expected shape is (256,) and sum should be (width * height) for grayscale

print("\nAll ImageProcessor tests executed. Press any key to close image windows.")
cv2.waitKey(0)
cv2.destroyAllWindows()
print("Tests complete.")
