import os
import re

from PyQt5.QtCore import Qt, QProcess, QProcessEnvironment
from PyQt5.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.core.version import VERSION
from src.ui.config_io import read_key_value_txt, write_key_value_txt
from src.ui.pages.api_key_page import ApiKeyPage
from src.ui.pages.bulk_page import BulkPage
from src.ui.pages.influencer_page import InfluencerPage
from src.ui.pages.tech_community_page import TechCommunityPage
from src.ui.pages.video_page import VideoPage
from src.ui.runner import build_process_args

NAV_ITEMS = [
    "비디오 분석",
    "인플루언서 분석",
    "채널 벌크 분석",
    "테크 커뮤니티 분석",
    "API 키 관리",
]

# tqdm's default bar: " 42%|████████            | 42/100 [00:01<00:02, 21.05it/s]"
PROGRESS_RE = re.compile(r"(\d+)%\|.*?\|\s*(\d+)/(\d+)")
# "[Info] Skip duplicated video id (skipped 37 total so far)"
SKIP_RE = re.compile(r"Skip duplicated video id \(skipped (\d+) total")

# Config keys each mode's process needs a non-empty value for before it's worth launching.
REQUIRED_FIELDS = {
    "video": [("DEV_KEY", "API 키 (API 키 관리 탭)"), ("OUTPUT", "출력 파일 경로")],
    "bulk": [("DEV_KEY", "API 키 (API 키 관리 탭)"), ("OUTPUT", "출력 파일 경로")],
    "influencer": [
        ("DEV_KEY", "API 키 (API 키 관리 탭)"),
        ("INPUT_EXCEL", "입력 엑셀 경로"),
        ("OUTPUT_EXCEL", "출력 엑셀 경로"),
    ],
    "tech_community": [("OUTPUT", "출력 파일 경로")],
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"YoutubeParser v{VERSION}")
        self.resize(1000, 700)

        self.nav_list = QListWidget()
        self.nav_list.addItems(NAV_ITEMS)
        self.nav_list.setFixedWidth(180)

        self.video_page = VideoPage()
        self.bulk_page = BulkPage()
        self.tech_community_page = TechCommunityPage()
        self.influencer_page = InfluencerPage()
        self.api_key_page = ApiKeyPage()

        for page in (self.video_page, self.bulk_page, self.influencer_page):
            page.api_key_page = self.api_key_page

        self.pages = QStackedWidget()
        self.pages.addWidget(self.video_page)
        self.pages.addWidget(self.influencer_page)
        self.pages.addWidget(self.bulk_page)
        self.pages.addWidget(self.tech_community_page)
        self.pages.addWidget(self.api_key_page)

        self.log_console = QPlainTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setPlaceholderText("실행 로그가 여기에 표시됩니다.")

        self.save_log_button = QPushButton("로그 저장")

        log_panel = QWidget()
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(0, 0, 0, 0)
        log_header = QHBoxLayout()
        log_header.addStretch()
        log_header.addWidget(self.save_log_button)
        log_layout.addLayout(log_header)
        log_layout.addWidget(self.log_console)
        log_panel.setLayout(log_layout)

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.pages)
        splitter.addWidget(log_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        self.load_button = QPushButton("입력 파일 불러오기")
        self.save_button = QPushButton("입력 파일로 저장")
        self.run_button = QPushButton("실행")
        self.stop_button = QPushButton("중지")
        self.stop_button.setEnabled(False)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        self.progress_label = QLabel()
        self.progress_label.setMinimumWidth(160)
        self.progress_label.setVisible(False)
        self.skip_label = QLabel()
        self.skip_label.setMinimumWidth(120)
        self.skip_label.setVisible(False)

        bottom_bar = QHBoxLayout()
        bottom_bar.addWidget(self.load_button)
        bottom_bar.addWidget(self.save_button)
        bottom_bar.addWidget(self.run_button)
        bottom_bar.addWidget(self.stop_button)
        bottom_bar.addWidget(self.progress_bar)
        bottom_bar.addWidget(self.progress_label)
        bottom_bar.addWidget(self.skip_label)
        bottom_bar.addStretch()
        self.version_label = QLabel(f"v{VERSION}")
        bottom_bar.addWidget(self.version_label)

        right_layout = QVBoxLayout()
        right_layout.addWidget(splitter)
        right_layout.addLayout(bottom_bar)

        central_layout = QHBoxLayout()
        central_layout.addWidget(self.nav_list)
        central_layout.addLayout(right_layout)

        central_widget = QWidget()
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

        self.process = None
        self._pending_config_path = None
        self._output_buffer = ""

        self.nav_list.currentRowChanged.connect(self._on_nav_changed)
        self.run_button.clicked.connect(self._on_run_clicked)
        self.stop_button.clicked.connect(self._on_stop_clicked)
        self.load_button.clicked.connect(self._on_load_clicked)
        self.save_button.clicked.connect(self._on_save_clicked)
        self.save_log_button.clicked.connect(self._on_save_log_clicked)
        self.nav_list.setCurrentRow(0)

        self._log("[Info] YoutubeParser UI 준비 완료")

    def _on_nav_changed(self, index):
        self.pages.setCurrentIndex(index)
        is_api_key_page = self.pages.widget(index) is self.api_key_page
        is_running = self.process is not None
        self.run_button.setEnabled(not is_api_key_page and not is_running)
        self.load_button.setEnabled(not is_api_key_page and not is_running)
        self.save_button.setEnabled(not is_api_key_page and not is_running)

    def _resolve_mode(self, page):
        """Map the current page to (mode key, extra CLI flags) for build_process_args."""
        if isinstance(page, VideoPage):
            return "video", []
        if isinstance(page, BulkPage):
            return "bulk", []
        if isinstance(page, TechCommunityPage):
            return "tech_community", []
        if isinstance(page, InfluencerPage):
            flags = []
            if page.run_channel_check.isChecked():
                flags.append("--yc")
            if page.run_video_check.isChecked():
                flags.append("--yv")
            return "influencer", flags
        return None, []

    def _missing_required_fields(self, mode, config_pairs):
        config = dict(config_pairs)
        return [label for key, label in REQUIRED_FIELDS.get(mode, []) if not config.get(key, "").strip()]

    def _on_run_clicked(self):
        if self.process is not None:
            return
        current_page = self.pages.currentWidget()
        mode, extra_flags = self._resolve_mode(current_page)
        if mode is None:
            return

        mode_name = self.nav_list.currentItem().text()
        try:
            config_pairs = current_page.to_config()
        except Exception as exc:
            self._log(f"[Error] 실행 준비 중 오류가 발생했습니다: {exc}")
            return

        missing = self._missing_required_fields(mode, config_pairs)
        if missing:
            message = "다음 항목을 입력해야 실행할 수 있습니다:\n- " + "\n- ".join(missing)
            self._log(f"[Warning] 실행이 취소되었습니다. 누락된 항목: {', '.join(missing)}")
            QMessageBox.warning(self, "필수 항목 누락", message)
            return

        try:
            program, args, work_dir, config_path = build_process_args(mode, config_pairs, extra_flags)
        except Exception as exc:
            self._log(f"[Error] 실행 준비 중 오류가 발생했습니다: {exc}")
            return

        self._pending_config_path = config_path
        self._output_buffer = ""
        self.progress_bar.setRange(0, 0)
        self.progress_label.setText("")
        self.skip_label.setText("")
        self._log(f"[Info] '{mode_name}' 실행을 시작합니다.")

        self.process = QProcess(self)
        self.process.setProgram(program)
        self.process.setArguments(args)
        self.process.setWorkingDirectory(work_dir)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        env = QProcessEnvironment.systemEnvironment()
        env.insert("PYTHONIOENCODING", "utf-8")
        self.process.setProcessEnvironment(env)
        self.process.readyReadStandardOutput.connect(self._on_process_output)
        self.process.finished.connect(self._on_process_finished)
        self.process.errorOccurred.connect(self._on_process_error)

        self._set_running(True)
        self.process.start()

    def _on_stop_clicked(self):
        if self.process is None:
            return
        self._log("[Warning] 실행 중지를 요청했습니다. (진행 중인 브라우저 작업이 즉시 종료됩니다)")
        self.process.kill()

    def _on_process_output(self):
        if self.process is None:
            return
        data = bytes(self.process.readAllStandardOutput())
        text = data.decode("utf-8", errors="replace")
        # Normalize Windows line endings first so a bare leftover "\r" can only mean
        # an in-place refresh (e.g. tqdm), never a real line ending.
        self._output_buffer += text.replace("\r\n", "\n")

        while True:
            newline_idx = self._output_buffer.find("\n")
            cr_idx = self._output_buffer.find("\r")
            if newline_idx == -1 and cr_idx == -1:
                break
            if cr_idx != -1 and (newline_idx == -1 or cr_idx < newline_idx):
                segment, self._output_buffer = self._output_buffer[:cr_idx], self._output_buffer[cr_idx + 1:]
                self._update_progress(segment)
            else:
                segment, self._output_buffer = self._output_buffer[:newline_idx], self._output_buffer[newline_idx + 1:]
                if not segment.strip():
                    continue
                # tqdm's final refresh on loop close is "\n"-terminated (unlike every
                # earlier "\r" tick) -- route it to the progress UI too, not the log,
                # so it doesn't duplicate what the progress bar/label already show.
                if PROGRESS_RE.search(segment) or SKIP_RE.search(segment):
                    self._update_progress(segment)
                else:
                    self._log(segment)

    def _update_progress(self, text):
        text = text.strip()
        if not text:
            return
        skip_match = SKIP_RE.search(text)
        if skip_match:
            self.skip_label.setText(f"중복 스킵: {skip_match.group(1)}건")
            return
        match = PROGRESS_RE.search(text)
        if match:
            percent, current, total = match.groups()
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(int(percent))
            self.progress_label.setText(f"{current}/{total} ({percent}%)")
        else:
            self.progress_label.setText(text)

    def _flush_output_buffer(self):
        remaining = self._output_buffer.strip()
        self._output_buffer = ""
        if remaining:
            self._log(remaining)

    def _on_process_finished(self, exit_code, exit_status):
        self._flush_output_buffer()
        if exit_code == 0:
            self._log("[Info] 실행이 완료되었습니다.")
        else:
            self._log(f"[Error] 실행이 종료되었습니다 (exit code {exit_code}).")
        self._cleanup_process()

    def _on_process_error(self, error):
        self._log(f"[Error] 프로세스 실행 오류: {error}")

    def _cleanup_process(self):
        if self._pending_config_path:
            try:
                os.remove(self._pending_config_path)
            except OSError:
                pass
            self._pending_config_path = None
        self.process = None
        self._output_buffer = ""
        self._set_running(False)

    def _set_running(self, running):
        self.run_button.setEnabled(not running)
        self.stop_button.setEnabled(running)
        self.load_button.setEnabled(not running)
        self.save_button.setEnabled(not running)
        self.nav_list.setEnabled(not running)
        if running:
            self.progress_bar.setVisible(True)
            self.progress_label.setVisible(True)
            self.skip_label.setVisible(True)

    def _on_load_clicked(self):
        current_page = self.pages.currentWidget()
        path, _ = QFileDialog.getOpenFileName(
            self, "입력 파일 불러오기", "", "Text Files (*.txt);;All Files (*)"
        )
        if not path:
            return
        try:
            config = read_key_value_txt(path)
        except OSError as exc:
            self._log(f"[Error] 입력 파일을 읽지 못했습니다: {exc}")
            return
        current_page.from_config(config)
        self._log(f"[Info] 입력 파일을 불러왔습니다: {path}")

    def _on_save_clicked(self):
        current_page = self.pages.currentWidget()
        path, _ = QFileDialog.getSaveFileName(
            self, "입력 파일로 저장", "", "Text Files (*.txt);;All Files (*)"
        )
        if not path:
            return
        try:
            write_key_value_txt(path, current_page.to_config())
        except OSError as exc:
            self._log(f"[Error] 입력 파일을 저장하지 못했습니다: {exc}")
            return
        self._log(f"[Info] 입력 파일로 저장했습니다: {path}")

    def _on_save_log_clicked(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "로그 저장", "log.txt", "Text Files (*.txt);;All Files (*)"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8-sig") as f:
                f.write(self.log_console.toPlainText())
        except OSError as exc:
            self._log(f"[Error] 로그를 저장하지 못했습니다: {exc}")
            return
        self._log(f"[Info] 로그를 저장했습니다: {path}")

    def _log(self, message):
        self.log_console.appendPlainText(message)
