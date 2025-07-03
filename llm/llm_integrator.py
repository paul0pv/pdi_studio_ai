# pdi_studio_ai/llm/llm_integrator.py

import json
from typing import List, Dict, Any, Optional
from llama_cpp import Llama
import os

# Asegúrate de que FILTER_METADATA esté disponible aquí si no lo está.
# Si FILTER_METADATA está definido en processing/filters.py, asegúrate de importarlo.
# from processing.filters import FILTER_METADATA # <--- Si lo necesitas directamente aquí

# IMPORTAR EL NUEVO MÓDULO DE REGLAS
from processing.predefined_pipelines import get_pipeline_from_rules

LLM_MODEL_PATH = "models/Phi-3-mini-4k-instruct-q4.gguf"


class LLMIntegrator:
    def __init__(self, model_path: str = LLM_MODEL_PATH):
        self.model_path = model_path
        self.llm: Optional[Llama] = None
        if not os.path.isfile(self.model_path):
            print(
                f"LLMIntegrator Error: Modelo no encontrado en {self.model_path}. Por favor, descarga el archivo GGUF."
            )
            return

        try:
            print(f"LLMIntegrator: Cargando LLM desde {self.model_path}...")
            self.llm = Llama(
                model_path=self.model_path,
                n_gpu_layers=-1,  # Ajusta según tu GPU (-1 para todas, 0 para CPU)
                n_ctx=4096,  # Tamaño del contexto (ajusta si el prompt se vuelve muy largo)
                n_threads=os.cpu_count()
                or 4,  # Usa el número de núcleos de CPU disponibles
                verbose=False,
            )
            print("LLMIntegrator: LLM cargado exitosamente.")
        except Exception as e:
            print(f"LLMIntegrator Error al cargar LLM: {e}")
            self.llm = None  # Asegúrate de que sea None si hay un error

    def generate_filter_pipeline(
        self, user_query: str, available_filters_metadata: Dict[str, Any]
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Generates an image processing pipeline based on user natural language input
        and a dictionary of available filter metadata.
        """
        if self.llm is None:
            print("LLMIntegrator: LLM no cargado. No se puede generar la pipeline.")
            return None

        # --- INICIO DE LA LÓGICA HÍBRIDA: 1. Intentar el matching basado en reglas primero ---
        rule_based_pipeline = get_pipeline_from_rules(user_query)
        if rule_based_pipeline:
            print(
                f"LLMIntegrator: Pipeline generada por reglas para '{user_query}': {rule_based_pipeline}"
            )
            return rule_based_pipeline
        # --- FIN DE LA LÓGICA HÍBRIDA ---

        # Si no hay una regla que coincida, se procede con la llamada al LLM
        # 1. Construir la información de los filtros disponibles (lógica existente)
        filters_info = []
        for name, metadata in available_filters_metadata.items():
            filter_description = metadata.get(
                "description", "No description available."
            )
            params_info = []
            for param_name, param_data in metadata.get("params", {}).items():
                param_type = param_data.get("type", "unknown")
                param_label = param_data.get("label", param_name)
                param_default = param_data.get("default", "N/A")
                param_range = param_data.get("range", "N/A")

                params_info.append(
                    f"- Parámetro: '{param_name}' ({param_label}), Tipo: {param_type}, Predeterminado: {param_default}, Rango: {param_range}"
                )
            params_str = (
                "\n  ".join(params_info)
                if params_info
                else "  No tiene parámetros configurables."
            )
            filters_info.append(
                f"  - Nombre: '{name}'\n  Descripción: {filter_description}\n  Parámetros:\n  {params_str}"
            )
        available_filters_str = "\n".join(filters_info)

        # 2. Definir el prompt del sistema (prompt de la "Nueva estrategia" ya probada)
        system_prompt = f"""Eres un extractor de información de filtros de imagen.
Tu **ÚNICA FUNCIÓN** es identificar los filtros de imagen y sus parámetros
a partir de una petición de usuario, y formatear esta información en un
objeto JSON.

**REGLAS ESTRICTAS DE SALIDA:**
1.  La salida **DEBE ser un objeto JSON a nivel raíz**.
2.  Este objeto DEBE contener una clave llamada `"filters_identified"`.
3.  El valor de `"filters_identified"` DEBE ser un **array JSON**.
4.  Cada objeto dentro de este array DEBE representar un filtro identificado.
5.  Cada objeto de filtro DEBE tener la clave `"name"` con el nombre **EXACTO** del filtro de la lista proporcionada.
6.  Si se mencionan parámetros para un filtro, DEBEN incluirse como **claves adicionales** dentro del objeto de ese filtro (no anidados bajo una clave "params" todavía).
7.  **SOLO** incluye filtros que estén en la lista `Filtros Disponibles`. Ignora cualquier solicitud de filtro no listado.
8.  **SOLO** incluye parámetros que estén definidos para ese filtro en la lista `Filtros Disponibles`.
9.  **NO incluyas texto adicional, explicaciones, preámbulos o comentarios fuera del JSON.**

**Filtros Disponibles y sus detalles (¡SOLO PUEDES USAR ESTOS!):**
{available_filters_str}

**EJEMPLOS DEL FORMATO DE SALIDA REQUERIDO (¡ADHIÉRETE A ESTE FORMATO!):**
(Si el usuario dice "aplicar tono sepia y un poco de ruido")
```json
{{
  "filters_identified": [
    {{ "name": "apply_sepia_tone" }},
    {{ "name": "add_noise", "intensity": 0.05 }}
  ]
}}
(Si el usuario dice "blanco y negro y desenfoque gaussiano con ksize 9")
{{
  "filters_identified": [
    {{ "name": "convert_to_grayscale" }},
    {{ "name": "apply_gaussian_blur", "ksize": 9 }}
  ]
}}
"""
        # 3. Preparar el mensaje del usuario
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query},
        ]

        print("LLMIntegrator: Enviando prompt al LLM (Nueva estrategia/Fallback)...")

        raw_json_str = ""
        try:
            response = self.llm.create_chat_completion(
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.01,
                max_tokens=4096,
            )
            raw_json_str = response["choices"][0]["message"]["content"].strip()
            print(f"LLMIntegrator: Respuesta cruda del LLM:\n{raw_json_str}")

            # 4. Post-procesamiento y construcción de la pipeline (más robusto)
            # Eliminar bloques de código markdown si el LLM los incluye
            if raw_json_str.startswith("```json") and raw_json_str.endswith("```"):
                raw_json_str = raw_json_str[7:-3].strip()
            elif raw_json_str.startswith("```") and raw_json_str.endswith("```"):
                raw_json_str = raw_json_str[3:-3].strip()

            parsed_data = json.loads(raw_json_str)

            # Esperamos un objeto con la clave "filters_identified" que contiene un array
            identified_filters_list = parsed_data.get("filters_identified")

            if not isinstance(identified_filters_list, list):
                print(
                    f"LLMIntegrator Error: La respuesta del LLM no contiene un array válido en 'filters_identified'. Cruda: {raw_json_str}"
                )
                return None

            pipeline = []
            for filter_entry_llm in identified_filters_list:
                if not isinstance(filter_entry_llm, dict):
                    print(
                        f"LLMIntegrator Warning: Entrada de filtro inválida (no es diccionario): {filter_entry_llm}. Ignorando."
                    )
                    continue

                filter_name = filter_entry_llm.get("name")
                if not filter_name or not isinstance(filter_name, str):
                    print(
                        f"LLMIntegrator Warning: Entrada de filtro sin nombre válido: {filter_entry_llm}. Ignorando."
                    )
                    continue

                if filter_name not in available_filters_metadata:
                    print(
                        f"LLMIntegrator Warning: El filtro '{filter_name}' generado por el LLM no existe en la lista de filtros disponibles. Ignorando."
                    )
                    continue

                # Extraer parámetros: Todas las demás claves en el objeto del filtro LLM
                params = {}
                filter_metadata = available_filters_metadata.get(filter_name, {})
                defined_params = filter_metadata.get("params", {})

                for key, value in filter_entry_llm.items():
                    if (
                        key != "name" and key in defined_params
                    ):  # Solo toma parámetros conocidos
                        # Intentar convertir el valor al tipo correcto si es posible
                        expected_type = defined_params[key].get("type")
                        try:
                            # Asumiendo que 'int_slider' y 'float_slider' esperan int/float
                            if expected_type == "int_slider" and isinstance(
                                value, (int, float)
                            ):
                                params[key] = int(value)
                            elif expected_type == "float_slider" and isinstance(
                                value, (int, float)
                            ):
                                params[key] = float(value)
                            else:  # Para otros tipos o si la conversión no es necesaria/falla
                                params[key] = value
                        except (ValueError, TypeError):
                            print(
                                f"LLMIntegrator Warning: No se pudo convertir el parámetro '{key}' con valor '{value}' al tipo esperado '{expected_type}'. Usando valor original."
                            )
                            params[key] = value

                pipeline.append({"name": filter_name, "params": params})

            if not pipeline:
                print(
                    "LLMIntegrator: El LLM no identificó filtros válidos para la petición."
                )
                return None

            print(f"LLMIntegrator: Pipeline generada exitosamente: {pipeline}")
            return pipeline

        except json.JSONDecodeError as e:
            print(
                f"LLMIntegrator Error: Fallo al decodificar JSON de la respuesta del LLM. Error: {e}\nRespuesta LLM cruda:\n{raw_json_str}"
            )
            return None
        except Exception as e:
            print(
                f"LLMIntegrator Error: Ocurrió un error inesperado durante la inferencia o el parseo del LLM: {e}"
            )
            return None
