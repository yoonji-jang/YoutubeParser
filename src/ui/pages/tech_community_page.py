from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import (
    QCheckBox,
    QDateEdit,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from src.ui.date_utils import previous_month_range
from src.ui.widgets.file_path_edit import FilePathEdit
from src.ui.widgets.tag_list_widget import TagListWidget


class TechCommunityPage(QWidget):
    """--tc: scrape non-YouTube tech forum posts by keyword within a date range."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.keyword_list = TagListWidget(placeholder="검색 키워드 입력 후 추가")

        self.quasarzone_check = QCheckBox("quasarzone")
        self.quasarzone_check.setChecked(True)
        self.coolenjoy_check = QCheckBox("coolenjoy")

        community_col = QVBoxLayout()
        community_col.addWidget(self.quasarzone_check)
        community_col.addWidget(self.coolenjoy_check)

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

        form = QFormLayout(self)
        form.addRow("키워드", self.keyword_list)
        form.addRow("커뮤니티", community_col)
        form.addRow("검색 기간", date_row)
        form.addRow("출력 파일", self.output_path)

    def to_config(self):
        """Serialize to the KEY=VALUE pairs used by run/tech_community/input_tech_community.txt."""
        communities = []
        if self.quasarzone_check.isChecked():
            communities.append("quasarzone")
        if self.coolenjoy_check.isChecked():
            communities.append("coolenjoy")
        return [
            ("KEYWORD", ", ".join(self.keyword_list.values())),
            ("COMMUNITY", ", ".join(communities)),
            ("PERIOD_DATE_START", self.start_date.date().toString("yyyy.MM.dd")),
            ("PERIOD_DATE_END", self.end_date.date().toString("yyyy.MM.dd")),
            ("OUTPUT", self.output_path.text()),
        ]

    def from_config(self, config):
        """Populate fields from a dict parsed out of an input_tech_community.txt-style file."""
        if "KEYWORD" in config:
            self.keyword_list.set_values([v.strip() for v in config["KEYWORD"].split(",") if v.strip()])
        if "COMMUNITY" in config:
            communities = [v.strip() for v in config["COMMUNITY"].split(",")]
            self.quasarzone_check.setChecked("quasarzone" in communities)
            self.coolenjoy_check.setChecked("coolenjoy" in communities)
        if "PERIOD_DATE_START" in config:
            self.start_date.setDate(QDate.fromString(config["PERIOD_DATE_START"], "yyyy.MM.dd"))
        if "PERIOD_DATE_END" in config:
            self.end_date.setDate(QDate.fromString(config["PERIOD_DATE_END"], "yyyy.MM.dd"))
        if "OUTPUT" in config:
            self.output_path.setText(config["OUTPUT"])
