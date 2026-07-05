from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.ui.widgets.tag_list_widget import TagListWidget


class ApiKeyPage(QWidget):
    """Shared YouTube Data API DEV_KEY pool used by all 4 analysis modes."""

    def __init__(self, parent=None):
        super().__init__(parent)

        description = QLabel(
            "여기서 등록한 API 키는 모든 분석 모드에서 공통으로 사용됩니다.\n"
            "쿼터가 초과되면 다음 키로 자동 전환됩니다."
        )
        description.setWordWrap(True)

        self.key_list = TagListWidget(placeholder="YouTube Data API 키 입력")

        layout = QVBoxLayout(self)
        layout.addWidget(description)
        layout.addWidget(self.key_list)
