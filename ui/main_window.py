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
    QTabWidget,
    QSplitter,
    QCheckBox,
    QDoubleSpinBox,
)
from PyQt6.QtCore import (
    Qt,
    QThread,
    pyqtSignal,
    QTimer,
    QDateTime,
    QSettings,
)  # Import QDateTime
from PyQt6.QtGui import QPixmap, QImage, QMovie  # Import QMovie for LLM spinner
import numpy as np
import cv2
import os  # Import os for path handling

# Import custom modules
from video_capture.camera_feed import CameraFeed
from ui.widgets.histogram_plotter import HistogramPlotter
from ui.widgets.filter_selector import FilterSelector
from ui.widgets.style_input_preview import StyleInputPreview
from ui.widgets.pipeline_manager import PipelineManager
from ui.widgets.preset_selector import PresetSelector
from ui.widgets.favorites_tab import FavoritesTab
from processing.image_processor import ImageProcessor
from processing.image_processing_worker import ImageProcessingWorker  # New worker

# from llm.llm_integrator import LLMIntegrator
from llm.pipeline_generator import PipelineGenerator

from config.presets import (
    load_presets,
    save_presets,
    add_preset,
    remove_preset,
    PRESETS_FILE,
)

# from config.preset_meta import (
#    add_to_recent,
#    get_recent,
#    toggle_favorite,
#    get_favorites,
#    is_favorite,
# )
from processing.filters import (
    FILTER_METADATA,
    AVAILABLE_FILTERS,
)  # Import for FilterSelector setup


