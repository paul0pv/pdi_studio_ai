# llm_integrator.py
import json
from typing import List, Dict, Any, Optional
from llama_cpp import Llama
import os

# Asegúrate de que FILTER_METADATA esté disponible aquí si no lo está.
# Si FILTER_METADATA está definido en processing/filters.py, asegúrate de importarlo.
# from processing.filters import FILTER_METADATA # <--- Asegúrate de tener esta importación
# La importación real de FILTER_METADATA se hace en main_window.py y se pasa.

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
            # --- Configuración para rendimiento del LLM ---
            # n_gpu_layers: Número de capas que se descargarán a la GPU.
            #   - Si tienes GPU NVIDIA con VRAM suficiente, prueba -1 para todas las capas.
            #     Asegúrate de haber instalado llama-cpp-python con soporte CUDA (ej: pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121).
            #   - Si no tienes GPU o tienes problemas, déjalo en 0 para usar solo CPU.
            # n_ctx: Tamaño de la ventana de contexto (máximo de tokens para prompt + respuesta).
            # n_threads: Número de hilos de CPU a usar. Se recomienda usar el número de núcleos de CPU.
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

        # 1. Construir la información de los filtros disponibles
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

        # 2. Definir el prompt del sistema con instrucciones detalladas
        system_prompt = f"""Eres un asistente avanzado para la generación de pipelines de procesamiento de imágenes. Tu objetivo es transformar peticiones de lenguaje natural en una secuencia estructurada de filtros de imagen en formato JSON.

**Instrucciones clave:**
-   Debes elegir filtros únicamente de la lista proporcionada.
-   Cada filtro debe ser un objeto JSON con las claves "name" (nombre del filtro) y "params" (un diccionario de sus parámetros).
-   Si un filtro tiene parámetros, DEBES incluirlos en el diccionario "params" con sus valores. Si un parámetro tiene un valor predeterminado y no se especifica explícitamente en la petición del usuario, puedes usar el predeterminado.
-   Si un filtro no requiere parámetros (su diccionario "params" en los metadatos está vacío), su diccionario "params" en la salida JSON debe ser un diccionario vacío: `{{}}`.
-   La salida final debe ser una lista de objetos JSON, donde cada objeto representa un filtro en la secuencia de la pipeline.
-   Asegúrate de que el JSON sea válido y esté bien formado.
-   No incluyas texto adicional fuera del JSON.

**Filtros Disponibles y sus detalles:**
{available_filters_str}

**Ejemplo de formato de salida JSON:**
```json
[
  {{
    "name": "convert_to_grayscale",
    "params": {{}}
  }},
  {{
    "name": "apply_gaussian_blur",
    "params": {{
      "ksize": 7
    }}
  }},
  {{
    "name": "adjust_brightness_contrast",
    "params": {{
      "alpha": 1.2,
      "beta": 10
    }}
  }}
]

"""

        # 3. Preparar el mensaje del usuario
        user_query_with_context = (
            f'Genera una pipeline de procesamiento de imágenes para: "{user_query}"'
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query_with_context},
        ]

        print("LLMIntegrator: Enviando prompt al LLM...")
        # print(f"--- SYSTEM PROMPT ---\n{system_prompt}\n--- USER QUERY ---\n{user_query_with_context}") # Para depuración

        raw_json_str = ""
        try:
            response = self.llm.create_chat_completion(
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=500,
            )
            raw_json_str = response["choices"][0]["message"]["content"].strip()
            print(f"LLMIntegrator: Respuesta cruda del LLM:\n{raw_json_str}")

            # 4. Post-procesamiento y validación de la respuesta
            # Limpieza básica: A veces el LLM puede incluir bloques de código markdown
            if raw_json_str.startswith("```json") and raw_json_str.endswith("```"):
                raw_json_str = raw_json_str[7:-3].strip()
            elif raw_json_str.startswith("```") and raw_json_str.endswith("```"):
                raw_json_str = raw_json_str[3:-3].strip()

            # Esto ya lo tenías, asegura que corrige 'namee'
            raw_json_str = raw_json_str.replace('"namee":', '"name":')
            raw_json_str = raw_json_str.replace(
                "'namee':", "'name':"
            )  # Por si usa comillas simples

            pipeline = json.loads(raw_json_str)
            if not isinstance(pipeline, list):
                print(
                    f"LLMIntegrator Error: La respuesta del LLM no es un array JSON. Cruda: {raw_json_str}"
                )
                return None

            # Validación más robusta de la estructura de la pipeline generada
            validated_pipeline = []
            for entry in pipeline:
                if not isinstance(entry, dict):
                    print(
                        f"LLMIntegrator Error: Entrada de filtro inválida (no es un diccionario): {entry}. Cruda: {raw_json_str}"
                    )
                    return None

                filter_name = entry.get("name")
                params = entry.get("params")

                if not filter_name or not isinstance(filter_name, str):
                    print(
                        f"LLMIntegrator Error: Entrada de filtro inválida (falta 'name' o no es string): {entry}. Cruda: {raw_json_str}"
                    )
                    return None

                if not isinstance(params, dict):
                    print(
                        f"LLMIntegrator Error: Entrada de filtro inválida (falta 'params' o no es diccionario): {entry}. Cruda: {raw_json_str}"
                    )
                    return None

                # Validación de si el nombre del filtro existe en los metadatos disponibles
                if filter_name not in available_filters_metadata:
                    print(
                        f"LLMIntegrator Warning: El filtro '{filter_name}' generado por el LLM no está en la lista de filtros disponibles. Ignorando."
                    )
                    continue  # Ignorar filtros no existentes

                validated_pipeline.append(entry)

            print(
                f"LLMIntegrator: Pipeline generada exitosamente: {validated_pipeline}"
            )
            return validated_pipeline

        except json.JSONDecodeError as e:
            print(
                f"LLMIntegrator Error: Fallo al decodificar JSON de la respuesta del LLM. Error: {e}\nRespuesta LLM cruda:\n{raw_json_str}"
            )
            return None
        except Exception as e:
            print(
                f"LLMIntegrator Error: Ocurrió un error inesperado durante la inferencia del LLM: {e}"
            )
            return None
