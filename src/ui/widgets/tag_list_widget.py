from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget


class TagListWidget(QWidget):
    """Editable, comma-separated list of short text values (keywords, channel URLs, ...).

    The box is a plain text field the user can type/edit directly at any time, like
    Notepad (no double-click needed); values() always reads whatever text currently
    sits in it, so manual edits are picked up immediately without going through the
    add/clear buttons.
    """

    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)

        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText(placeholder)
        self.add_button = QPushButton("추가")
        self.clear_button = QPushButton("전체 삭제")

        self.text_edit = QPlainTextEdit()
        self.text_edit.setMinimumHeight(90)

        input_row = QHBoxLayout()
        input_row.addWidget(self.input_edit)
        input_row.addWidget(self.add_button)
        input_row.addWidget(self.clear_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.text_edit)
        layout.addLayout(input_row)

        self.add_button.clicked.connect(self._add_from_input)
        self.input_edit.returnPressed.connect(self._add_from_input)
        self.clear_button.clicked.connect(self._clear_all)

    def _add_from_input(self):
        new_values = [v.strip() for v in self.input_edit.text().split(",") if v.strip()]
        if not new_values:
            return
        current = self.values()
        for value in new_values:
            if value not in current:
                current.append(value)
        self.text_edit.setPlainText(", ".join(current))
        self.input_edit.clear()

    def _clear_all(self):
        self.text_edit.setPlainText("")

    def values(self):
        return [v.strip() for v in self.text_edit.toPlainText().split(",") if v.strip()]

    def set_values(self, values):
        cleaned = []
        for value in values:
            value = value.strip()
            if value and value not in cleaned:
                cleaned.append(value)
        self.text_edit.setPlainText(", ".join(cleaned))