class MainWindow(QMainWindow):
    def __init__(self, pipeline_generator: PipelineGenerator):
        super().__init__()
        self.pipeline_generator = pipeline_generator
        print("MainWindow: Initializing MainWindow UI components...")

        self.setWindowTitle("PDI Live Studio")
        self.setGeometry(100, 100, 1200, 800)

        # --- Apply Dark Theme (QSS) ---
        self._apply_dark_theme()

        # --- Central Widget and Layout ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        # self.pipeline_tabs = QTabWidget()

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

        # --- Camera Feed Setup ---
        self.camera_feed = CameraFeed()
        self.camera_feed.frame_ready.connect(self._on_camera_frame_ready)
        self.camera_feed.start()
        self.camera_is_running = True  # Track camera state

        # --- Controls Panel (Right Side) ---
        self.controls_panel_layout = QVBoxLayout()
        self.controls_panel_layout.setContentsMargins(10, 10, 10, 10)

        # --- Initialize widgets before using ---
        self.filter_selector = FilterSelector(available_filters=AVAILABLE_FILTERS)
        self.filter_selector.filter_selected_to_add.connect(
            self._add_filter_to_pipeline_from_selector
        )

        self.pipeline_manager = PipelineManager()
        self.pipeline_manager.pipeline_updated.connect(self.set_pipeline_from_manager)

        self.style_preview_widget = StyleInputPreview(
            self.camera_feed, self.pipeline_generator
        )

        # --- LLM Integration Group ---
        self.llm_group_box = QGroupBox("Asistente de Estilos (LLM)")
        self.llm_group_box_layout = QVBoxLayout(self.llm_group_box)

        self.llm_prompt_input = QLineEdit()
        self.llm_prompt_input.setPlaceholderText(
            "Describe el estilo deseado para el video..."
        )
        self.llm_group_box_layout.addWidget(self.llm_prompt_input)

        self.llm_generate_button = QPushButton("Generar Pipeline con LLM")
        self.llm_generate_button.clicked.connect(self._generate_pipeline_with_llm)
        self.llm_group_box_layout.addWidget(self.llm_generate_button)

        self.temperature_input = QDoubleSpinBox()
        self.temperature_input.setRange(0.0, 1.0)
        self.temperature_input.setSingleStep(0.05)
        self.temperature_input.setValue(0.2)
        self.temperature_input.setSuffix("  Temperatura")
        self.llm_group_box_layout.addWidget(self.temperature_input)

        self.debug_checkbox = QCheckBox("Mostrar prompt generado")
        self.llm_group_box_layout.addWidget(self.debug_checkbox)

        self.llm_status_label = QLabel("LLM: Listo")
        self.llm_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.llm_group_box_layout.addWidget(self.llm_status_label)

        self.llm_loading_spinner = QLabel()
        self.llm_loading_spinner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        spinner_gif_path = os.path.join(
            os.path.dirname(__file__), "..", "resources", "loading_spinner.gif"
        )
        self.llm_movie = QMovie(spinner_gif_path)
        if self.llm_movie.isValid():
            self.llm_loading_spinner.setMovie(self.llm_movie)
            self.llm_loading_spinner.setFixedSize(32, 32)
            self.llm_loading_spinner.setScaledContents(True)
            self.llm_loading_spinner.hide()
        else:
            self.llm_loading_spinner.setText("Cargando...")
            self.llm_loading_spinner.hide()
        self.llm_group_box_layout.addWidget(self.llm_loading_spinner)

        self.preset_selector = PresetSelector()
        self.preset_selector.set_pipeline_source(
            self.pipeline_manager.get_current_pipeline_config
        )
        self.preset_selector.preset_applied.connect(self._apply_preset_from_selector)

        # --- Tabs for Manual flux vs LLM assistant ---
        self.pipeline_tabs = QTabWidget()

        # Manual Tab
        manual_tab = QWidget()
        manual_layout = QVBoxLayout(manual_tab)
        manual_layout.addWidget(self.filter_selector)

        # Splitter horizontal entre pipeline y presets
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.pipeline_manager)
        splitter.addWidget(self.preset_selector)

        # Opcional: proporción inicial (60% pipeline, 40% presets)
        splitter.setSizes([600, 400])

        manual_layout.addWidget(splitter)

        # Favorites Tab
        self.favorites_tab = FavoritesTab(self._apply_preset_from_selector)

        # LLM Tab
        llm_tab = QWidget()
        llm_layout = QVBoxLayout(llm_tab)
        llm_layout.addWidget(self.llm_group_box)
        llm_layout.addWidget(self.style_preview_widget)

        self.pipeline_tabs.addTab(manual_tab, "Manual")
        self.pipeline_tabs.addTab(llm_tab, "Asistente LLM")
        self.pipeline_tabs.addTab(self.favorites_tab, "Favoritos")

        self.controls_panel_layout.addWidget(self.pipeline_tabs)
        self.controls_panel_layout.addStretch(1)
        self.main_layout.addLayout(self.controls_panel_layout)

        # --- Status Bar (New) ---
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.show_status_message("PDI Live Studio iniciado.")

        # --- Image Processing ---
        self.image_processor = ImageProcessor()
        self.processing_worker = ImageProcessingWorker(self.image_processor)
        self.processing_worker.processed_frame_ready.connect(
            self.update_video_display_and_histogram
        )
        self.processing_worker.error_occurred.connect(self._handle_processing_error)
        self.processing_worker.start()

        # Initial pipeline setup for the image processor and worker
        self.set_pipeline_from_manager(
            self.pipeline_manager.get_current_pipeline_config()
        )

        self.pipeline_generator = pipeline_generator
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
        self.style_preview_widget.set_prompt(prompt)
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

        try:
            self.pipeline_generator.debug = self.debug_checkbox.isChecked()
            self.pipeline_generator.temperature = self.temperature_input.value()

            pipeline = self.pipeline_generator.generate(prompt)

            if pipeline:
                self.pipeline_manager.set_pipeline_from_config(pipeline)
                self.image_processor.set_pipeline(pipeline)
                self.show_status_message("Pipeline generada por LLM.")
                self.llm_status_label.setText("LLM: Pipeline generada exitosamente.")
            else:
                self.show_status_message("LLM no pudo generar un pipeline válido.")
                self.llm_status_label.setText("LLM: No se pudo generar pipeline.")
        except Exception as e:
            self.show_status_message(f"Error LLM: {e}", 5000)
            self.llm_status_label.setText("LLM: Error durante la inferencia.")
        finally:
            self.llm_generate_button.setEnabled(True)
            self.llm_prompt_input.setEnabled(True)
            self.filter_selector.setEnabled(True)
            self.pipeline_manager.setEnabled(True)
            if self.llm_movie.isValid():
                self.llm_movie.stop()
                self.llm_loading_spinner.hide()

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

    def _apply_preset_from_selector(self, name: str, pipeline: list):
        self.pipeline_manager.set_pipeline_from_config(pipeline)
        self.image_processor.set_pipeline(pipeline)
        self.show_status_message(f"Preset '{name}' aplicado.")

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
        #        if self.llm_thread and self.llm_thread.isRunning():
        #            print("MainWindow: Stopping LLM thread...")
        #            self.llm_thread.quit()
        #            self.llm_thread.wait()
        #            print("MainWindow: LLM thread stopped.")
        print("MainWindow: All threads stopped.")
        event.accept()
