# test_presets.py
import os
from config import presets  # Import the presets module

print("--- Testing config/presets.py ---")

TEST_PRESETS_FILE = "config/test_presets.json"  # Use a separate file for testing

# Ensure the config directory exists for the test file
os.makedirs("config", exist_ok=True)

# --- Test 1: Save an empty dictionary initially (simulates first run or empty file) ---
print("\nTest 1: Saving empty presets.")
presets.save_presets({}, file_path=TEST_PRESETS_FILE)
loaded_presets = presets.load_presets(file_path=TEST_PRESETS_FILE)
print("Loaded after saving empty:", loaded_presets)
assert loaded_presets == {}, "Test 1 failed: Should load an empty dict."

# --- Test 2: Add a new preset ---
print("\nTest 2: Adding 'Test Sepia' preset.")
test_sepia_pipeline = [
    {"name": "grayscale", "params": {}, "enabled": True},
    {"name": "sepia_tint", "params": {"strength": 0.8}, "enabled": True},
]
presets.add_preset("Test Sepia", test_sepia_pipeline, file_path=TEST_PRESETS_FILE)
loaded_presets = presets.load_presets(file_path=TEST_PRESETS_FILE)
print("Loaded after adding 'Test Sepia':", loaded_presets)
assert (
    "Test Sepia" in loaded_presets
    and loaded_presets["Test Sepia"] == test_sepia_pipeline
), "Test 2 failed: 'Test Sepia' not added correctly."

# --- Test 3: Add another preset ---
print("\nTest 3: Adding 'Test Blur' preset.")
test_blur_pipeline = [
    {"name": "gaussian_blur", "params": {"ksize": 9}, "enabled": True}
]
presets.add_preset("Test Blur", test_blur_pipeline, file_path=TEST_PRESETS_FILE)
loaded_presets = presets.load_presets(file_path=TEST_PRESETS_FILE)
print("Loaded after adding 'Test Blur':", loaded_presets)
assert (
    "Test Blur" in loaded_presets and loaded_presets["Test Blur"] == test_blur_pipeline
), "Test 3 failed: 'Test Blur' not added correctly."
assert len(loaded_presets) == 2, "Test 3 failed: Incorrect number of presets."

# --- Test 4: Update an existing preset ---
print("\nTest 4: Updating 'Test Sepia' preset with new parameters.")
updated_sepia_pipeline = [
    {"name": "grayscale", "params": {}, "enabled": True},
    {
        "name": "sepia_tint",
        "params": {"strength": 0.95},
        "enabled": True,
    },  # Changed strength
    {
        "name": "adjust_brightness_contrast",
        "params": {"alpha": 1.1, "beta": 10},
        "enabled": True,
    },
]
presets.add_preset(
    "Test Sepia", updated_sepia_pipeline, file_path=TEST_PRESETS_FILE
)  # Use add_preset to update
loaded_presets = presets.load_presets(file_path=TEST_PRESETS_FILE)
print("Loaded after updating 'Test Sepia':", loaded_presets)
assert loaded_presets["Test Sepia"] == updated_sepia_pipeline, (
    "Test 4 failed: 'Test Sepia' not updated correctly."
)
assert len(loaded_presets) == 2, (
    "Test 4 failed: Number of presets changed after update."
)

# --- Test 5: Remove a preset ---
print("\nTest 5: Removing 'Test Blur' preset.")
presets.remove_preset("Test Blur", file_path=TEST_PRESETS_FILE)
loaded_presets = presets.load_presets(file_path=TEST_PRESETS_FILE)
print("Loaded after removing 'Test Blur':", loaded_presets)
assert "Test Blur" not in loaded_presets and len(loaded_presets) == 1, (
    "Test 5 failed: 'Test Blur' not removed correctly."
)

# --- Test 6: Remove non-existent preset ---
print("\nTest 6: Attempting to remove non-existent preset.")
presets.remove_preset("NonExistentPreset", file_path=TEST_PRESETS_FILE)
loaded_presets = presets.load_presets(file_path=TEST_PRESETS_FILE)
print("Loaded after trying to remove non-existent:", loaded_presets)
assert len(loaded_presets) == 1, "Test 6 failed: Presets should not have changed."

# --- Cleanup: Remove the test file ---
print("\nCleaning up test file...")
os.remove(TEST_PRESETS_FILE)
print(f"Removed {TEST_PRESETS_FILE}.")

print("\nAll presets tests completed successfully!")
