# ui/main_window/theme_loader.py

import os


def apply_dark_theme(main_window):
    qss_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "styles", "dark_theme.qss"
    )
    try:
        with open(qss_path, "r") as file:
            main_window.setStyleSheet(file.read())
    except Exception as e:
        print(f"[ThemeLoader] Error cargando QSS: {e}")
