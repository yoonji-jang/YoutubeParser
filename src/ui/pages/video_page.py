from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QComboBox, QDateEdit, QFormLayout, QHBoxLayout, QLabel, QWidget

from src.ui.date_utils import previous_month_range
from src.ui.widgets.file_path_edit import FilePathEdit
from src.ui.widgets.tag_list_widget import TagListWidget

FILTER_OPTIONS = [
    ("최신", "latest"),
    ("오늘", "today"),
    ("이번 주", "this_week"),
    ("이번 달", "this_month"),
    ("올해", "this_year"),
]


class VideoPage(QWidget):
    """--va: keyword search across YouTube within a date range."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.keyword_list = TagListWidget(placeholder="검색 키워드 입력 후 추가")

        self.start_date = QDateEdit(calendarPopup=True)
        self.end_date = QDateEdit(calendarPopup=True)
        start_default, end_default = previous_month_range()
        self.start_date.setDate(start_default)
        self.end_date.setDate(end_default)

        date_row = QHBoxLayout()
        date_row.addWidget(self.start_date)
        date_row.addWidget(QLabel("~"))
        date_row.addWidget(self.end_date)

        self.filter_combo = QComboBox()
        for label, value in FILTER_OPTIONS:
            self.filter_combo.addItem(label, value)

        self.output_path = FilePathEdit(mode="save", name_filter="CSV/Excel (*.csv *.xlsx)")

        self.api_key_page = None

        form = QFormLayout(self)
        form.addRow("키워드", self.keyword_list)
        form.addRow("검색 기간", date_row)
        form.addRow("필터", self.filter_combo)
        form.addRow("출력 파일", self.output_path)

    def to_config(self):
        """Serialize to the KEY=VALUE pairs used by run/video/input_video.txt."""
        dev_keys = ", ".join(self.api_key_page.key_list.values()) if self.api_key_page else ""
        return [
            ("KEYWORD", ", ".join(self.keyword_list.values())),
            ("PERIOD_DATE_START", self.start_date.date().toString("yyyy.MM.dd")),
            ("PERIOD_DATE_END", self.end_date.date().toString("yyyy.MM.dd")),
            ("OUTPUT", self.output_path.text()),
            ("FILTER", self.filter_combo.currentData()),
            ("DEV_KEY", dev_keys),
        ]

    def from_config(self, config):
        """Populate fields from a dict parsed out of an input_video.txt-style file."""
        if "KEYWORD" in config:
            self.keyword_list.set_values([v.strip() for v in config["KEYWORD"].split(",") if v.strip()])
        if "PERIOD_DATE_START" in config:
            self.start_date.setDate(QDate.fromString(config["PERIOD_DATE_START"], "yyyy.MM.dd"))
        if "PERIOD_DATE_END" in config:
            self.end_date.setDate(QDate.fromString(config["PERIOD_DATE_END"], "yyyy.MM.dd"))
        if "OUTPUT" in config:
            self.output_path.setText(config["OUTPUT"])
        if "FILTER" in config:
            index = self.filter_combo.findData(config["FILTER"])
            if index >= 0:
                self.filter_combo.setCurrentIndex(index)
        if "DEV_KEY" in config and self.api_key_page:
            self.api_key_page.key_list.set_values([v.strip() for v in config["DEV_KEY"].split(",") if v.strip()])
