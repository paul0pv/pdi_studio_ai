# ui/main_window.py

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QSpacerItem,
    QSizePolicy,
    QComboBox,
    QMessageBox,
    QGroupBox,
    QStatusBar,  # Import QStatusBar
    QFileDialog,  # Import QFileDialog for saving captures
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QDateTime  # Import QDateTime
from PyQt6.QtGui import QPixmap, QImage, QMovie  # Import QMovie for LLM spinner
import numpy as np
import cv2
import os  # Import os for path handling

# Import custom modules
from video_capture.camera_feed import CameraFeed
from processing.image_processor import ImageProcessor
from ui.widgets.histogram_plotter import HistogramPlotter
from ui.widgets.filter_selector import FilterSelector
from ui.widgets.pipeline_manager import PipelineManager

from llm.llm_integrator import LLMIntegrator
from config.presets import (
    load_presets,
    save_presets,
    add_preset,
    remove_preset,
    PRESETS_FILE,
)
from processing.filters import (
    FILTER_METADATA,
    AVAILABLE_FILTERS,
)  # Import for FilterSelector setup
from processing.image_processing_worker import ImageProcessingWorker  # New worker


class LLMWorker(QThread):
    pipeline_generated = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    status_update = pyqtSignal(str)

    def __init__(self, llm_integrator: LLMIntegrator, user_prompt: str):
        super().__init__()
        self.llm_integrator = llm_integrator
        self.user_prompt = user_prompt

    def run(self):
        self.status_update.emit("LLM: Pensando en tu estilo, por favor espera...")
        try:
            pipeline = self.llm_integrator.generate_filter_pipeline(
                self.user_prompt, list(FILTER_METADATA.keys())
            )
            if pipeline:
                self.pipeline_generated.emit(pipeline)
                self.status_update.emit("LLM: Pipeline generada exitosamente.")
            else:
                self.error_occurred.emit(
                    "LLM: No se pudo generar el pipeline. Intenta de nuevo."
                )
                self.status_update.emit("LLM: Error al generar pipeline.")
        except Exception as e:
            self.error_occurred.emit(f"LLM: Error durante la inferencia: {e}")
            self.status_update.emit("LLM: Error de inferencia.")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        print("MainWindow: Initializing MainWindow UI components...")

        self.setWindowTitle("PDI Live Studio")
        self.setGeometry(100, 100, 1200, 800)

        # --- Apply Dark Theme (QSS) ---
        self._apply_dark_theme()

        # --- Central Widget and Layout ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # --- Video Display Area ---
        self.video_display_layout = QVBoxLayout()
        self.video_label = QLabel("Waiting for video stream...")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setFixedSize(640, 480)  # Fixed size for video display
        self.video_label.setFrameShape(QFrame.Shape.Box)
        self.video_label.setFrameShadow(QFrame.Shadow.Raised)
        self.video_display_layout.addWidget(self.video_label)

        # --- Video Controls (New) ---
        self.video_controls_layout = QHBoxLayout()
        self.play_pause_button = QPushButton("Pausar")
        self.play_pause_button.clicked.connect(self._toggle_camera_feed)
        self.capture_button = QPushButton("Capturar Imagen")
        self.capture_button.clicked.connect(self._capture_frame)

        self.video_controls_layout.addWidget(self.play_pause_button)
        self.video_controls_layout.addWidget(self.capture_button)
        self.video_display_layout.addLayout(self.video_controls_layout)

        # --- Histogram Plotter ---
        self.histogram_widget = HistogramPlotter()
        self.video_display_layout.addWidget(self.histogram_widget)

        self.main_layout.addLayout(self.video_display_layout)

        # --- Controls Panel (Right Side) ---
        self.controls_panel_layout = QVBoxLayout()
        self.controls_panel_layout.setContentsMargins(
            10, 10, 10, 10
        )  # Add some padding

        # --- LLM Integration Group ---
        self.llm_group_box = QGroupBox("Asistente de Estilos (LLM)")
        self.llm_group_box.setCheckable(False)  # Not directly checkable
        self.llm_group_box_layout = QVBoxLayout(self.llm_group_box)

        self.llm_prompt_input = QLineEdit()
        self.llm_prompt_input.setPlaceholderText(
            "Describe el estilo deseado para el video..."
        )
        self.llm_group_box_layout.addWidget(self.llm_prompt_input)

        self.llm_generate_button = QPushButton("Generar Pipeline con LLM")
        self.llm_generate_button.clicked.connect(self._generate_pipeline_with_llm)
        self.llm_group_box_layout.addWidget(self.llm_generate_button)

        # LLM Status Indicator (New)
        self.llm_status_label = QLabel("LLM: Listo")
        self.llm_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.llm_status_label.setStyleSheet(
            "color: #a0a0a0; font-size: 12px; margin-top: 5px;"
        )
        self.llm_group_box_layout.addWidget(self.llm_status_label)

        self.llm_loading_spinner = QLabel()  # Spinner label
        self.llm_loading_spinner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Ensure the path to the GIF is correct based on your resources folder
        spinner_gif_path = os.path.join(
            os.path.dirname(__file__), "..", "resources", "loading_spinner.gif"
        )
        self.llm_movie = QMovie(spinner_gif_path)
        if self.llm_movie.isValid():
            self.llm_loading_spinner.setMovie(self.llm_movie)
            self.llm_loading_spinner.setFixedSize(
                32, 32
            )  # Set a fixed size for the spinner
            self.llm_loading_spinner.setScaledContents(True)  # Scale GIF to label size
            self.llm_loading_spinner.hide()  # Hidden by default
        else:
            print(
                f"Warning: loading_spinner.gif not found or invalid at {spinner_gif_path}."
            )
            self.llm_loading_spinner.setText("Cargando...")  # Fallback text
            self.llm_loading_spinner.hide()

        self.llm_group_box_layout.addWidget(self.llm_loading_spinner)

        # LLM Integrator instance (assumed path is correct from previous phase)
        self.llm_integrator = LLMIntegrator()
        self.llm_thread = None  # To hold the LLM worker thread

        self.controls_panel_layout.addWidget(self.llm_group_box)

        # --- Filter Selector ---
        # Pass available filters and metadata to the selector
        self.filter_selector = FilterSelector(available_filters=AVAILABLE_FILTERS)
        # Connect the signal to the new method
        self.filter_selector.filter_selected_to_add.connect(
            self._add_filter_to_pipeline_from_selector
        )
        self.controls_panel_layout.addWidget(self.filter_selector)

        # --- Pipeline Manager ---
        self.pipeline_manager = PipelineManager()
        self.pipeline_manager.pipeline_updated.connect(self.set_pipeline_from_manager)
        self.controls_panel_layout.addWidget(self.pipeline_manager)

        # Spacer to push everything to the top
        self.controls_panel_layout.addStretch(1)

        self.main_layout.addLayout(self.controls_panel_layout)

        # --- Status Bar (New) ---
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.show_status_message("PDI Live Studio iniciado.")

        # --- Camera Feed Setup ---
        self.camera_feed = CameraFeed()
        self.camera_feed.frame_ready.connect(self._on_camera_frame_ready)
        self.camera_feed.start()
        self.camera_is_running = True  # Track camera state

        # --- Image Processing ---
        self.image_processor = ImageProcessor()
        self.processing_worker = ImageProcessingWorker(self.image_processor)
        self.processing_worker.processed_frame_ready.connect(
            self.update_video_display_and_histogram
        )
        self.processing_worker.error_occurred.connect(self._handle_processing_error)
        self.processing_worker.start()

        # Initial pipeline setup for the image processor and worker
        # CORRECTED LINE: from .get_current_pipeline() to .get_current_pipeline_config()
        self.set_pipeline_from_manager(
            self.pipeline_manager.get_current_pipeline_config()
        )

        # Load and display presets section (from previous phase)
        # Assuming you had _setup_preset_ui() which needs to be uncommented or implemented
        # self._setup_preset_ui()  # Call this if you have it implemented

        # Store current processed frame for capture
        self.current_processed_frame = None  # Initialize

        print("MainWindow: UI setup complete.")

    def _apply_dark_theme(self):
        """Loads and applies the dark theme QSS file."""
        # Corrected path: ui/main_window.py is in 'ui' folder, styles is one level up
        qss_file_path = os.path.join(
            os.path.dirname(__file__), "..", "styles", "dark_theme.qss"
        )
        qss_file_path = os.path.abspath(qss_file_path)  # Get absolute path
        try:
            with open(qss_file_path, "r") as file:
                self.setStyleSheet(file.read())
            print(f"MainWindow: Dark theme loaded from {qss_file_path}")
        except FileNotFoundError:
            print(f"Error: Dark theme QSS file not found at {qss_file_path}")
        except Exception as e:
            print(f"Error loading dark theme QSS: {e}")

    def show_status_message(self, message: str, timeout_ms: int = 3000):
        self.statusBar.showMessage(message, timeout_ms)

    # --- New Video Control Slots ---
    def _toggle_camera_feed(self):
        """Pauses or resumes the camera feed."""
        if self.camera_is_running:
            self.camera_feed.stop_capture_loop()  # Call a new method on CameraFeed
            self.play_pause_button.setText("Reproducir")
            self.camera_is_running = False
            self.show_status_message("Flujo de cámara pausado.")
        else:
            self.camera_feed.start_capture_loop()  # Call a new method on CameraFeed
            self.play_pause_button.setText("Pausar")
            self.camera_is_running = True
            self.show_status_message("Flujo de cámara reanudado.")

    def _capture_frame(self):
        """Captures the current processed frame and saves it."""
        if self.current_processed_frame is not None:
            # Use QFileDialog to allow user to choose save location and name
            timestamp = QDateTime.currentDateTime().toString("yyyyMMdd_hhmmsszzz")
            default_filename = f"capture_{timestamp}.png"
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar Imagen Capturada",
                default_filename,
                "PNG Images (*.png);;All Files (*)",
            )

            if file_path:
                # Ensure the frame is BGR before saving with OpenCV
                frame_to_save = self.current_processed_frame
                if (
                    len(frame_to_save.shape) == 3 and frame_to_save.shape[2] == 3
                ):  # If it's a 3-channel image
                    # Ensure it's BGR if it was RGB for display, OpenCV expects BGR
                    # If it came from the processing_worker, it's likely BGR already,
                    # but being explicit about it.
                    pass  # No conversion needed if it's already BGR from OpenCV

                if cv2.imwrite(file_path, frame_to_save):
                    self.show_status_message(
                        f"Imagen capturada y guardada en {file_path}"
                    )
                    print(f"Frame captured and saved to {file_path}")
                else:
                    self.show_status_message("Error al guardar la imagen capturada.")
                    print(f"Error saving captured frame to {file_path}")
            else:
                self.show_status_message("Guardar imagen cancelado.")
        else:
            self.show_status_message("No hay fotogramas para capturar aún.")

    def _on_camera_frame_ready(self, frame: np.ndarray):
        """
        Receives frames from the CameraFeed and sends them to the ImageProcessingWorker.
        """
        if self.processing_worker.isRunning():
            # Pass a copy of the frame to avoid modification issues across threads
            self.processing_worker.enqueue_frame(frame.copy())

    # Keep this method as is, it updates the display and stores current_processed_frame
    def update_video_display_and_histogram(
        self, processed_frame: np.ndarray, hist_data: np.ndarray
    ):
        """
        Updates the video display and histogram with processed frame data.
        This slot is called from the processing worker thread.
        """
        self.current_processed_frame = (
            processed_frame  # Store the latest processed frame for capture
        )

        if processed_frame is None or processed_frame.size == 0:
            # print("Update display: Received empty frame from processing worker.") # Too verbose
            return

        h, w = processed_frame.shape[:2]

        # Convert processed frame (BGR or Grayscale) to QImage
        if len(processed_frame.shape) == 3:  # Color image (BGR)
            rgb_image = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            bytes_per_line = 3 * w
            q_image = QImage(
                rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888
            )
        else:  # Grayscale image (2D array)
            bytes_per_line = w
            q_image = QImage(
                processed_frame.data,
                w,
                h,
                bytes_per_line,
                QImage.Format.Format_Grayscale8,
            )

        # Scale QImage to fit QLabel size
        pixmap = QPixmap.fromImage(q_image).scaled(
            self.video_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.video_label.setPixmap(pixmap)

        # Update the histogram display with the processed histogram data
        self.histogram_widget.update_plot(hist_data)

    # --- New LLM-related methods (moved from _generate_pipeline_with_llm or added) ---
    def _generate_pipeline_with_llm(self):
        prompt = self.llm_prompt_input.text().strip()
        if not prompt:
            self.show_status_message(
                "Por favor, introduce una descripción para el LLM.", 3000
            )
            return

        # Disable UI elements during LLM processing
        self.llm_generate_button.setEnabled(False)
        self.llm_prompt_input.setEnabled(False)
        self.filter_selector.setEnabled(False)
        self.pipeline_manager.setEnabled(False)

        self.llm_status_label.setText("LLM: Procesando...")
        if self.llm_movie.isValid():
            self.llm_loading_spinner.show()
            self.llm_movie.start()

        self.llm_thread = LLMWorker(self.llm_integrator, prompt)
        self.llm_thread.pipeline_generated.connect(self._on_pipeline_generated_by_llm)
        self.llm_thread.error_occurred.connect(self._on_llm_error)
        self.llm_thread.status_update.connect(
            self.llm_status_label.setText
        )  # Update status label
        self.llm_thread.finished.connect(
            self._on_llm_finished
        )  # Enable UI elements when finished
        self.llm_thread.start()

    def _on_pipeline_generated_by_llm(self, pipeline: list):
        """Slot to receive the generated pipeline from LLMWorker."""
        if pipeline:
            self.pipeline_manager.set_pipeline_from_config(
                pipeline
            )  # Update the pipeline manager's UI
            self.image_processor.set_pipeline(
                pipeline
            )  # Update the image processor's pipeline
            self.show_status_message("Pipeline actualizada por LLM.")
        else:
            self.show_status_message("LLM no pudo generar un pipeline válido.")

    def _on_llm_error(self, error_message: str):
        """Slot to handle errors from LLMWorker."""
        QMessageBox.warning(self, "Error del LLM", error_message)
        self.show_status_message(f"Error LLM: {error_message}", 5000)

    def _on_llm_finished(self):
        """Called when the LLMWorker thread finishes, regardless of success or error."""
        # Enable UI elements
        self.llm_generate_button.setEnabled(True)
        self.llm_prompt_input.setEnabled(True)
        self.filter_selector.setEnabled(True)
        self.pipeline_manager.setEnabled(True)

        if self.llm_movie.isValid():
            self.llm_movie.stop()
            self.llm_loading_spinner.hide()
        # The status label will be set by the last status_update signal or error_occurred signal

    # --- New method for FilterSelector to add filter to pipeline ---
    def _add_filter_to_pipeline_from_selector(self, filter_name: str):
        """
        Adds a selected filter from the FilterSelector to the ImageProcessor's pipeline
        and updates the PipelineManager UI.
        """
        # The PipelineManager's add_filter_to_pipeline already gets default params
        # from filters.py. We just need to tell it which filter to add.
        self.pipeline_manager.add_filter_to_pipeline(filter_name)
        self.show_status_message(f"Filtro '{filter_name}' añadido al pipeline.")
        # The pipeline_manager will emit pipeline_updated, which will then call set_pipeline_from_manager

    # Existing methods, ensure they are present as discussed in previous phases
    def set_pipeline_from_manager(self, pipeline_config: list):
        """
        Receives the updated pipeline from PipelineManager and applies it to the
        ImageProcessor.
        """
        self.image_processor.set_pipeline(pipeline_config)
        print("MainWindow: ImageProcessor pipeline updated from PipelineManager.")
        # No status message here, as pipeline_manager emits it frequently on small changes

    def _handle_processing_error(self, error_message: str):
        """
        Handles errors emitted by the ImageProcessingWorker.
        """
        QMessageBox.critical(self, "Error de Procesamiento de Imagen", error_message)
        self.show_status_message(f"Error de procesamiento: {error_message}", 5000)

    def _setup_preset_ui(self):
        """
        Sets up the UI elements for preset management and loads initial presets.
        This method will be called during MainWindow initialization.
        """
        # --- Presets Section (already added in __init__, just connecting logic) ---
        # Assuming these widgets already exist from previous steps in __init__
        # self.presets_group = QGroupBox("Gestión de Presets")
        # self.preset_combobox = QComboBox()
        # self.save_preset_name_input = QLineEdit()
        # save_preset_button = QPushButton("Guardar Preset Actual")
        # load_preset_button = QPushButton("Cargar Preset")
        # delete_preset_button = QPushButton("Eliminar Preset Seleccionado")
        # self.preset_status_output = QLabel("")

        # Connect signals for preset buttons
        self.findChild(QPushButton, "Cargar Preset").clicked.connect(
            self._on_load_preset_clicked
        )
        self.findChild(QPushButton, "Guardar Preset Actual").clicked.connect(
            self._on_save_preset_clicked
        )
        self.findChild(QPushButton, "Eliminar Preset Seleccionado").clicked.connect(
            self._on_delete_preset_clicked
        )

        self._load_and_populate_presets()  # Load presets on startup

    # --- Presets Management Slots (Copied from previous phase, ensure they are defined) ---
    def _load_and_populate_presets(self):
        """Loads presets from file and populates the QComboBox."""
        self.available_presets = load_presets()
        self.preset_combobox.clear()
        if self.available_presets:
            self.preset_combobox.addItems(sorted(self.available_presets.keys()))
            self.preset_combobox.setCurrentIndex(-1)  # No selection initially
            self.preset_status_output.setText(
                f"Presets cargados: {len(self.available_presets)}"
            )
        else:
            self.preset_combobox.setPlaceholderText("No hay presets disponibles")
            self.preset_status_output.setText("No hay presets guardados.")

    def _on_load_preset_clicked(self):
        """Loads the selected preset and applies it to the pipeline."""
        selected_preset_name = self.preset_combobox.currentText()
        if (
            not selected_preset_name
            or selected_preset_name == "No hay presets disponibles"
        ):
            self.preset_status_output.setText("Selecciona un preset para cargar.")
            return

        pipeline_to_load = self.available_presets.get(selected_preset_name)
        if pipeline_to_load:
            self.pipeline_manager.set_pipeline_from_config(pipeline_to_load)
            self.preset_status_output.setText(
                f"Preset '{selected_preset_name}' cargado."
            )
        else:
            self.preset_status_output.setText(
                f"Error: Preset '{selected_preset_name}' no encontrado."
            )

    def _on_save_preset_clicked(self):
        """Saves the current pipeline as a new preset."""
        preset_name = self.save_preset_name_input.text().strip()
        if not preset_name:
            self.preset_status_output.setText(
                "Por favor, introduce un nombre para el preset."
            )
            return

        current_pipeline = self.pipeline_manager.get_current_pipeline_config()
        if not current_pipeline:
            self.preset_status_output.setText(
                "La pipeline actual está vacía. No se puede guardar."
            )
            return

        try:
            add_preset(preset_name, current_pipeline)
            self.preset_status_output.setText(
                f"Preset '{preset_name}' guardado exitosamente."
            )
            self.save_preset_name_input.clear()  # Clear input field
            self._load_and_populate_presets()  # Refresh combobox
        except Exception as e:
            self.preset_status_output.setText(f"Error al guardar preset: {e}")

    def _on_delete_preset_clicked(self):
        """Deletes the selected preset."""
        selected_preset_name = self.preset_combobox.currentText()
        if (
            not selected_preset_name
            or selected_preset_name == "No hay presets disponibles"
        ):
            self.preset_status_output.setText("Selecciona un preset para eliminar.")
            return

        try:
            remove_preset(selected_preset_name)
            self.preset_status_output.setText(
                f"Preset '{selected_preset_name}' eliminado."
            )
            self._load_and_populate_presets()  # Refresh combobox
        except Exception as e:
            self.preset_status_output.setText(f"Error al eliminar preset: {e}")

    def closeEvent(self, event):
        """
        Handles the window close event to ensure all threads are stopped cleanly.
        """
        print("MainWindow: closeEvent triggered. Stopping threads...")
        if self.camera_feed.isRunning():
            self.camera_feed.stop()
            self.camera_feed.wait()
            print("MainWindow: CameraFeed stopped.")
        if self.processing_worker.isRunning():
            self.processing_worker.stop()
            self.processing_worker.wait()
            print("MainWindow: Processing worker stopped.")
        if self.llm_thread and self.llm_thread.isRunning():
            print("MainWindow: Stopping LLM thread...")
            self.llm_thread.quit()
            self.llm_thread.wait()
            print("MainWindow: LLM thread stopped.")
        print("MainWindow: All threads stopped.")
        event.accept()

