from PyQt5.QtWidgets import QCheckBox, QFormLayout, QHBoxLayout, QLabel, QSpinBox, QWidget

from src.ui.widgets.file_path_edit import FilePathEdit


class InfluencerPage(QWidget):
    """--ia: read channel/video rows from an input workbook, enrich in place."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.input_excel_path = FilePathEdit(mode="open", name_filter="Excel (*.xlsx)")
        self.output_excel_path = FilePathEdit(mode="save", name_filter="Excel (*.xlsx)")

        self.influencer_sheet = QSpinBox()
        self.influencer_sheet.setRange(0, 50)
        self.video_sheet = QSpinBox()
        self.video_sheet.setRange(0, 50)
        self.video_sheet.setValue(1)

        sheet_row = QHBoxLayout()
        sheet_row.addWidget(QLabel("채널 시트"))
        sheet_row.addWidget(self.influencer_sheet)
        sheet_row.addWidget(QLabel("비디오 시트"))
        sheet_row.addWidget(self.video_sheet)

        self.start_row = QSpinBox()
        self.start_row.setRange(1, 100000)
        self.start_row.setValue(5)
        self.start_col = QSpinBox()
        self.start_col.setRange(1, 1000)
        self.start_col.setValue(2)
        self.end_row = QSpinBox()
        self.end_row.setRange(1, 100000)
        self.end_row.setValue(50)
        self.max_result = QSpinBox()
        self.max_result.setRange(1, 500)
        self.max_result.setValue(30)

        self.run_channel_check = QCheckBox("채널 분석 실행 (--yc)")
        self.run_channel_check.setChecked(True)
        self.run_video_check = QCheckBox("비디오 분석 실행 (--yv)")
        self.run_video_check.setChecked(True)

        run_row = QHBoxLayout()
        run_row.addWidget(self.run_channel_check)
        run_row.addWidget(self.run_video_check)

        self.api_key_page = None

        form = QFormLayout(self)
        form.addRow("입력 엑셀", self.input_excel_path)
        form.addRow("출력 엑셀", self.output_excel_path)
        form.addRow("시트 번호", sheet_row)
        form.addRow("시작 행", self.start_row)
        form.addRow("시작 열", self.start_col)
        form.addRow("종료 행", self.end_row)
        form.addRow("채널당 최대 영상 수", self.max_result)
        form.addRow("실행 항목", run_row)

    def to_config(self):
        """Serialize to the KEY=VALUE pairs used by run/influencer/input_influencer.txt."""
        dev_keys = ", ".join(self.api_key_page.key_list.values()) if self.api_key_page else ""
        return [
            ("DEV_KEY", dev_keys),
            ("INPUT_EXCEL", self.input_excel_path.text()),
            ("OUTPUT_EXCEL", self.output_excel_path.text()),
            ("INFLUENCER_SHEET", str(self.influencer_sheet.value())),
            ("VIDEO_SHEET", str(self.video_sheet.value())),
            ("START_ROW", str(self.start_row.value())),
            ("START_COL", str(self.start_col.value())),
            ("END_ROW", str(self.end_row.value())),
            ("MAX_RESULT", str(self.max_result.value())),
        ]

    def from_config(self, config):
        """Populate fields from a dict parsed out of an input_influencer.txt-style file."""
        if "DEV_KEY" in config and self.api_key_page:
            self.api_key_page.key_list.set_values([v.strip() for v in config["DEV_KEY"].split(",") if v.strip()])
        if "INPUT_EXCEL" in config:
            self.input_excel_path.setText(config["INPUT_EXCEL"])
        if "OUTPUT_EXCEL" in config:
            self.output_excel_path.setText(config["OUTPUT_EXCEL"])
        if "INFLUENCER_SHEET" in config:
            self.influencer_sheet.setValue(int(config["INFLUENCER_SHEET"]))
        if "VIDEO_SHEET" in config:
            self.video_sheet.setValue(int(config["VIDEO_SHEET"]))
        if "START_ROW" in config:
            self.start_row.setValue(int(config["START_ROW"]))
        if "START_COL" in config:
            self.start_col.setValue(int(config["START_COL"]))
        if "END_ROW" in config:
            self.end_row.setValue(int(config["END_ROW"]))
        if "MAX_RESULT" in config:
            self.max_result.setValue(int(config["MAX_RESULT"]))
