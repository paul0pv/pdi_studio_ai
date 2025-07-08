# ui/main_window/main_window.py

from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from PyQt6.QtGui import QAction, QPixmap
from PyQt6.QtCore import Qt
from ui.main_window.layout_video import build_video_area
from ui.main_window.layout_pipeline_tabs import build_pipeline_tabs
from ui.main_window.theme_loader import apply_dark_theme
from ui.main_window.handlers_camera import setup_camera_handlers
from ui.main_window.handlers_llm import setup_llm_handlers
from ui.main_window.handlers_pipeline import setup_pipeline_handlers
from ui.main_window.utils import convert_frame_to_qimage
from setup_launcher import launch_setup_gui
from ui.widgets.histogram_dockable_panel import HistogramDockablePanel
from config.settings import SettingsManager
from video_capture.camera_feed import CameraFeed
from processing.image_processor import ImageProcessor


class MainWindow(QMainWindow):
    def __init__(self, pipeline_generator):
        super().__init__()
        self.setWindowTitle("PDI Live Studio")
        self.setGeometry(100, 100, 1200, 800)

        self.pipeline_generator = pipeline_generator
        self.camera_feed = CameraFeed()
        self.camera_feed.frame_ready.connect(self._on_frame_ready)
        self.camera_feed.start()

        self.image_processor = ImageProcessor()
        self.camera_is_running = True
        self.current_processed_frame = None

        self.histogram_dock = HistogramDockablePanel(self.image_processor, self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.histogram_dock)

        apply_dark_theme(self)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        self.video_display_layout = build_video_area(self)
        self.pipeline_tabs_layout = build_pipeline_tabs(self)

        self.main_layout.addLayout(self.video_display_layout)
        self.main_layout.addLayout(self.pipeline_tabs_layout)

        setup_camera_handlers(self)
        setup_llm_handlers(self)
        setup_pipeline_handlers(self)

        self._build_status_bar()
        self._build_menu_bar()

        self.refresh_all()

    def _on_frame_ready(self, frame):
        self.current_processed_frame = self.image_processor.process_frame(frame)
        qimage = convert_frame_to_qimage(self.current_processed_frame)
        self.video_label.setPixmap(QPixmap.fromImage(qimage))
        self.histogram_dock.update_with_frame(frame, self.current_processed_frame)

    def _build_status_bar(self):
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("🟢 Sistema inicializado correctamente.")

    def show_status_message(self, message: str, timeout: int = 5000):
        """
        Muestra un mensaje en la barra de estado.

        Args:
            message (str): Texto a mostrar.
            timeout (int): Tiempo en milisegundos antes de ocultar el mensaje.
        """
        if hasattr(self, "status_bar"):
            self.status_bar.showMessage(message, timeout)

    def _build_menu_bar(self):
        menu = self.menuBar()
        config_menu = menu.addMenu("Configuración")
        view_menu = menu.addMenu("Ver")

        relaunch_action = QAction("Reconfigurar IA", self)
        relaunch_action.triggered.connect(self._relaunch_setup)
        config_menu.addAction(relaunch_action)
        toggle_histogram_action = QAction("Mostrar/Ocultar Histograma", self)
        toggle_histogram_action.triggered.connect(
            lambda: self.histogram_dock.setVisible(not self.histogram_dock.isVisible())
        )
        view_menu.addAction(toggle_histogram_action)

    def _apply_preset_from_selector(self, name: str, pipeline: list):
        if not pipeline or not isinstance(pipeline, list):
            self.show_status_message(f"⚠️ Preset '{name}' inválido o vacío.")
            return
        self.pipeline_manager.set_pipeline_from_config(pipeline)
        self.image_processor.set_pipeline(pipeline)
        self.show_status_message(f"✅ Preset '{name}' aplicado.")

    def _apply_pipeline_from_preview(self):
        self.show_status_message("✅ Pipeline aplicada desde vista previa.")

    # Aquí puede agregar lógica para aplicar la pipeline si es necesario

    def _relaunch_setup(self):
        settings = SettingsManager()
        launch_setup_gui(settings)
        self.refresh_all()

    def refresh_all(self):
        self.preset_selector.refresh()
        self.favorites_tab.refresh()
        self.pipeline_manager.set_pipeline_from_config(
            self.image_processor.get_pipeline()
        )
        self.show_status_message("🔄 Interfaz sincronizada.")

    def closeEvent(self, event):
        if hasattr(self, "camera_feed") and self.camera_feed.isRunning():
            print("[MainWindow] 🔻 Deteniendo hilo de cámara...")
            self.camera_feed.stop()
            self.camera_feed.wait()

        if hasattr(self, "histogram_dock"):
            thread = getattr(self.histogram_dock.panel, "_active_thread", None)
            if thread and thread.isRunning():
                print("[MainWindow] 🔻 Deteniendo hilo de histograma...")
                thread.quit()
                thread.wait()

        event.accept()
