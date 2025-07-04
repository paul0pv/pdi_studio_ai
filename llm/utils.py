# llm/utils.py

from typing import Dict, Any


def get_filtered_metadata(
    style_detected: str, full_metadata: Dict[str, Any]
) -> Dict[str, Any]:
    style_to_filters = {
        "pop_art": ["adjust_saturation", "adjust_brightness_contrast", "invert_colors"],
        "tenebrismo": ["adjust_brightness_contrast", "apply_laplacian_sharpen"],
        "minimalismo": [
            "convert_to_grayscale",
            "apply_gaussian_blur",
            "non_local_means_denoising",
        ],
        "retratos": ["bokeh_effect", "adjust_saturation", "sepia_tint"],
        "nocturno": ["non_local_means_denoising", "adjust_brightness_contrast"],
        "general": list(full_metadata.keys()),
    }
    selected_filters = style_to_filters.get(style_detected, [])
    if not selected_filters:
        selected_filters = list(full_metadata.keys())
    return {f: full_metadata[f] for f in selected_filters if f in full_metadata}
