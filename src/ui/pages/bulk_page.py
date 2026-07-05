from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QDateEdit, QFormLayout, QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget

from src.ui.date_utils import previous_month_range
from src.ui.excel_utils import parse_channel_urls_from_excel
from src.ui.widgets.file_path_edit import FilePathEdit


class BulkPage(QWidget):
    """--yb: sweep every video on each given channel within a date range."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.input_excel_path = FilePathEdit(mode="open", name_filter="Excel (*.xlsx)")
        self.load_channels_button = QPushButton("채널 목록 불러오기")

        self.channel_display = QPlainTextEdit()
        self.channel_display.setReadOnly(True)
        self.channel_display.setMinimumHeight(90)
        self.channel_display.setPlaceholderText("엑셀에서 채널 목록을 불러오면 여기에 표시됩니다.")

        channel_col = QVBoxLayout()
        channel_col.addWidget(self.channel_display)
        channel_col.addWidget(self.load_channels_button)

        self.start_date = QDateEdit(calendarPopup=True)
        self.end_date = QDateEdit(calendarPopup=True)
        start_default, end_default = previous_month_range()
        self.start_date.setDate(start_default)
        self.end_date.setDate(end_default)

        date_row = QHBoxLayout()
        date_row.addWidget(self.start_date)
        date_row.addWidget(QLabel("~"))
        date_row.addWidget(self.end_date)

        self.output_path = FilePathEdit(mode="save", name_filter="CSV/Excel (*.csv *.xlsx)")

        self.api_key_page = None
        self._channels = []

        self.load_channels_button.clicked.connect(self._on_load_channels_clicked)

        form = QFormLayout(self)
        form.addRow("입력 엑셀", self.input_excel_path)
        form.addRow("채널 목록", channel_col)
        form.addRow("검색 기간", date_row)
        form.addRow("출력 파일", self.output_path)

    def _on_load_channels_clicked(self):
        path = self.input_excel_path.text().strip()
        if not path:
            return
        self._set_channels(parse_channel_urls_from_excel(path))

    def _set_channels(self, channels):
        self._channels = [c.strip() for c in channels if c.strip()]
        self.channel_display.setPlainText(", ".join(self._channels))

    def to_config(self):
        """Serialize to the KEY=VALUE pairs used by run/bulk/input_bulk.txt."""
        dev_keys = ", ".join(self.api_key_page.key_list.values()) if self.api_key_page else ""
        return [
            ("PERIOD_DATE_START", self.start_date.date().toString("yyyy.MM.dd")),
            ("PERIOD_DATE_END", self.end_date.date().toString("yyyy.MM.dd")),
            ("OUTPUT", self.output_path.text()),
            ("DEV_KEY", dev_keys),
            ("CHANNEL", ", ".join(self._channels)),
        ]

    def from_config(self, config):
        """Populate fields from a dict parsed out of an input_bulk.txt-style file."""
        if "PERIOD_DATE_START" in config:
            self.start_date.setDate(QDate.fromString(config["PERIOD_DATE_START"], "yyyy.MM.dd"))
        if "PERIOD_DATE_END" in config:
            self.end_date.setDate(QDate.fromString(config["PERIOD_DATE_END"], "yyyy.MM.dd"))
        if "OUTPUT" in config:
            self.output_path.setText(config["OUTPUT"])
        if "DEV_KEY" in config and self.api_key_page:
            self.api_key_page.key_list.set_values([v.strip() for v in config["DEV_KEY"].split(",") if v.strip()])
        if "CHANNEL" in config:
            self._set_channels(config["CHANNEL"].split(","))
