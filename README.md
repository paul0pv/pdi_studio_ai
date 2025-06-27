# 🎨 PDI Studio AI

Estudio de Procesamiento Digital de Imágenes (PDI) en Tiempo Real con IA

Este es un estudio de procesamiento digital de imágenes en tiempo real, potenciado por un Modelo de Lenguaje Grande (LLM) local. La aplicación permite a los usuarios aplicar una variedad de filtros de imagen a un feed de cámara en vivo o a imágenes cargadas, con la capacidad única de generar pipelines de procesamiento complejas utilizando lenguaje natural.

## ✨ Características Principales

    Procesamiento de Imágenes en Tiempo Real: Aplica filtros a un feed de cámara en vivo, observando los resultados instantáneamente.

    Generación de Pipelines con IA (LLM Local): Describe el efecto de imagen deseado en lenguaje natural, y un LLM local generará una secuencia de filtros (pipeline) para lograrlo.

    Gestión de Pipelines Flexible:

        - Añade y elimina filtros de la pipeline.

        - Modifica los parámetros de los filtros individualmente mediante controles deslizantes e inputs numéricos.

        - Activa o desactiva filtros específicos en la pipeline.

    Previsualización y Análisis:

        - Visualiza el histograma de la imagen procesada para comprender mejor la distribución de píxeles.

        - Guarda capturas de pantalla de la imagen procesada.

    Gestión de Presets:

        - Guarda tus pipelines de filtros favoritas como presets para su uso futuro.

        - Carga y elimina presets existentes.

    Interfaz de Usuario Intuitiva: Desarrollada con PyQt6 para una experiencia de usuario fluida y reactiva.

## 🚀 Cómo Empezar

Sigue estos pasos para configurar y ejecutar PDI Studio AI en tu máquina local.

Requisitos

    - Python 3.8 o superior

    - Pip (gestor de paquetes de Python)

    - Una webcam (opcional, si deseas usar el feed en vivo)

    - Suficiente RAM y/o VRAM para el modelo LLM (al menos 4GB de RAM son recomendables para el Phi-3-mini-4k-instruct-q4.gguf en CPU, más para GPU).

## ⚙️ Instalación

    Clona el repositorio:

```Bash

git clone https://github.com/tu-usuario/pdi_studio_ai.git
cd pdi_studio_ai
``` 

(Asegúrate de reemplazar tu-usuario con tu nombre de usuario de GitHub si lo subes a tu cuenta personal).

Crea y activa un entorno virtual (recomendado):

```Bash
python -m venv venv
# En Windows:
.\venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate
```

Instala las dependencias de Python:

```Bash
pip install -r requirements.txt
```

Si tienes una GPU NVIDIA y quieres usarla para el LLM, instala llama-cpp-python con soporte CUDA:

```Bash
pip uninstall llama-cpp-python # Desinstala la versión solo CPU si ya está instalada
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
```

(Asegúrate de que cu121 coincida con tu versión de CUDA. Consulta la documentación de llama-cpp-python para más detalles si tu versión de CUDA es diferente).

Descarga el modelo LLM:
PDI Studio AI utiliza el modelo Phi-3-mini-4k-instruct-q4.gguf. Debes descargarlo manualmente y colocarlo en la carpeta models/ dentro del directorio raíz del proyecto.

    Descarga el modelo desde Hugging Face:
    microsoft/Phi-3-mini-4k-instruct-gguf - Phi-3-mini-4k-instruct-q4.gguf

    Crea el directorio models si no existe:

```Bash
        mkdir -p models
```

    Coloca el archivo Phi-3-mini-4k-instruct-q4.gguf dentro de la carpeta models.
    La ruta final del modelo debería ser pdi_studio_ai/models/Phi-3-mini-4k-instruct-q4.gguf.

## ▶️ Ejecución

Una vez que hayas instalado todas las dependencias y descargado el modelo LLM, puedes ejecutar la aplicación:

```Bash
python main.py
```
## 📂 Estructura del Proyecto

