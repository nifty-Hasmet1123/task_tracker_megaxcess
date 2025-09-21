from PyQt6.QtWidgets import QComboBox, QMessageBox
from PyQt6.QtCore import Qt

class StyledComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Pointing hand on the widget itself
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        # Pointing hand on dropdown items
        self.view().setCursor(Qt.CursorShape.PointingHandCursor)

        # Apply styling
        self.setStyleSheet("""
            QComboBox {
                border: 1px solid #aaa;
                border-radius: 6px;
                padding: 6px 10px;
                background: #f9f9f9;
                selection-background-color: #0078d7;
            }

            QComboBox:hover {
                border: 1px solid #0078d7;
                background: #f1faff;
            }

            QComboBox::drop-down {
                border-left: 1px solid #aaa;
                width: 25px;
            }

            QComboBox QAbstractItemView {
                border: 1px solid #aaa;
                selection-background-color: #0078d7;
                selection-color: white;
                background: white;
                outline: 0;
            }

            QComboBox QAbstractItemView::item:hover {
                background: #e6f2ff;   /* hover effect */
                color: black;
            }
        """)

class CustomMessageBox(QMessageBox):
    def __init__(self, icon: QMessageBox.Icon, title: str, text: str, parent=None):
        super().__init__(icon, title, text, parent)
        self.setStandardButtons(QMessageBox.StandardButton.Ok)
        self.apply_cursor()

    def apply_cursor(self):
        """Apply pointing hand cursor to all buttons."""
        for button in self.buttons():
            button.setCursor(Qt.CursorShape.PointingHandCursor)

    @staticmethod
    def info(parent, title: str, text: str):
        msg = CustomMessageBox(QMessageBox.Icon.Information, title, text, parent)
        return msg.exec()

    @staticmethod
    def warning(parent, title: str, text: str):
        msg = CustomMessageBox(QMessageBox.Icon.Warning, title, text, parent)
        return msg.exec()

    @staticmethod
    def error(parent, title: str, text: str):
        msg = CustomMessageBox(QMessageBox.Icon.Critical, title, text, parent)
        return msg.exec()
