# processing/filters.py

import cv2
import numpy as np

# --- Filter Functions ---


def convert_to_grayscale(image: np.ndarray) -> np.ndarray:
    """Converts a BGR image to grayscale."""
    if len(image.shape) == 2 or image.shape[2] == 1:
        return image  # Already grayscale
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def invert_colors(image: np.ndarray) -> np.ndarray:
    """Inverts the colors of an image."""
    return cv2.bitwise_not(image)


def apply_gaussian_blur(image: np.ndarray, ksize: int = 5) -> np.ndarray:
    """Applies Gaussian blur to an image. ksize must be odd."""
    ksize = ksize if ksize % 2 == 1 else ksize + 1  # Ensure ksize is odd
    return cv2.GaussianBlur(image, (ksize, ksize), 0)


def apply_median_blur(image: np.ndarray, ksize: int = 5) -> np.ndarray:
    """Applies Median blur to an image. ksize must be odd."""
    ksize = ksize if ksize % 2 == 1 else ksize + 1  # Ensure ksize is odd
    return cv2.medianBlur(image, ksize)


def apply_canny_edge_detection(
    image: np.ndarray, low_threshold: int = 50, high_threshold: int = 150
) -> np.ndarray:
    """Applies Canny edge detection. Image is converted to grayscale internally."""
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.Canny(image, low_threshold, high_threshold)


def adjust_brightness_contrast(
    image: np.ndarray, alpha: float = 1.0, beta: int = 0
) -> np.ndarray:
    """Adjusts brightness (beta) and contrast (alpha) of an image."""
    return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)


def sepia_tint(image: np.ndarray, strength: float = 0.8) -> np.ndarray:
    """
    Applies a sepia tint to the image.
    Ensures image is 3-channel BGR before applying tint.
    """
    # Convert to BGR if grayscale
    if len(image.shape) == 2 or image.shape[2] == 1:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    # Sepia matrix (simplified for demonstration)
    # The sum of each row should ideally be 1 for maintaining brightness
    # These values are often adjusted for desired effect
    sepia_matrix = np.array(
        [
            [0.272, 0.534, 0.131],
            [0.349, 0.686, 0.168],
            [0.393, 0.769, 0.189],
        ]
    ).T  # Transpose for cv2.transform (cols of matrix must match scn)

    # Apply tint gradually based on strength
    identity_matrix = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ]
    ).T

    # Interpolate between identity and sepia matrix based on strength
    final_matrix = (1.0 - strength) * identity_matrix + strength * sepia_matrix

    # Convert image to float32 for matrix multiplication
    image_float = image.astype(np.float32) / 255.0

    # Apply the transformation
    tinted_image = cv2.transform(image_float, final_matrix)

    # Clip values to [0, 1] and convert back to uint8
    tinted_image = np.clip(tinted_image, 0.0, 1.0) * 255.0
    return tinted_image.astype(np.uint8)


def apply_laplacian_sharpen(
    image: np.ndarray, kernel_size: int = 3, scale: float = 1.0
) -> np.ndarray:
    """Sharpens the image using the Laplacian operator."""
    if len(image.shape) == 2 or image.shape[2] == 1:
        # If grayscale, convert to BGR for sharpening and then back to gray if desired,
        # or just sharpen as grayscale. For sharpening, grayscale is fine.
        # However, for consistency in returning color, we ensure 3 channels.
        # For sharpening it is often applied per channel or on grayscale.
        # We will keep it simple and convert to grayscale if input is color for laplacian,
        # as per typical usage, and then potentially convert back to color.
        # For now, let's keep it simple: apply on grayscale.
        gray_image = (
            image if len(image.shape) == 2 else cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        )
        sharpened = cv2.Laplacian(gray_image, cv2.CV_64F, ksize=kernel_size)
        sharpened = gray_image - scale * sharpened
        sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
        return (
            sharpened
            if len(image.shape) == 2
            else cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)
        )

    # If color, apply on each channel or convert to grayscale and then apply
    # Simplest for now: convert to grayscale, sharpen, then convert back to BGR
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sharpened_gray = cv2.Laplacian(gray_image, cv2.CV_64F, ksize=kernel_size)
    sharpened_gray = gray_image - scale * sharpened_gray
    sharpened_gray = np.clip(sharpened_gray, 0, 255).astype(np.uint8)
    return cv2.cvtColor(sharpened_gray, cv2.COLOR_GRAY2BGR)


def adjust_saturation(image: np.ndarray, factor: float = 1.5) -> np.ndarray:
    """
    Adjusts the saturation of an image.
    Ensures image is 3-channel BGR before conversion to HSV.
    """
    # Convert to BGR if grayscale
    if len(image.shape) == 2 or image.shape[2] == 1:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    # Apply factor to saturation, clip to [0, 255]
    s = np.clip(s * factor, 0, 255).astype(np.uint8)

    merged_hsv = cv2.merge([h, s, v])
    return cv2.cvtColor(merged_hsv, cv2.COLOR_HSV2BGR)


