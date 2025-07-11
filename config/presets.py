# config/presets.py

import os
import json
from typing import List, Dict, Any, Optional
from PyQt6.QtWidgets import QFileDialog

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


def rename_preset(old_name: str, new_name: str, file_path: str = PRESETS_FILE):
    """
    Renames an existing preset.

    Args:
        old_name (str): The current name of the preset.
        new_name (str): The new name to assign.
        file_path (str): The path to the JSON file.
    """
    presets = load_presets(file_path)

    if old_name not in presets:
        print(f"Preset '{old_name}' not found. Cannot rename.")
        return

    if new_name in presets:
        print(f"Preset '{new_name}' already exists. Overwriting.")

    presets[new_name] = presets.pop(old_name)
    save_presets(presets, file_path)
    print(f"Preset renamed from '{old_name}' to '{new_name}'.")


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


def export_preset_to_json(
    preset_name: str, file_path: str = PRESETS_FILE, export_path: str = None
):
    """
    Exporta un preset individual a un archivo JSON separado.

    Args:
        preset_name (str): Nombre del preset a exportar.
        file_path (str): Ruta del archivo de presets principal.
        export_path (str): Ruta del archivo de salida. Si no se especifica, se usa '<preset_name>.json'.
    """
    presets = load_presets(file_path)
    if preset_name not in presets:
        print(f"Preset '{preset_name}' no encontrado.")
        return

    export_path = export_path or f"{preset_name}.json"
    try:
        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(presets[preset_name], f, indent=4, ensure_ascii=False)
        print(f"Preset '{preset_name}' exportado a '{export_path}'.")
    except Exception as e:
        print(f"Error al exportar preset: {e}")


def import_preset_from_json(
    file_path: Optional[str] = None, target_path: str = PRESETS_FILE
) -> Optional[str]:
    """
    Importa un preset desde un archivo JSON externo y lo añade al archivo de presets principal.

    Args:
        file_path (str, optional): Ruta del archivo JSON a importar. Si no se proporciona, se abre un diálogo.
        target_path (str): Ruta del archivo de presets principal.

    Returns:
        str | None: Nombre del preset importado si fue exitoso, None en caso contrario.
    """
    if not file_path:
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Seleccionar archivo de preset",
            "",
            "Archivos JSON (*.json);;Todos los archivos (*)",
        )
        if not file_path:
            print("Importación cancelada por el usuario.")
            return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            preset_data = json.load(f)
        if not isinstance(preset_data, list):
            print(
                "⚠️ El archivo no contiene una pipeline válida (se esperaba una lista)."
            )
            return None

        preset_name = os.path.splitext(os.path.basename(file_path))[0]
        presets = load_presets(target_path)
        presets[preset_name] = preset_data
        save_presets(presets, target_path)
        print(f"✅ Preset '{preset_name}' importado desde '{file_path}'.")
        return preset_name

    except Exception as e:
        print(f"❌ Error al importar preset: {e}")
        return None
