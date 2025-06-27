# config/presets.py

import json
from typing import List, Dict, Any

# Define the default path for the presets file
PRESETS_FILE = "config/presets.json"


def load_presets(file_path: str = PRESETS_FILE) -> Dict[str, List[Dict[str, Any]]]:
    """
    Loads filter presets from a JSON file.

    Args:
        file_path (str): The path to the JSON file containing the presets.

    Returns:
        Dict[str, List[Dict[str, Any]]]: A dictionary where keys are preset names
                                         and values are lists of filter configurations.
                                         Returns an empty dictionary if the file is not found or is invalid.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            presets_data = json.load(f)
            # Basic validation: ensure it's a dictionary
            if not isinstance(presets_data, dict):
                print(
                    f"Warning: Presets file '{file_path}' does not contain a valid dictionary. Returning empty presets."
                )
                return {}
            return presets_data
    except FileNotFoundError:
        print(f"Presets file '{file_path}' not found. Returning empty presets.")
        return {}
    except json.JSONDecodeError:
        print(
            f"Error decoding JSON from '{file_path}'. Check file format. Returning empty presets."
        )
        return {}
    except Exception as e:
        print(f"An unexpected error occurred while loading presets: {e}")
        return {}


def save_presets(
    presets: Dict[str, List[Dict[str, Any]]], file_path: str = PRESETS_FILE
):
    """
    Saves filter presets to a JSON file.

    Args:
        presets (Dict[str, List[Dict[str, Any]]]): A dictionary of preset names
                                                    and their filter configurations.
        file_path (str): The path to the JSON file where presets will be saved.
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(presets, f, indent=4, ensure_ascii=False)
        print(f"Presets successfully saved to '{file_path}'.")
    except Exception as e:
        print(f"Error saving presets to '{file_path}': {e}")


def add_preset(
    preset_name: str,
    filter_pipeline: List[Dict[str, Any]],
    file_path: str = PRESETS_FILE,
):
    """
    Adds a new preset or updates an existing one.

    Args:
        preset_name (str): The name of the preset to add/update.
        filter_pipeline (List[Dict[str, Any]]): The list of filter configurations for this preset.
        file_path (str): The path to the JSON file.
    """
    presets = load_presets(file_path)
    presets[preset_name] = filter_pipeline
    save_presets(presets, file_path)
    print(f"Preset '{preset_name}' added/updated.")


def remove_preset(preset_name: str, file_path: str = PRESETS_FILE):
    """
    Removes a preset by name.

    Args:
        preset_name (str): The name of the preset to remove.
        file_path (str): The path to the JSON file.
    """
    presets = load_presets(file_path)
    if preset_name in presets:
        del presets[preset_name]
        save_presets(presets, file_path)
        print(f"Preset '{preset_name}' removed.")
    else:
        print(f"Preset '{preset_name}' not found.")