# --- New Advanced Filter Functions (Placeholders for Phase 2) ---


def apply_denoising_nlm(
    image: np.ndarray,
    h: float = 10,
    h_color: float = 10,
    template_window_size: int = 7,
    search_window_size: int = 21,
) -> np.ndarray:
    """
    Applies Non-Local Means Denoising to the image.
    h: Parameter regulating filter strength for luminance component.
    h_color: Parameter regulating filter strength for color components.
    template_window_size: Size in pixels of the template patch that is used to compute weights. Should be odd.
    search_window_size: Size in pixels of the window that is used to compute weighted average for given pixel. Should be odd.
    """
    # Convert to 8-bit if not already (required by fastNlMeansDenoising/Colored)
    if image.dtype != np.uint8:
        image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)

    if len(image.shape) == 3:  # Color image
        return cv2.fastNlMeansDenoisingColored(
            image, None, h, h_color, template_window_size, search_window_size
        )
    else:  # Grayscale image
        return cv2.fastNlMeansDenoising(
            image, None, h, template_window_size, search_window_size
        )


def apply_object_detection_placeholder(image: np.ndarray) -> np.ndarray:
    """
    Placeholder for basic object detection. Returns the original image with a simple annotation.
    Real implementation would use more advanced CV techniques or ML models.
    """
    # This is a very basic placeholder. For actual object detection,
    # you'd integrate models (e.g., YOLO, Haar cascades) or more complex CV.
    output_image = image.copy()
    if len(output_image.shape) == 2:  # Ensure it's 3-channel for drawing
        output_image = cv2.cvtColor(output_image, cv2.COLOR_GRAY2BGR)

    # Example: Draw a placeholder rectangle
    h, w = output_image.shape[:2]
    cv2.rectangle(
        output_image, (w // 4, h // 4), (w * 3 // 4, h * 3 // 4), (0, 255, 0), 2
    )
    cv2.putText(
        output_image,
        "Objeto Detectado (Placeholder)",
        (w // 4 + 10, h // 4 + 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2,
    )
    return output_image


def apply_bokeh_effect(
    image: np.ndarray,
    blur_strength: int = 15,
    center_x: float = 0.5,
    center_y: float = 0.5,
    radius: float = 0.2,
) -> np.ndarray:
    """
    Applies a simple circular bokeh (depth of field) effect.
    blur_strength: Kernel size for blur (odd integer).
    center_x, center_y: Normalized coordinates (0.0-1.0) for the center of the focused area.
    radius: Normalized radius (0.0-1.0) of the focused area.
    """
    if blur_strength % 2 == 0:
        blur_strength += 1  # Ensure odd kernel size

    output_image = image.copy()
    h, w = output_image.shape[:2]

    # Create a mask for the focused area (e.g., a circle)
    mask = np.zeros((h, w), dtype=np.uint8)
    center_pixel_x = int(w * center_x)
    center_pixel_y = int(h * center_y)
    pixel_radius = int(min(h, w) * radius)

    cv2.circle(
        mask, (center_pixel_x, center_pixel_y), pixel_radius, 255, -1
    )  # Draw filled circle

    # Blur the entire image
    blurred_image = cv2.GaussianBlur(output_image, (blur_strength, blur_strength), 0)

    # Combine original (focused) and blurred areas using the mask
    # The mask needs to be 3 channels if the image is color
    if len(output_image.shape) == 3:
        mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

    # Blend the focused area (from original) and blurred area (from blurred_image)
    result = np.where(mask == 255, output_image, blurred_image)

    return result


# --- Filter Metadata ---
FILTER_METADATA = {
    "convert_to_grayscale": {
        "function": convert_to_grayscale,
        "description": "Converts the image to grayscale, removing all color information.",
        "params": {},
    },
    "invert_colors": {
        "function": invert_colors,
        "description": "Inverts the colors of the image, creating a negative effect.",
        "params": {},
    },
    "apply_gaussian_blur": {
        "function": apply_gaussian_blur,
        "description": "Applies a Gaussian blur to soften the image and reduce noise. 'ksize' controls the blur strength (must be odd).",
        "params": {
            "ksize": {
                "type": "int_slider",
                "range": (1, 99, 2),  # Odd numbers only
                "default": 5,
                "label": "Kernel Size (Odd)",
            }
        },
    },
    "apply_median_blur": {
        "function": apply_median_blur,
        "description": "Applies a Median blur, effective for removing salt-and-pepper noise. 'ksize' controls the blur strength (must be odd).",
        "params": {
            "ksize": {
                "type": "int_slider",
                "range": (1, 99, 2),  # Odd numbers only
                "default": 5,
                "label": "Kernel Size (Odd)",
            }
        },
    },
    "apply_canny_edge_detection": {
        "function": apply_canny_edge_detection,
        "description": "Detects edges in the image using the Canny algorithm. 'low_threshold' and 'high_threshold' define the sensitivity.",
        "params": {
            "low_threshold": {
                "type": "int_slider",
                "range": (0, 255, 1),
                "default": 50,
                "label": "Low Threshold",
            },
            "high_threshold": {
                "type": "int_slider",
                "range": (0, 255, 1),
                "default": 150,
                "label": "High Threshold",
            },
        },
    },
    "adjust_brightness_contrast": {
        "function": adjust_brightness_contrast,
        "description": "Adjusts the brightness and contrast. 'alpha' (contrast) and 'beta' (brightness).",
        "params": {
            "alpha": {
                "type": "float_slider",
                "range": (0.0, 3.0, 0.01),
                "default": 1.0,
                "label": "Contrast (Alpha)",
            },
            "beta": {
                "type": "int_slider",
                "range": (-100, 100, 1),
                "default": 0,
                "label": "Brightness (Beta)",
            },
        },
    },
    "sepia_tint": {
        "function": sepia_tint,
        "description": "Applies a warm, reddish-brown sepia tone to the image. 'strength' controls the intensity of the effect.",
        "params": {
            "strength": {
                "type": "float_slider",
                "range": (0.0, 1.0, 0.01),
                "default": 0.8,
                "label": "Strength",
            }
        },
    },
    "apply_laplacian_sharpen": {
        "function": apply_laplacian_sharpen,
        "description": "Sharpens the image using the Laplacian operator, enhancing details and edges. 'kernel_size' (odd) and 'scale' control the effect.",
        "params": {
            "kernel_size": {
                "type": "int_slider",
                "range": (1, 15, 2),
                "default": 3,
                "label": "Kernel Size (Odd)",
            },
            "scale": {
                "type": "float_slider",
                "range": (0.0, 5.0, 0.01),
                "default": 1.0,
                "label": "Sharpening Scale",
            },
        },
    },
    "adjust_saturation": {
        "function": adjust_saturation,
        "description": "Adjusts the color saturation of the image. Factor > 1.0 increases, < 1.0 decreases. 0.0 for grayscale.",
        "params": {
            "factor": {
                "type": "float_slider",
                "range": (0.0, 3.0, 0.01),
                "default": 1.5,
                "label": "Factor",
            }
        },
    },
    "non_local_means_denoising": {
        "function": apply_denoising_nlm,
        "description": "Aplica la reducción de ruido Non-Local Means.",
        "params": {
            "h": {
                "type": "float_slider",
                "range": (0.0, 50.0, 0.1),
                "default": 10.0,
                "label": "Intensidad Luminancia (h)",
            },
            "h_color": {
                "type": "float_slider",
                "range": (0.0, 50.0, 0.1),
                "default": 10.0,
                "label": "Intensidad Color (h_color)",
            },
            "template_window_size": {
                "type": "int_slider",
                "range": (1, 15, 2),  # Must be odd
                "default": 7,
                "label": "Tamaño Ventana Plantilla",
            },
            "search_window_size": {
                "type": "int_slider",
                "range": (1, 31, 2),  # Must be odd
                "default": 21,
                "label": "Tamaño Ventana Búsqueda",
            },
        },
    },
    "object_detection_placeholder": {
        "function": apply_object_detection_placeholder,
        "description": "Un filtro de demostración para la detección de objetos.",
        "params": {},  # No adjustable parameters for this placeholder
    },
    "bokeh_effect": {
        "function": apply_bokeh_effect,
        "description": "Aplica un efecto de desenfoque de profundidad (bokeh) circular.",
        "params": {
            "blur_strength": {
                "type": "int_slider",
                "range": (1, 49, 2),  # Must be odd
                "default": 15,
                "label": "Intensidad de Desenfoque",
            },
            "center_x": {
                "type": "float_slider",
                "range": (0.0, 1.0, 0.01),
                "default": 0.5,
                "label": "Centro X (0-1)",
            },
            "center_y": {
                "type": "float_slider",
                "range": (0.0, 1.0, 0.01),
                "default": 0.5,
                "label": "Centro Y (0-1)",
            },
            "radius": {
                "type": "float_slider",
                "range": (0.01, 0.5, 0.01),
                "default": 0.2,
                "label": "Radio (0-1)",
            },
        },
    },
}

# You can also make a list of available filter names for convenience
AVAILABLE_FILTERS = list(FILTER_METADATA.keys())


# --- Function to get a filter function by name ---
def get_filter_function(filter_name: str):
    """Returns the filter function associated with a given name."""
    return FILTER_METADATA.get(filter_name, {}).get("function")


# --- Function to get default parameters for a filter ---
def get_default_filter_params(filter_name: str) -> dict:
    """Returns the default parameters for a given filter name."""
    params = {}
    metadata_params = FILTER_METADATA.get(filter_name, {}).get("params", {})
    for param_name, param_info in metadata_params.items():
        params[param_name] = param_info.get("default")
    return params
