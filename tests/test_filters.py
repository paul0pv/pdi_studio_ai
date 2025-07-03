# test_filters.py
import cv2
import numpy as np
from processing import filters  # Import the filters module

print("--- Testing processing/filters.py ---")

# Load a test image (make sure you have 'test_image.jpg' in your project root)
# You can download a sample image or use one from your webcam if you prefer.
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
        "Please create or place 'test_image.jpg' in the same directory as 'test_filters.py'."
    )
    print(
        "You can download one from: https://unsplash.com/photos/a-view-of-a-mountain-range-from-a-plane-window-G2834zL3o-Y"
    )
    exit()
except Exception as e:
    print(f"An error occurred while loading the image: {e}")
    exit()

# Display original image
cv2.imshow("Original Image", original_image)
cv2.waitKey(1)  # Small delay to ensure window opens

# --- Test Gaussian Blur ---
print("\nTesting Gaussian Blur...")
blurred_image = filters.apply_gaussian_blur(original_image, ksize=15)
cv2.imshow("Gaussian Blur (k=15)", blurred_image)
cv2.waitKey(1)

# --- Test Median Blur ---
print("Testing Median Blur...")
# For median blur, it's good to introduce some noise first to see its effect
noise = np.random.randint(0, 256, original_image.shape, dtype=np.uint8)
noisy_image = original_image + noise  # Simple way to add noise
median_blurred_image = filters.apply_median_blur(noisy_image, ksize=5)
cv2.imshow("Median Blur (k=5) on Noisy Image", median_blurred_image)
cv2.waitKey(1)

# --- Test Canny Edge Detection ---
print("Testing Canny Edge Detection...")
edges_image = filters.apply_canny_edge_detection(
    original_image, low_threshold=50, high_threshold=150
)
cv2.imshow("Canny Edges (50, 150)", edges_image)
cv2.waitKey(1)

# --- Test Grayscale Conversion ---
print("Testing Grayscale Conversion...")
grayscale_image = filters.convert_to_grayscale(original_image)
cv2.imshow("Grayscale", grayscale_image)
cv2.waitKey(1)

# --- Test Invert Colors ---
print("Testing Invert Colors...")
inverted_image = filters.invert_colors(original_image)
cv2.imshow("Inverted Colors", inverted_image)
cv2.waitKey(1)

# --- Test Brightness & Contrast Adjustment ---
print("Testing Brightness & Contrast Adjustment...")
bright_contrast_image = filters.adjust_brightness_contrast(
    original_image, alpha=1.5, beta=50
)  # More contrast, brighter
cv2.imshow("Bright & Contrast (alpha=1.5, beta=50)", bright_contrast_image)
cv2.waitKey(1)

# --- Test Sepia Tint ---
print("Testing Sepia Tint...")
sepia_image = filters.sepia_tint(original_image, strength=0.9)
cv2.imshow("Sepia Tint (strength=0.9)", sepia_image)
cv2.waitKey(1)

print("\nAll filter tests executed. Press any key to close image windows.")
cv2.waitKey(0)  # Wait indefinitely until a key is pressed
cv2.destroyAllWindows()
print("Tests complete.")
