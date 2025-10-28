from PyQt5.QtWidgets import QMainWindow, QStackedWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from core.budget_manager import BudgetManager
from ui.budget_window import BudgetWindow
from config.settings import APP_TITLE, APP_ICON


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setWindowIcon(QIcon(str(APP_ICON)))
        self.resize(1280, 800)
        self.setLayoutDirection(Qt.RightToLeft)

        # Initialize budget manager
        self.manager = BudgetManager()

        # Create stacked widget to manage pages
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Display budget management window
        self._show_budget()

    def _show_budget(self):
        """Display the budget management interface."""
        self.budget = BudgetWindow(self.manager)
        self.stack.addWidget(self.budget)
        self.stack.setCurrentWidget(self.budget)
        self.showMaximized()
