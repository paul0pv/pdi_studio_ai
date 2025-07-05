# 🎨 **PDI Studio AI**

**_Plataforma modular de procesamiento digital de imágenes en tiempo real, asistida por IA generativa local._**

## 🧠 Visión General
PDI Studio AI es una plataforma interactiva para aplicar, diseñar y automatizar pipelines de procesamiento digital de imágenes (PDI) en tiempo real. Integra un modelo de lenguaje local (LLM) para generar secuencias de filtros a partir de descripciones en lenguaje natural, y permite al usuario ajustar cada etapa visualmente. Su arquitectura modular permite extenderlo fácilmente a sistemas embebidos, robótica o aplicaciones industriales.

---

## ✨ Características Principales

### Procesamiento de Imágenes en Tiempo Real
- Aplica filtros secuenciales a un feed de cámara en vivo o imágenes cargadas.
- Visualiza los resultados instantáneamente con histogramas y controles dinámicos.

### Generación de Pipelines con LLM Local
- Describe el estilo o efecto deseado en lenguaje natural.
- El modelo Phi-3-mini genera automáticamente una secuencia de filtros.
- Incluye fallback inteligente por estilo o reglas predefinidas si el modelo falla.
    - Por estilo detectado (ej. “minimalismo”)
    - Por coincidencia exacta con reglas predefinidas

### Gestión Visual de Pipelines
- Añade, elimina, reordena y ajusta filtros desde una interfaz gráfica.
- Controla parámetros con sliders validados (rango, imparidad, tipo).
- Activa o desactiva filtros individualmente.

### Validación y Robustez
- Todos los parámetros son validados automáticamente según su metadata.
- Se evita el uso de valores inválidos (por ejemplo, kernels pares).
- El sistema detecta y corrige errores silenciosos en tiempo real.

### Asistencia Visual y Análisis
- Visualización de histograma de la imagen procesada.
- Captura de pantalla del resultado.
- Indicadores visuales si se usó fallback o si un filtro falló.

### Presets y Reglas
- Guarda pipelines como presets reutilizables.
- Incluye reglas predefinidas para estilos comunes ("blanco y negro", "efecto cómic", etc.).

---

## 🧩 Arquitectura General

```Mermaid
flowchart TD
    A[Usuario] -->|Prompt o UI| B[MainWindow]
    B --> C[PipelineManager]
    B --> D[ImageProcessor]
    B --> E[LLMWorker]
    C --> D
    E --> C
    D --> F[ImageProcessingWorker]
    F --> G[Feed de Cámara / Imagen]
    G --> D
```

- El usuario puede construir pipelines manualmente o describirlos en lenguaje natural.

- El modelo LLM genera filtros que se validan y aplican en tiempo real.

- El procesamiento se ejecuta en hilos separados para mantener la UI fluida.

---

## 🎛️ Filtros Disponibles

| Filtro	| Descripción | Parámetros |
|-----------|-------------|------------|
|convert_to_grayscale | Escala de grises | — |
|invert_colors	| Negativo de imagen	| — |
|apply_gaussian_blur	| Suavizado gaussiano	| ksize (impar) |
|apply_median_blur	| Filtro de mediana	| ksize (impar) |
|apply_canny_edge_detection	| Detección de bordes	| low_threshold, high_threshold |
|adjust_brightness_contrast	| Brillo y contraste	| alpha, beta |
|sepia_tint	| Tono sepia	| strength |
|apply_laplacian_sharpen	| Realce de bordes	| alpha |
|adjust_saturation	| Saturación HSV	| saturation_factor|
|non_local_means_denoising	| Reducción de ruido	| h, h_color, template_window_size, search_window_size|
|bokeh_effect	| Desenfoque radial	| ksize, center_x, center_y, radius |

## 🚀 Cómo Empezar

### Requisitos

- Python 3.8 o superior
- Una webcam (opcional)
- Al menos 4 GB de RAM (recomendado para LLM en CPU)
- GPU NVIDIA (opcional, para acelerar el modelo LLM)

---

## ⚙️ Instalación

```bash
git clone https://github.com/paul0pv/pdi_studio_ai.git
cd pdi_studio_ai
python -m venv venv

# MacOS/Linux:
source venv/bin/activate  
# Windows: 
.\venv\Scripts\activate en Windows

pip install -r requirements.txt
```

### Soporte para GPU (opcional)

```bash
pip uninstall llama-cpp-python
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
```

### Descargar el modelo LLM

  - Modelo: Phi-3-mini-4k-instruct-q4.gguf

  - Fuente: Hugging Face → microsoft/Phi-3-mini-4k-instruct-gguf

```bash
mkdir -p models
```
#### Coloca el archivo .gguf dentro de models/

## ▶️ Ejecución

