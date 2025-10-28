import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from ui.main_window import MainWindow
from config import settings


def main():
    """Main entry point for the application."""
    # Enable high DPI scaling for better display on high-resolution screens
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # Create application instance
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Load global QSS style if available
    qss_file = settings.QSS_DIR / "app.qss"
    if qss_file.exists():
        with open(qss_file, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())

    # Set application icon
    app.setWindowIcon(QIcon(str(settings.APP_ICON)))

    # Create and show main window
    w = MainWindow()
    w.show()

    # Start the application event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
