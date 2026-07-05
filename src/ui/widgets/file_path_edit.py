from PyQt5.QtWidgets import QFileDialog, QHBoxLayout, QLineEdit, QPushButton, QWidget


class FilePathEdit(QWidget):
    """Line edit + browse button for picking a file path (open or save)."""

    def __init__(self, mode="save", name_filter="All Files (*)", parent=None):
        super().__init__(parent)
        self.mode = mode
        self.name_filter = name_filter

        self.line_edit = QLineEdit()
        self.browse_button = QPushButton("찾아보기")
        self.browse_button.clicked.connect(self._browse)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.browse_button)

    def _browse(self):
        if self.mode == "open":
            path, _ = QFileDialog.getOpenFileName(self, "파일 선택", "", self.name_filter)
        else:
            path, _ = QFileDialog.getSaveFileName(self, "파일 선택", "", self.name_filter)
        if path:
            self.line_edit.setText(path)

    def text(self):
        return self.line_edit.text()

    def setText(self, value):
        self.line_edit.setText(value)