```bash
python main.py
```

## 📂 Estructura del Proyecto

```bash
pdi_studio_ai/
├── config/                                # Presets y configuraciones
│   ├──  __init__.py  
│   ├── preset_meta.py  
│   └── presets.py  
├── llm/  
│   ├── client.py  
│   ├── __init__.py  
│   ├── llm_worker.py                       # Hilo para ejecución del modelo
│   ├── parser.py  
│   ├── pipeline_generator.py               # Generación de pipelines con fallback
│   ├── prompt_builder.py  
│   └── utils.py  
├── models/                                 # Modelos LLM (.gguf)
├── processing/  
│   ├── filters.py                          # Filtros y metadatos
│   ├── image_processing_worker.py          # Hilo para procesamiento de imágenes en segundo plano.
│   ├── image_processor.py                  # Aplicación de pipelines
│   ├── __init__.py  
│   ├── predefined_pipelines.py             # Reglas por texto
│   ├── semantic_classifier.py              
│   ├── utils.py  
│   └── validation.py                       # Validación de parámetros
├── resources/  
│   ├── icons/  
│   └── loading_spinner.gif  
├── styles/  
│   └── dark_theme.qss  
├── tests/  
│   ├── conf_test.py  
│   ├──test_camera_feed.py  
│   ├── test_filters2.py  
│   ├── test_filters.py  
│   ├── test_full_pipeline.py  
│   ├── test_histogram_plotter.py  
│   ├── test_image_processor.py  
│   ├── test_llm_integrator.py  
│   ├── test_pipeline_generator.py  
│   ├── test_presets.py  
│   ├── test_prompt_builder.py  
│   └── test_semantic_classifier.py  
├── ui/  
│   ├── widgets/  
│   │   ├── favorites_tab.py  
│   │   ├── filter_control.py           # Widget para controlar un filtro individual (parámetros, habilitar/deshabilitar).
│   │   ├── filter_selector.py          # Widget para seleccionar y añadir nuevos filtros a la pipeline.
│   │   ├── histogram_plotter.py        # Widget para mostrar el histograma de la imagen procesada.
│   │   ├── __init__.py  
│   │   ├── pipeline_manager.py         # Widget para gestionar la lista de filtros en la pipeline (reordenar, eliminar).
│   │   ├── preset_selector.py  
│   │   ├── preview_window.py  
│   │   └── style_input_preview.py  
│   ├── __init__.py  
│   ├── main_window.py                  # La ventana principal de la aplicación PyQt6.
│   └── main_window.py.bak  
├── video_capture/  
│   ├── camera_feed.py                  # Clase para manejar la captura de video de la cámara.
│   ├── camera_utils.py  
│   └── __init__.py  
├── demo_ai_pipeline.py                 # Script para testear el comportamiento de un modelo
├── filter_control.txt  
├── filter.txt  
├── main.py                             # Punto de entrada principal de la aplicación.
├── README.md  
└── requirements.txt                    # Dependencias de Python.
```

## 🛠️ Funcionalidades Avanzadas

### Procesamiento en hilos separados (imagen y LLM)
| Hilo	| Función |
|-------|---------|
| ImageProcessingWorker	| Aplica filtros a cada frame |
| LLMWorker | Ejecuta el modelo de lenguaje y genera pipelines |
| UI Principal	| Control de interfaz y eventos |

- Fallback automático si el modelo falla

- Test de filtros con validación automática

- Selector de cámara dinámico

- Editor visual de parámetros con validación en tiempo real

## 🛣️ Futuras Implementaciones

### Nuevos Filtros

  - Transformadas de Hough, operaciones morfológicas, segmentación por color

  - Filtros en el dominio de la frecuencia (FFT, DCT)

### Mejora del LLM

- Confirmación de parámetros atípicos

- Descripción automática de pipelines

- Historial de prompts y respuestas

### UI Avanzada

- Miniaturas por filtro

- Drag & Drop para reordenar

- Vista previa por etapa

### Despliegue en Robots/Drones

- Compatible con Raspberry Pi, Jetson Nano, Coral TPU

- Pipelines predefinidos o generados remotamente

- Comunicación por MQTT/WebSocket para actualización dinámica

- Ideal para navegación visual, inspección o agricultura de precisión

## 🧠 Aplicaciones Prácticas

| Sector | Aplicación |
---------|------------|
| Audiovisual | Estilización y corrección visual automatizada |
| Robótica | Preprocesamiento visual para navegación o inspección |
| Educación | Enseñanza interactiva de PDI |
| Gobierno | Restauración de imágenes históricas, vigilancia |
| Industria | Inspección visual, detección de defectos |

## 📜 Licencia

Este proyecto está licenciado bajo MIT. Puedes usarlo, modificarlo y distribuirlo libremente.

