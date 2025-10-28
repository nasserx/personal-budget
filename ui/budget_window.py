from functools import partial
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFrame, QGroupBox, QLineEdit, QPushButton,
    QScrollArea, QGridLayout, QLabel, QTableWidget, QTableWidgetItem,
    QAbstractItemView, QHeaderView, QProgressBar, QMessageBox, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QEasingCurve, pyqtSignal
from PyQt5.QtGui import QFont
from ui.dialogs import CategoryDialog, ExpenseDialog
from config import settings


class BudgetWindow(QWidget):
    """Budget Management Interface"""

    # Signal to notify data update
    data_updated = pyqtSignal()

    def __init__(self, manager):
        """Initialize the BudgetWindow."""
        super().__init__()
        self.m = manager
        self._is_loading = False
        self._update_queue = []
        self._toast_label = None
        self._current_selected_table = None

        # Connect signals
        self.data_updated.connect(self._safe_reload_ui)

        self.setLayoutDirection(Qt.RightToLeft)
        self._load_styles()
        self._build_ui()

        # Initial UI load
        QTimer.singleShot(100, self._initial_load)

    def _initial_load(self):
        """Perform safe initial data load."""
        self._is_loading = True
        try:
            self._reload_all_data()
        finally:
            self._is_loading = False

    def _load_styles(self):
        """Load QSS style files."""
        try:
            qss_budget = settings.QSS_DIR / "budget.qss"
            qss_dialogs = settings.QSS_DIR / "dialogs.qss"
            qss = ""
            for path in (qss_budget, qss_dialogs):
                if path.exists():
                    with open(path, "r", encoding="utf-8") as f:
                        qss += f.read() + "\n"
            self.setStyleSheet(qss)
        except Exception as e:
            print(f"Error loading styles: {e}")

    def _build_ui(self):
        """Build main UI layout."""
        root = QHBoxLayout(self)
        root.setContentsMargins(24, 16, 24, 16)
        root.setSpacing(16)
        root.addWidget(self._build_right_panel(), 0)
        root.addWidget(self._build_left_panel(), 1)

    def _build_right_panel(self):
        """Create right panel layout."""
        frame = QFrame()
        frame.setFixedWidth(420)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        layout.addWidget(self._build_income_box())
        layout.addWidget(self._build_categories_box())
        layout.addWidget(self._build_add_category_button())
        layout.addStretch(1)
        return frame

    def _build_income_box(self):
        """Build income input section."""
        box = QGroupBox()
        box.setObjectName("grpIncome")
        layout = QVBoxLayout(box)
        layout.setSpacing(6)
        layout.setContentsMargins(0, 0, 0, 25)

        title = QLabel()
        title.setObjectName("lblIncomeTitle")
        title.setFont(QFont("Tajawal", 12, QFont.DemiBold))
        title.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(title)

        row = QHBoxLayout()
        row.setSpacing(6)
        self.income_input = QLineEdit()
        self.income_input.setPlaceholderText("أدخل الدخل الشهري")
        self.income_input.setFixedHeight(36)
        self.income_input.setAlignment(Qt.AlignRight)
        self.income_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        btn_save = QPushButton("حفظ")
        btn_save.setFixedHeight(36)
        btn_save.setFixedWidth(80)
        btn_save.setObjectName("btnSaveIncome")
        btn_save.clicked.connect(self._save_income)

        row.addWidget(self.income_input, 1)
        row.addWidget(btn_save, 0, Qt.AlignVCenter)
        layout.addLayout(row)
        return box

    def _build_categories_box(self):
        """Build categories table box."""
        box = QGroupBox()
        box.setObjectName("grpCategories")
        layout = QVBoxLayout(box)
        layout.setSpacing(8)

        self.tbl = QTableWidget(0, 4)
        self.tbl.setHorizontalHeaderLabels(["اسم الفئة", "المبلغ", "تعديل", "حذف"])
        self._apply_table_style(self.tbl)

        # Connect table selection event
        self.tbl.itemSelectionChanged.connect(lambda: self._on_table_selection_changed(self.tbl))

        h = self.tbl.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 4):
            h.setSectionResizeMode(i, QHeaderView.ResizeToContents)

        layout.addWidget(self.tbl)
        return box

    def _build_add_category_button(self):
        """Create button to add new category."""
        btn = QPushButton("إضافة فئة جديدة")
        btn.setFixedHeight(36)
        btn.setObjectName("btnAddCategory")
        btn.clicked.connect(self._add_category)
        return btn

    def _build_left_panel(self):
        """Create left panel for cards area."""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.cards_host = QWidget()
        self.grid = QGridLayout(self.cards_host)
        self.grid.setSpacing(24)
        self.grid.setAlignment(Qt.AlignTop)
        scroll.setWidget(self.cards_host)
        layout.addWidget(scroll)
        return frame

    def _on_table_selection_changed(self, current_table):
        """Handle table selection change."""
        if self._current_selected_table and self._current_selected_table != current_table:
            self._current_selected_table.clearSelection()
            self._current_selected_table.setCurrentItem(None)
        self._current_selected_table = current_table

    def _clear_all_selections(self):
        """Clear selections from all tables."""
        if self._current_selected_table:
            self._current_selected_table.clearSelection()
            self._current_selected_table.setCurrentItem(None)
            self._current_selected_table = None

    def _reload_all_data(self):
        """Reload all data without rebuilding UI."""
        try:
            self.income_input.blockSignals(True)
            income = self.m.get_monthly_income()
            self.income_input.setText(f"{income:.2f}")
            self.income_input.blockSignals(False)
            self._render_categories_table()
            self._render_cards()
        except Exception as e:
            print(f"Error loading data: {e}")

    def _safe_reload_ui(self):
        """Safely reload the UI asynchronously."""
        if self._is_loading:
            return
        self._is_loading = True
        try:
            QTimer.singleShot(50, self._deferred_reload)
        except Exception as e:
            print(f"Error reloading UI: {e}")
            self._is_loading = False

    def _deferred_reload(self):
        """Deferred UI reload."""
        try:
            self._reload_all_data()
        finally:
            self._is_loading = False

    def _apply_table_style(self, table: QTableWidget, max_visible_rows=6):
        """Apply consistent style to tables."""
        table.setFocusPolicy(Qt.StrongFocus)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        table.verticalHeader().setDefaultSectionSize(31)
        table.setFocusPolicy(Qt.ClickFocus)
        self._fix_table_height(table, max_visible_rows)

    def _fix_table_height(self, table: QTableWidget, visible_rows=6):
        """Fix table height according to visible rows."""
        fixed = table.horizontalHeader().height() + (31 * visible_rows) + 2
        table.setMinimumHeight(fixed)
        table.setMaximumHeight(fixed)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def _save_income(self):
        """Save monthly income value."""
        try:
            value = float(self.income_input.text().strip())
            if value <= 0:
                raise ValueError
        except ValueError:
            self._show_message("يرجى إدخال رقم صحيح.", success=False)
            return
        try:
            self.m.set_monthly_income(value)
            self.data_updated.emit()
            self._show_message("تم حفظ الدخل بنجاح ✅")
        except Exception as e:
            self._show_message(f"خطأ في الحفظ: {str(e)}", success=False)

    def _add_category(self):
        """Add new budget category."""
        try:
            cats = self.m.get_categories()
            remaining = max(100 - sum(c["percentage"] for c in cats), 0)
            dlg = CategoryDialog(self, title="إضافة فئة", init_perc=remaining)
            if dlg.exec_():
                name, perc = dlg.get_data()
                self.m.add_category(name, perc)
                self.data_updated.emit()
                self._show_message("تمت إضافة الفئة بنجاح ✅")
        except Exception as e:
            self._show_message(str(e), success=False)

    def _render_categories_table(self):
        """Render categories table."""
        from config.settings import CURRENCY
        self.tbl.setUpdatesEnabled(False)
        self.tbl.setRowCount(0)
        try:
            inc = self.m.get_monthly_income()
            categories = self.m.get_categories()
            for c in categories:
                r = self.tbl.rowCount()
                self.tbl.insertRow(r)
                self.tbl.setItem(r, 0, QTableWidgetItem(c["name"]))
                allocated = inc * c["percentage"] / 100.0
                self.tbl.setItem(r, 1, QTableWidgetItem(f"{allocated:.0f} {CURRENCY}"))
                btn_edit = QPushButton("تعديل")
                btn_edit.setObjectName("btnEdit")
                btn_del = QPushButton("حذف")
                btn_del.setObjectName("btnDelete")
                btn_edit.clicked.connect(partial(self._edit_category, c["name"], c["percentage"]))
                btn_del.clicked.connect(partial(self._delete_category, c["name"]))
                self.tbl.setCellWidget(r, 2, btn_edit)
                self.tbl.setCellWidget(r, 3, btn_del)
        finally:
            self.tbl.setUpdatesEnabled(True)

    def _edit_category(self, old_name, old_perc):
        """Edit category details."""
        try:
            dlg = CategoryDialog(self, title="تعديل فئة", init_name=old_name, init_perc=old_perc)
            if dlg.exec_():
                n, p = dlg.get_data()
                self.m.update_category(old_name, n, p)
                self.data_updated.emit()
                self._show_message("تم تعديل الفئة بنجاح ✅")
        except Exception as e:
            self._show_message(str(e), success=False)

    def _delete_category(self, name):
        """Delete selected category."""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("تأكيد الحذف")
        msg.setText(f"هل أنت متأكد أنك تريد حذف '{name}'؟")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.button(QMessageBox.Yes).setText("نعم")
        msg.button(QMessageBox.No).setText("إلغاء")
        reply = msg.exec_()
        if reply == QMessageBox.Yes:
            try:
                self.m.delete_category(name)
                self.data_updated.emit()
                self._show_message("تم حذف الفئة 🗑")
            except Exception as e:
                self._show_message(str(e), success=False)

    def _clear_grid(self):
        """Safely clear all cards from layout."""
        for i in reversed(range(self.grid.count())):
            item = self.grid.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                widget.setParent(None)
                widget.deleteLater()

    def _render_cards(self):
        """Render category cards."""
        try:
            self._clear_grid()
            from config.settings import CURRENCY
            inc = self.m.get_monthly_income()
            categories = self.m.get_categories()
            for i, cat in enumerate(categories):
                card = self._create_category_card(cat, inc, CURRENCY)
                if card:
                    self.grid.addWidget(card, i // 2, i % 2)
        except Exception as e:
            print(f"Error rendering cards: {e}")

    def _create_category_card(self, category, income, currency):
        """Create single category card."""
        try:
            card = QFrame()
            card.setObjectName("Card")
            layout = QVBoxLayout(card)
            layout.setContentsMargins(16, 16, 16, 16)
            layout.setSpacing(10)

            title = QLabel(f"{category['name']} ({category['percentage']:.1f}%)")
            title.setFont(QFont("Tajawal", 13, QFont.Bold))
            layout.addWidget(title)

            allocated = income * category["percentage"] / 100.0
            spent = sum(s["amount"] for s in category["sub"])
            remain = allocated - spent
            percent = min((spent / allocated * 100) if allocated > 0 else 0, 100)

            bar = QProgressBar()
            bar.setValue(int(percent))
            bar.setAlignment(Qt.AlignCenter)
            bar.setFormat(f"{percent:.1f}%")
            bar.setMinimum(0)
            bar.setMaximum(100)
            layout.addWidget(bar)

            color = "red" if remain < 0 else "#424242"
            info_text = f"المخصص: {allocated:.0f} {currency} | المصروف: {spent:.0f} {currency} | المتبقي: <span style='color:{color};'>{remain:.0f} {currency}</span>"
            info = QLabel(info_text)
            info.setTextFormat(Qt.RichText)
            info.setObjectName("infoLabel")
            layout.addWidget(info)

            table = self._create_expenses_table(category)
            layout.addWidget(table)

            add_btn = QPushButton("إضافة مصروف")
            add_btn.setFixedHeight(42)
            add_btn.setObjectName("btnAddExpense")
            add_btn.clicked.connect(partial(self._add_expense, category["name"]))
            layout.addWidget(add_btn)

            return card
        except Exception as e:
            print(f"Error creating card: {e}")
            return None

    def _create_expenses_table(self, category):
        """Create expenses table for a category."""
        table = QTableWidget(0, 4)
        table.setHorizontalHeaderLabels(["اسم المصروف", "المبلغ", "تعديل", "حذف"])
        self._apply_table_style(table)
        table.itemSelectionChanged.connect(lambda: self._on_table_selection_changed(table))
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for col in range(1, 4):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        for expense in category["sub"]:
            row = table.rowCount()
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(expense["name"]))
            table.setItem(row, 1, QTableWidgetItem(f"{expense['amount']:.0f}"))
            btn_edit = QPushButton("تعديل")
            btn_edit.setObjectName("btnEdit")
            btn_del = QPushButton("حذف")
            btn_del.setObjectName("btnDelete")
            btn_edit.clicked.connect(partial(self._edit_expense, category["name"], expense["name"], expense["amount"]))
            btn_del.clicked.connect(partial(self._delete_expense, category["name"], expense["name"]))
            table.setCellWidget(row, 2, btn_edit)
            table.setCellWidget(row, 3, btn_del)
        return table

    def _add_expense(self, cat_name):
        """Add expense to a category."""
        try:
            dlg = ExpenseDialog(self, title="إضافة مصروف")
            if dlg.exec_():
                name, amount = dlg.get_data()
                self.m.add_expense(cat_name, name, amount)
                self.data_updated.emit()
                self._show_message("تمت إضافة المصروف ✅")
        except Exception as e:
            self._show_message(str(e), success=False)

    def _edit_expense(self, cat_name, old_name, old_amount):
        """Edit existing expense."""
        try:
            dlg = ExpenseDialog(self, title="تعديل مصروف", init_name=old_name, init_amount=old_amount)
            if dlg.exec_():
                name, amount = dlg.get_data()
                self.m.update_expense(cat_name, old_name, name, amount)
                self.data_updated.emit()
                self._show_message("تم تعديل المصروف ✅")
        except Exception as e:
            self._show_message(str(e), success=False)

    def _delete_expense(self, cat_name, expense_name):
        """Delete expense from a category."""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("تأكيد الحذف")
        msg.setText(f"هل أنت متأكد أنك تريد حذف '{expense_name}'؟")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.button(QMessageBox.Yes).setText("نعم")
        msg.button(QMessageBox.No).setText("إلغاء")
        reply = msg.exec_()
        if reply == QMessageBox.Yes:
            try:
                self.m.delete_expense(cat_name, expense_name)
                self.data_updated.emit()
                self._show_message("تم حذف المصروف 🗑")
            except Exception as e:
                self._show_message(str(e), success=False)

    def _show_message(self, text, success=True):
        """Display temporary toast notification."""
        if self._toast_label:
            try:
                self._toast_label.deleteLater()
            except:
                pass
        toast = QLabel(text, self)
        toast.setAlignment(Qt.AlignCenter)
        toast.setFont(QFont("Tajawal", 11, QFont.Medium))
        toast.setObjectName("toastSuccess" if success else "toastError")
        toast.adjustSize()
        w, h = toast.width() + 20, toast.height() + 6
        x = (self.width() - w) // 2
        toast.setGeometry(x, 25, w, h)
        toast.setWindowOpacity(0.0)
        toast.show()
        anim = QPropertyAnimation(toast, b"windowOpacity")
        anim.setDuration(300)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.start()
        QTimer.singleShot(2500, toast.deleteLater)
        self._toast_label = toast

    def mousePressEvent(self, event):
        """Clear table selection when clicking outside."""
        if event.button() == Qt.LeftButton:
            self._clear_all_selections()
        super().mousePressEvent(event)

    def closeEvent(self, event):
        """Clean resources on window close."""
        try:
            if hasattr(self, '_toast_label') and self._toast_label:
                self._toast_label.deleteLater()
        except:
            pass
        super().closeEvent(event)