pdi_studio_ai/
├── main.py                     # Punto de entrada principal de la aplicación.
├── requirements.txt            # Dependencias de Python.
├── .gitignore                  # Archivos y directorios ignorados por Git.
├── models/                     # Directorio para modelos LLM (ej. Phi-3-mini-4k-instruct-q4.gguf).
├── config/
│   └── presets.json            # Archivo JSON para guardar y cargar presets de filtros.
├── video_capture/
│   └── camera_feed.py          # Clase para manejar la captura de video de la cámara.
├── processing/
│   ├── __init__.py
│   ├── filters.py              # Definición de funciones de filtro y sus metadatos.
│   ├── image_processor.py      # Aplica la pipeline de filtros a un frame de imagen.
│   └── image_processing_worker.py # Hilo para procesamiento de imágenes en segundo plano.
└── ui/
    ├── __init__.py
    ├── main_window.py          # La ventana principal de la aplicación PyQt6.
    └── widgets/
        ├── __init__.py
        ├── filter_control.py   # Widget para controlar un filtro individual (parámetros, habilitar/deshabilitar).
        ├── filter_selector.py  # Widget para seleccionar y añadir nuevos filtros a la pipeline.
        ├── histogram_plotter.py # Widget para mostrar el histograma de la imagen procesada.
        └── pipeline_manager.py  # Widget para gestionar la lista de filtros en la pipeline (reordenar, eliminar).

## 🛣️ Futuras Implementaciones

Este proyecto es una base sólida, y hay muchas áreas para expandir y mejorar:

    Más Filtros y Efectos:

        - Implementar una gama más amplia de filtros de OpenCV (ej. Transformada de Hough para detección de líneas/círculos, operaciones morfológicas, segmentación por color, etc.).

        - Añadir filtros avanzados o combinaciones predefinidas.

        - Soporte para máscaras y regiones de interés (ROI) para aplicar filtros solo a partes de la imagen.

    Mejoras en la Interfaz de Usuario (UI):

        - Arrastrar y Soltar (Drag & Drop): Implementar la funcionalidad de arrastrar y soltar para reordenar filtros en el PipelineManager de manera más intuitiva.

        - Vista Previa en Tiempo Real (Thumbnails): Mostrar una pequeña miniatura de la imagen después de cada filtro en la pipeline para depuración visual.

        - Interfaz de Ajuste Fino: Una forma más interactiva de ajustar parámetros, tal vez con feedback visual en tiempo real en un pequeño área de vista previa.

        - Temas Oscuros/Claros: Opciones para personalizar la apariencia de la interfaz.

    Capacidades del LLM:

        - "Undo" y "Redo" de Peticiones LLM: Permitir al usuario iterar y refinar las sugerencias del LLM.

        - Confirmación de Parámetros: Si el LLM sugiere parámetros inusuales, pedir confirmación al usuario o resaltar los valores atípicos.

        - Generación de Descripción de Pipelines: Permitir al LLM generar una descripción en lenguaje natural de una pipeline de filtros existente.

        - Manejo de Errores Semánticos: Mejorar la capacidad del LLM para interpretar peticiones complejas o ambiguas y pedir aclaraciones.

    Carga y Guardado de Imágenes/Videos:

        - Permitir cargar archivos de imagen y video desde el disco para su procesamiento, no solo el feed de la cámara.

        - Funcionalidad para guardar videos procesados.

    Optimización y Rendimiento:

        - Explorar el uso de GPGPU (CUDA/OpenCL) para el procesamiento de imágenes para un rendimiento aún mayor, especialmente con resoluciones altas.

        - Optimización de la comunicación entre hilos para reducir la latencia.

    Funcionalidades Adicionales:

        - Anotaciones: Herramientas para dibujar o añadir texto a la imagen procesada.

        - Calibración de Cámara: Opciones básicas de calibración (brillo, contraste, saturación, etc.) si la cámara lo soporta.

        - Benchmarks: Herramientas para medir el rendimiento de la pipeline y los filtros individuales.

