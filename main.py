from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QComboBox,
    QPushButton,
    QLabel, 
    QTableWidgetItem,
    QHeaderView,
    QScrollArea
) 
from PyQt6.QtCore import QDate, Qt, QSettings
from PyQt6.QtGui import QPalette, QColor, QBrush
# from modified_interface import Ui_Form
from main_interface import Ui_Form
from datetime import timedelta
from typing import List
from custom_widget import StyledComboBox, CustomMessageBox

import sys
import os
import json
import traceback
import warnings

class Main(QWidget, Ui_Form):
    def __init__(self, path_loc: str):
        super().__init__()
        self.set_dark_mode_if_needed() # Check and set dark mode first
        self.setupUi(self)
        self.path_loc = path_loc
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.showMaximized()

        self.data = self.load_json()
        self.apply_styles()
        
        self._combo_box_ref: List[QComboBox] = []
        self._label_ref: List[QLabel] = []
        self.main_task = [
            "Casino Plus OSM",
            "Casino Plus OTG",
            "Dheights OSM",
            "Dheights OTG",
            "Midori OSM",
            "Megabet",
            "Glowlight eBingo",
            "Glowlight Sportsbetting",
            "Glowlight eCasion(eGames & live casino)",
            "Dheights screenshots",
            "Megabet non-integration",
            "Midori OTG non-integration"
        ]
        self._previous_date_information = None

        self.current_date_information.setText(self.show_time())
        self.current_date_information.setStyleSheet("color: 'blue';")
        self.current_date_information.setDisabled(True)

        self.add_scrollable_tasks()
        self.set_filter_date()
        self.filter_date.currentIndexChanged.connect(self.display_information)

    def set_dark_mode_if_needed(self):
        """Checks for system dark mode and applies a dark palette."""
        settings = QSettings("HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize", QSettings.Format.NativeFormat)
        if settings.value("AppsUseLightTheme") == 0:
            # System is in dark mode, apply dark palette
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 220))
            palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
            palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
            QApplication.setPalette(palette)
            
            # Additional dark mode styling (e.g., for disabled widgets)
            qdarkstyle_qss = """
                /* Disabled widgets in dark mode */
                *:disabled {
                    color: #a0a0a0;
                    background-color: #3e3e3e;
                }
            """
            QApplication.instance().setStyleSheet(qdarkstyle_qss)

    def load_json(self):
        """Load JSON into memory, return {} if missing or invalid."""
        if not os.path.exists(self.path_loc):
            return {}
        
        try:
            with open(self.path_loc, "r") as f:
                if os.path.getsize(self.path_loc) == 0:
                    return {}
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            traceback.print_exc()
            CustomMessageBox.critical(self, "Error", "Failed to load JSON file.")
            return {}

    def save_json(self):
        """Write self.data back to file."""
        with open(self.path_loc, "w") as f:
            json.dump(self.data, f, indent=4)

    def add_scrollable_tasks(self):
        task_container = QWidget()
        task_layout = QVBoxLayout(task_container)

        for task in self.main_task:
            h_box = QHBoxLayout()
            label = QLabel(task)
            combo_box = StyledComboBox(self)
            combo_box.addItems(["In progress", "Done"])
            combo_box.setCursor(Qt.CursorShape.PointingHandCursor)
            combo_box.currentIndexChanged.connect(self.check_if_all_done)
            self._combo_box_ref.append(combo_box)
            self._label_ref.append(label)
            h_box.addWidget(label)
            h_box.addWidget(combo_box)
            task_layout.addLayout(h_box)
        
        self.save_information = QPushButton("Save Information")
        self.save_information.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_information.clicked.connect(self.save_information_logic)
        self.save_information.setEnabled(False)
        task_layout.addWidget(self.save_information)
        task_layout.addStretch(1)

        self.task_scroll_area = QScrollArea()
        self.task_scroll_area.setWidgetResizable(True)
        self.task_scroll_area.setWidget(task_container)
        self.main_layout.addWidget(self.task_scroll_area)

    def check_if_all_done(self):
        is_done = all(c.currentText().lower() == "done" for c in self._combo_box_ref)
        self.save_information.setEnabled(is_done)
        
    def save_information_logic(self):
        result = {label.text(): status.currentText() for label, status in zip(self._label_ref, self._combo_box_ref)}
        self.data.setdefault(self._previous_date_information, {})
        self.data[self._previous_date_information].update(result)
        self.save_json()
        self.set_filter_date()
        self.filter_date.setCurrentText(self._previous_date_information)
        self.display_information()
        CustomMessageBox.information(self, "Success", "Data Saved Successfully!")

    def set_filter_date(self):
        self.filter_date.clear()
        for date in sorted(self.data.keys()):
            self.filter_date.addItem(date)

        if self.filter_date.count() > 0:
            self.filter_date.setCurrentIndex(self.filter_date.count() - 1) 

    def display_information(self):
        current_text = self.filter_date.currentText()
        if not current_text:
            return
        day_data = self.data.get(current_text, {})
        self.tableWidget.setRowCount(0)
        for row, (task, status) in enumerate(day_data.items()):
            self.tableWidget.insertRow(row)
            task_item = QTableWidgetItem(task)
            status_item = QTableWidgetItem(status)
            self.tableWidget.setItem(row, 0, task_item)
            self.tableWidget.setItem(row, 1, status_item)

    def show_time(self):
        qt_now = QDate.currentDate().toPyDate()
        prev_date = qt_now - timedelta(days=1)
        date_today = qt_now.strftime(r"%m-%d-%Y")
        yesterday = prev_date.strftime(r"%m-%d-%Y")
        self._previous_date_information = yesterday
        return f"Current Date: {date_today} | Processing: {yesterday}"
        
if __name__ == "__main__":
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    app = QApplication(sys.argv)
    main = Main("./data.json")
    main.show()
    
    sys.exit(app.exec())
