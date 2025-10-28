from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt
from config import settings


class CategoryDialog(QDialog):
    """Dialog for adding or editing a budget category."""
    
    def __init__(self, parent=None, title="إضافة فئة", init_name="", init_perc=""):
        """Initialize CategoryDialog."""
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setLayoutDirection(Qt.RightToLeft)
        self.name_input = QLineEdit(init_name)
        self.perc_input = QLineEdit(str(init_perc))

        # Load dialog QSS style
        with open(settings.QSS_DIR / "dialogs.qss", "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

        self._ui()

    def _ui(self):
        """Build the dialog UI layout."""
        self.resize(410, 250)
        self.setMinimumWidth(410)

        layout = QVBoxLayout(self)
        layout.setSpacing(30)

        lbl_name = QLabel("اسم الفئة")
        self.name_input.setPlaceholderText("مثال: إيجار، طعام، ادخار")
        layout.addWidget(lbl_name)
        layout.addWidget(self.name_input)

        lbl_perc = QLabel("النسبة من الدخل (%)")
        self.perc_input.setPlaceholderText("مثال: 10")
        layout.addWidget(lbl_perc)
        layout.addWidget(self.perc_input)

        buttons = QHBoxLayout()
        buttons.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        save_btn = QPushButton("حفظ")
        cancel_btn = QPushButton("إلغاء")
        save_btn.setObjectName("saveBtn")
        cancel_btn.setObjectName("cancelBtn")

        # Connect button signals
        save_btn.clicked.connect(self._on_save)
        cancel_btn.clicked.connect(self.reject)

        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)

    def _on_save(self):
        """Validate inputs and accept dialog if valid."""
        name = self.name_input.text().strip()
        perc_text = self.perc_input.text().strip()

        if not name:
            self._send_message("يرجى إدخال اسم الفئة.", success=False)
            return

        try:
            perc = float(perc_text)
        except ValueError:
            self._send_message("النسبة يجب أن تكون رقمًا.", success=False)
            return

        if perc <= 0:
            self._send_message("النسبة يجب أن تكون أكبر من الصفر.", success=False)
            return

        self.accept()

    def _send_message(self, text, success=False):
        """Send feedback message to parent window."""
        if self.parent() and hasattr(self.parent(), "_show_message"):
            self.parent()._show_message(text, success=success)
        self.reject()

    def get_data(self):
        """Return category name and percentage."""
        try:
            return self.name_input.text().strip(), float(self.perc_input.text().strip())
        except ValueError:
            return self.name_input.text().strip(), 0.0


class ExpenseDialog(QDialog):
    """Dialog for adding or editing an expense."""
    
    def __init__(self, parent=None, title="إضافة مصروف", init_name="", init_amount=""):
        """Initialize ExpenseDialog."""
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setLayoutDirection(Qt.RightToLeft)
        self.name_input = QLineEdit(init_name)
        self.amount_input = QLineEdit(str(init_amount))

        # Load dialog QSS style
        with open(settings.QSS_DIR / "dialogs.qss", "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

        self._ui()

    def _ui(self):
        """Build the dialog UI layout."""
        self.resize(410, 250)
        self.setMinimumWidth(410)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        lbl_name = QLabel("اسم المصروف")
        self.name_input.setPlaceholderText("مثال: إيجار، كهرباء، تسوق")
        layout.addWidget(lbl_name)
        layout.addWidget(self.name_input)

        lbl_amount = QLabel("المبلغ (ريال)")
        self.amount_input.setPlaceholderText("مثال: 250")
        layout.addWidget(lbl_amount)
        layout.addWidget(self.amount_input)

        buttons = QHBoxLayout()
        buttons.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        save_btn = QPushButton("حفظ")
        cancel_btn = QPushButton("إلغاء")
        save_btn.setObjectName("saveBtn")
        cancel_btn.setObjectName("cancelBtn")

        # Connect button signals
        save_btn.clicked.connect(self._on_save)
        cancel_btn.clicked.connect(self.reject)

        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)

    def _on_save(self):
        """Validate inputs and accept dialog if valid."""
        name = self.name_input.text().strip()
        amt_text = self.amount_input.text().strip()

        if not name:
            self._send_message("يرجى إدخال اسم المصروف.", success=False)
            return

        try:
            amt = float(amt_text)
        except ValueError:
            self._send_message("يرجى إدخال رقم صحيح للمبلغ.", success=False)
            return

        if amt < 0:
            self._send_message("المبلغ يجب أن يكون أكبر من او يساوي صفر", success=False)
            return

        self.accept()

    def _send_message(self, text, success=False):
        """Send feedback message to parent window."""
        if self.parent() and hasattr(self.parent(), "_show_message"):
            self.parent()._show_message(text, success=success)
        self.reject()

    def get_data(self):
        """Return expense name and amount."""
        try:
            return self.name_input.text().strip(), float(self.amount_input.text().strip())
        except ValueError:
            return self.name_input.text().strip(), 0.0
