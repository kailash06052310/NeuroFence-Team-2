"""
NeuroFence Desktop UI
Compatible with NeuroFence Backend

Author:
Prithvi UI + Kailash Backend Integration

Features:
- Non-blocking model loading
- Background analysis using QThread
- Progress bar
- Risk / Verdict / Confidence cards
- Layer statistics
- Neuron activation heatmap
- Dark / Light mode
- PDF report opening
- Safe thread cleanup
"""

import sys
import os
import re
import subprocess
import webbrowser

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFrame,
    QProgressBar,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
)

from PyQt6.QtCore import Qt, QObject, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QBrush

from model_loader import ModelLoader
from main import main


# ==========================================================
# MODEL LOADER WORKER
# ==========================================================

class ModelLoaderWorker(QObject):

    finished = pyqtSignal()
    loaded = pyqtSignal(object, object, str)
    error = pyqtSignal(str)

    def run(self):
        try:
            loader = ModelLoader()
            model, tokenizer = loader.load_model()

            model_name = getattr(
                loader,
                "model_name",
                "Hugging Face Model"
            )

            self.loaded.emit(
                model,
                tokenizer,
                model_name
            )

        except Exception as e:
            self.error.emit(str(e))

        finally:
            self.finished.emit()


# ==========================================================
# ANALYSIS WORKER
# ==========================================================

class AnalysisWorker(QObject):

    finished = pyqtSignal()
    log_signal = pyqtSignal(str)

    def __init__(self, model, tokenizer):
        super().__init__()
        self.model = model
        self.tokenizer = tokenizer

    def run(self):

        try:
            main(
                model=self.model,
                tokenizer=self.tokenizer,
                log_callback=self.log_signal.emit
            )

        except Exception as e:
            self.log_signal.emit(
                f"\n[ERROR] {e}"
            )

        finally:
            self.finished.emit()


# ==========================================================
# MAIN WINDOW
# ==========================================================

class NeuroFenceApp(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "NeuroFence - LLM Forensic & Security Suite"
        )

        self.setMinimumSize(1050, 760)
        self.resize(1150, 820)

        # --------------------------------------------------
        # Application State
        # --------------------------------------------------

        self.loader = None

        self.model = None
        self.tokenizer = None

        self.model_loaded = False

        self.is_dark = True

        # Analysis thread references
        self.thread = None
        self.worker = None

        # Model loading thread references
        self.load_thread = None
        self.load_worker = None

        self.analysis_running = False
        self.loading_model = False

        # Result state
        self.latest_risk = None
        self.latest_verdict = "Waiting"
        self.latest_confidence = None
        self.latest_avg_diff = None
        self.latest_max_diff = None
        self.latest_high_layers = None
        self.latest_total_layers = None

        # --------------------------------------------------
        # Central Widget
        # --------------------------------------------------

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        # --------------------------------------------------
        # Header
        # --------------------------------------------------

        header = QHBoxLayout()

        title_box = QVBoxLayout()
        title_box.setSpacing(2)

        self.title = QLabel(
            "🚀 NeuroFence Forensic Security Dashboard"
        )
        self.title.setObjectName("titleLabel")

        self.subtitle = QLabel(
            "LLM Hidden-Activation Security Analysis"
        )
        self.subtitle.setObjectName("subtitleLabel")

        title_box.addWidget(self.title)
        title_box.addWidget(self.subtitle)

        header.addLayout(title_box)
        header.addStretch()

        self.theme_button = QPushButton(
            "☀️ Light Mode"
        )
        self.theme_button.setFixedWidth(135)

        self.theme_button.clicked.connect(
            self.toggle_theme
        )

        header.addWidget(
            self.theme_button
        )

        layout.addLayout(header)

        # --------------------------------------------------
        # Control Buttons
        # --------------------------------------------------

        buttons = QHBoxLayout()
        buttons.setSpacing(10)

        self.load_button = QPushButton(
            "📁 Load Model"
        )

        self.run_button = QPushButton(
            "🔍 Run Analysis"
        )

        self.report_button = QPushButton(
            "📄 Open PDF Report"
        )

        self.run_button.setEnabled(False)

        self.load_button.clicked.connect(
            self.load_model_action
        )

        self.run_button.clicked.connect(
            self.run_analysis_action
        )

        self.report_button.clicked.connect(
            self.report_action
        )

        buttons.addWidget(self.load_button)
        buttons.addWidget(self.run_button)
        buttons.addWidget(self.report_button)
        buttons.addStretch()

        layout.addLayout(buttons)

        # --------------------------------------------------
        # Progress Section
        # --------------------------------------------------

        progress_frame = QFrame()
        progress_frame.setObjectName("panel")

        progress_layout = QVBoxLayout(
            progress_frame
        )

        progress_layout.setContentsMargins(
            14, 10, 14, 10
        )

        progress_header = QHBoxLayout()

        self.progress_label = QLabel("Ready")
        self.progress_label.setObjectName(
            "sectionLabel"
        )

        self.progress_value = QLabel("0%")
        self.progress_value.setObjectName(
            "progressValue"
        )

        progress_header.addWidget(
            self.progress_label
        )

        progress_header.addStretch()

        progress_header.addWidget(
            self.progress_value
        )

        progress_layout.addLayout(
            progress_header
        )

        self.progress_bar = QProgressBar()

        self.progress_bar.setRange(
            0, 100
        )

        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(12)

        progress_layout.addWidget(
            self.progress_bar
        )

        layout.addWidget(
            progress_frame
        )

        # --------------------------------------------------
        # Risk Cards
        # --------------------------------------------------

        cards = QGridLayout()
        cards.setSpacing(10)

        self.risk_card = self.create_card(
            "Risk Score",
            "--",
            "risk"
        )

        self.verdict_card = self.create_card(
            "Verdict",
            "Waiting",
            "verdict"
        )

        self.confidence_card = self.create_card(
            "Confidence",
            "--",
            "confidence"
        )

        self.high_layers_card = self.create_card(
            "High-Risk Layers",
            "--",
            "layers"
        )

        cards.addWidget(
            self.risk_card, 0, 0
        )

        cards.addWidget(
            self.verdict_card, 0, 1
        )

        cards.addWidget(
            self.confidence_card, 0, 2
        )

        cards.addWidget(
            self.high_layers_card, 0, 3
        )

        layout.addLayout(cards)

        # --------------------------------------------------
        # Statistics Cards
        # --------------------------------------------------

        stats = QGridLayout()
        stats.setSpacing(10)

        self.average_card = self.create_card(
            "Average Difference",
            "--",
            "stat"
        )

        self.maximum_card = self.create_card(
            "Maximum Difference",
            "--",
            "stat"
        )

        self.total_layers_card = self.create_card(
            "Total Layers",
            "--",
            "stat"
        )

        self.status_card = self.create_card(
            "System Status",
            "Ready",
            "status"
        )

        stats.addWidget(
            self.average_card, 0, 0
        )

        stats.addWidget(
            self.maximum_card, 0, 1
        )

        stats.addWidget(
            self.total_layers_card, 0, 2
        )

        stats.addWidget(
            self.status_card, 0, 3
        )

        layout.addLayout(stats)

        # --------------------------------------------------
        # Heatmap
        # --------------------------------------------------

        heatmap_frame = QFrame()
        heatmap_frame.setObjectName("panel")

        heatmap_layout = QVBoxLayout(
            heatmap_frame
        )

        heatmap_layout.setContentsMargins(
            12, 10, 12, 10
        )

        heatmap_header = QHBoxLayout()

        heatmap_title = QLabel(
            "🧠 Neuron Activation Heatmap"
        )
        heatmap_title.setObjectName(
            "sectionLabel"
        )

        self.heatmap_info = QLabel(
            "Waiting for analysis..."
        )
        self.heatmap_info.setObjectName(
            "mutedLabel"
        )

        heatmap_header.addWidget(
            heatmap_title
        )

        heatmap_header.addStretch()

        heatmap_header.addWidget(
            self.heatmap_info
        )

        heatmap_layout.addLayout(
            heatmap_header
        )

        self.heatmap = QTableWidget()

        self.heatmap.setColumnCount(3)

        self.heatmap.setHorizontalHeaderLabels(
            [
                "Layer",
                "Normalized Activity",
                "Activity Level",
            ]
        )

        self.heatmap.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.heatmap.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.heatmap.setAlternatingRowColors(
            True
        )

        self.heatmap.verticalHeader().setVisible(
            False
        )

        header_view = (
            self.heatmap.horizontalHeader()
        )

        header_view.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents
        )

        header_view.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch
        )

        header_view.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.ResizeToContents
        )

        self.heatmap.setMinimumHeight(220)

        heatmap_layout.addWidget(
            self.heatmap
        )

        # --------------------------------------------------
        # Heatmap Legend
        # --------------------------------------------------

        legend = QHBoxLayout()

        legend_title = QLabel("Legend:")
        legend_title.setObjectName(
            "mutedLabel"
        )

        legend.addWidget(
            legend_title
        )

        for text, color in [
            ("Low", "#22C55E"),
            ("Moderate", "#EAB308"),
            ("High", "#F97316"),
            ("Critical", "#EF4444"),
        ]:

            label = QLabel(
                f"  {text}  "
            )

            label.setStyleSheet(
                f"""
                QLabel {{
                    background: {color};
                    color: #111827;
                    border-radius: 5px;
                    padding: 3px 7px;
                    font-weight: bold;
                }}
                """
            )

            legend.addWidget(
                label
            )

        legend.addStretch()

        heatmap_layout.addLayout(
            legend
        )

        layout.addWidget(
            heatmap_frame,
            2
        )

        # --------------------------------------------------
        # Execution Log
        # --------------------------------------------------

        console_title = QLabel(
            "Execution Log"
        )

        console_title.setObjectName(
            "sectionLabel"
        )

        layout.addWidget(
            console_title
        )

        self.console = QTextEdit()

        self.console.setReadOnly(True)

        self.console.setPlaceholderText(
            "Execution logs and analysis results "
            "will appear here..."
        )

        self.console.setMinimumHeight(150)

        layout.addWidget(
            self.console,
            1
        )

        self.apply_dark_theme()

    # ======================================================
    # CARD HELPERS
    # ======================================================

    def create_card(
        self,
        title,
        value,
        kind="stat"
    ):

        card = QFrame()

        card.setObjectName(
            "card"
        )

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            12, 10, 12, 10
        )

        layout.setSpacing(4)

        title_label = QLabel(
            title
        )

        title_label.setObjectName(
            "cardTitle"
        )

        value_label = QLabel(
            value
        )

        value_label.setObjectName(
            f"cardValue_{kind}"
        )

        value_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(
            title_label
        )

        layout.addWidget(
            value_label
        )

        card.value_label = value_label

        return card

    def set_card_value(
        self,
        card,
        value
    ):

        card.value_label.setText(
            str(value)
        )

    # ======================================================
    # THEME
    # ======================================================

    def toggle_theme(self):

        if self.is_dark:

            self.apply_light_theme()

            self.theme_button.setText(
                "🌙 Dark Mode"
            )

            self.is_dark = False

        else:

            self.apply_dark_theme()

            self.theme_button.setText(
                "☀️ Light Mode"
            )

            self.is_dark = True

        self.refresh_heatmap_styles()

    def apply_dark_theme(self):

        self.setStyleSheet("""
            QMainWindow {
                background: #0F172A;
            }

            QLabel#titleLabel {
                color: #38BDF8;
                font-size: 24px;
                font-weight: bold;
            }

            QLabel#subtitleLabel {
                color: #94A3B8;
                font-size: 13px;
            }

            QLabel#sectionLabel {
                color: #38BDF8;
                font-size: 15px;
                font-weight: bold;
            }

            QLabel#mutedLabel {
                color: #94A3B8;
                font-size: 12px;
            }

            QLabel#progressValue {
                color: #38BDF8;
                font-weight: bold;
            }

            QPushButton {
                background: #1E293B;
                color: #38BDF8;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 9px 14px;
                font-weight: bold;
            }

            QPushButton:hover {
                background: #334155;
            }

            QPushButton:disabled {
                color: #64748B;
                background: #172033;
            }

            QFrame#panel {
                background: #111C31;
                border: 1px solid #334155;
                border-radius: 8px;
            }

            QFrame#card {
                background: #1E293B;
                border: 1px solid #334155;
                border-radius: 9px;
                min-height: 78px;
            }

            QLabel#cardTitle {
                color: #94A3B8;
                font-size: 11px;
                font-weight: bold;
            }

            QLabel#cardValue_risk {
                color: #F8FAFC;
                font-size: 22px;
                font-weight: bold;
            }

            QLabel#cardValue_verdict {
                color: #F8FAFC;
                font-size: 18px;
                font-weight: bold;
            }

            QLabel#cardValue_confidence,
            QLabel#cardValue_layers,
            QLabel#cardValue_stat,
            QLabel#cardValue_status {
                color: #38BDF8;
                font-size: 19px;
                font-weight: bold;
            }

            QProgressBar {
                background: #020617;
                border: 1px solid #334155;
                border-radius: 6px;
            }

            QProgressBar::chunk {
                background: #38BDF8;
                border-radius: 5px;
            }

            QTableWidget {
                background: #020617;
                alternate-background-color: #0B1220;
                color: #E2E8F0;
                border: 1px solid #334155;
                gridline-color: #334155;
                selection-background-color: #1E3A5F;
            }

            QHeaderView::section {
                background: #1E293B;
                color: #38BDF8;
                padding: 7px;
                border: 1px solid #334155;
                font-weight: bold;
            }

            QTextEdit {
                background: #020617;
                color: #38BDF8;
                border: 1px solid #334155;
                border-radius: 6px;
                font-family: Consolas, monospace;
                font-size: 12px;
                padding: 8px;
            }
        """)

    def apply_light_theme(self):

        self.setStyleSheet("""
            QMainWindow {
                background: #F8FAFC;
            }

            QLabel#titleLabel {
                color: #0369A1;
                font-size: 24px;
                font-weight: bold;
            }

            QLabel#subtitleLabel {
                color: #64748B;
                font-size: 13px;
            }

            QLabel#sectionLabel {
                color: #0369A1;
                font-size: 15px;
                font-weight: bold;
            }

            QLabel#mutedLabel {
                color: #64748B;
                font-size: 12px;
            }

            QLabel#progressValue {
                color: #0369A1;
                font-weight: bold;
            }

            QPushButton {
                background: #FFFFFF;
                color: #0369A1;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 9px 14px;
                font-weight: bold;
            }

            QPushButton:hover {
                background: #E2E8F0;
            }

            QPushButton:disabled {
                color: #94A3B8;
                background: #E2E8F0;
            }

            QFrame#panel {
                background: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
            }

            QFrame#card {
                background: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 9px;
                min-height: 78px;
            }

            QLabel#cardTitle {
                color: #64748B;
                font-size: 11px;
                font-weight: bold;
            }

            QLabel#cardValue_risk,
            QLabel#cardValue_verdict {
                color: #0F172A;
                font-size: 20px;
                font-weight: bold;
            }

            QLabel#cardValue_confidence,
            QLabel#cardValue_layers,
            QLabel#cardValue_stat,
            QLabel#cardValue_status {
                color: #0369A1;
                font-size: 19px;
                font-weight: bold;
            }

            QProgressBar {
                background: #E2E8F0;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
            }

            QProgressBar::chunk {
                background: #0284C7;
                border-radius: 5px;
            }

            QTableWidget {
                background: #FFFFFF;
                alternate-background-color: #F8FAFC;
                color: #0F172A;
                border: 1px solid #CBD5E1;
                gridline-color: #CBD5E1;
                selection-background-color: #DBEAFE;
            }

            QHeaderView::section {
                background: #E2E8F0;
                color: #0369A1;
                padding: 7px;
                border: 1px solid #CBD5E1;
                font-weight: bold;
            }

            QTextEdit {
                background: #FFFFFF;
                color: #0F172A;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                font-family: Consolas, monospace;
                font-size: 12px;
                padding: 8px;
            }
        """)

    # ======================================================
    # MODEL LOADING
    # ======================================================

    def load_model_action(self):

        if self.analysis_running or self.loading_model:
            return

        self.loading_model = True
        self.model_loaded = False

        self.load_button.setEnabled(False)
        self.run_button.setEnabled(False)
        self.report_button.setEnabled(False)

        self.console.append(
            "\n[STATUS] Loading Hugging Face Model..."
        )

        self.progress_label.setText(
            "Loading model..."
        )

        self.set_progress(5)

        self.status_card_value(
            "Loading"
        )

        self.load_thread = QThread()
        self.load_worker = ModelLoaderWorker()

        self.load_worker.moveToThread(
            self.load_thread
        )

        self.load_thread.started.connect(
            self.load_worker.run
        )

        self.load_worker.loaded.connect(
            self.model_loaded_success
        )

        self.load_worker.error.connect(
            self.model_load_error
        )

        self.load_worker.finished.connect(
            self.load_thread.quit
        )

        self.load_worker.finished.connect(
            self.load_worker.deleteLater
        )

        self.load_thread.finished.connect(
            self.model_loading_finished
        )

        self.load_thread.finished.connect(
            self.load_thread.deleteLater
        )

        self.load_thread.start()

    def model_loaded_success(
        self,
        model,
        tokenizer,
        model_name
    ):

        self.model = model
        self.tokenizer = tokenizer

        self.model_loaded = True

        self.set_progress(100)

        self.progress_label.setText(
            "Model loaded successfully"
        )

        self.status_card_value(
            "Model Ready"
        )

        self.console.append(
            f"[SUCCESS] Model Loaded Successfully: "
            f"{model_name}\n"
        )

    def model_load_error(self, message):

        self.model_loaded = False

        self.set_progress(0)

        self.progress_label.setText(
            "Model loading failed"
        )

        self.status_card_value(
            "Error"
        )

        self.console.append(
            f"[ERROR] {message}\n"
        )

    def model_loading_finished(self):

        self.loading_model = False

        self.load_thread = None
        self.load_worker = None

        self.load_button.setEnabled(True)
        self.report_button.setEnabled(True)

        if self.model_loaded:
            self.run_button.setEnabled(True)

    # ======================================================
    # RUN ANALYSIS
    # ======================================================

    def run_analysis_action(self):

        if not self.model_loaded:

            self.console.append(
                "\n[WARNING] Please load the model first!\n"
            )

            return

        if (
            self.analysis_running
            or self.loading_model
        ):
            return

        self.analysis_running = True

        self.run_button.setEnabled(False)
        self.load_button.setEnabled(False)
        self.report_button.setEnabled(False)

        self.reset_result_cards()
        self.clear_heatmap()

        self.console.append(
            "\n[STATUS] Starting NeuroFence Analysis...\n"
        )

        self.progress_label.setText(
            "Running analysis..."
        )

        self.set_progress(5)

        self.status_card_value(
            "Analyzing"
        )

        self.thread = QThread()
        self.worker = AnalysisWorker(
            self.model,
            self.tokenizer
        )

        self.worker.moveToThread(
            self.thread
        )

        self.thread.started.connect(
            self.worker.run
        )

        self.worker.log_signal.connect(
            self.handle_backend_log
        )

        # IMPORTANT:
        # Do not set self.thread/self.worker to None here.
        # QThread must be allowed to finish before its
        # Python/Qt objects are released.
        self.worker.finished.connect(
            self.thread.quit
        )

        self.worker.finished.connect(
            self.worker.deleteLater
        )

        self.thread.finished.connect(
            self.analysis_thread_finished
        )

        self.thread.finished.connect(
            self.thread.deleteLater
        )

        self.thread.start()

    # ======================================================
    # BACKEND LOG PROCESSING
    # ======================================================

    def handle_backend_log(self, message):

        text = str(message)

        self.console.append(
            text
        )

        lower = text.lower()

        if "creating average baseline" in lower:

            self.set_progress(15)

            self.progress_label.setText(
                "Creating activation baseline..."
            )

        elif "average baseline created" in lower:

            self.set_progress(30)

            self.progress_label.setText(
                "Baseline created"
            )

        elif "testing adversarial prompts" in lower:

            self.set_progress(40)

            self.progress_label.setText(
                "Testing adversarial prompts..."
            )

        elif "detection result" in lower:

            self.set_progress(
                max(
                    self.progress_bar.value(),
                    65
                )
            )

            self.progress_label.setText(
                "Processing detection results..."
            )

        elif "neuron visualization" in lower:

            self.set_progress(
                max(
                    self.progress_bar.value(),
                    75
                )
            )

        elif "json report saved" in lower:

            self.set_progress(
                max(
                    self.progress_bar.value(),
                    88
                )
            )

            self.progress_label.setText(
                "Saving JSON report..."
            )

        elif "pdf report generated" in lower:

            self.set_progress(
                max(
                    self.progress_bar.value(),
                    95
                )
            )

            self.progress_label.setText(
                "Generating PDF report..."
            )

        elif "neurofence analysis completed" in lower:

            self.set_progress(100)

            self.progress_label.setText(
                "Analysis completed"
            )

        self.parse_detection_data(
            text
        )

        self.parse_heatmap_data(
            text
        )

    # ======================================================
    # DETECTION DATA
    # ======================================================

    def parse_detection_data(
        self,
        text
    ):

        patterns = [
            (
                r"Risk Score\s*:\s*"
                r"([-+]?\d*\.?\d+)",
                "risk"
            ),
            (
                r"Confidence\s*:\s*"
                r"([-+]?\d*\.?\d+)",
                "confidence"
            ),
            (
                r"Avg Diff\s*:\s*"
                r"([-+]?\d*\.?\d+)",
                "avg"
            ),
            (
                r"Max Diff\s*:\s*"
                r"([-+]?\d*\.?\d+)",
                "max"
            ),
            (
                r"High Layers:\s*"
                r"(\d+)\s*/\s*(\d+)",
                "layers"
            ),
            (
                r"Verdict\s*:\s*(.+)",
                "verdict"
            ),
        ]

        for pattern, field in patterns:

            match = re.search(
                pattern,
                text,
                flags=re.IGNORECASE
            )

            if not match:
                continue

            try:

                if field == "risk":

                    self.latest_risk = float(
                        match.group(1)
                    )

                    self.set_card_value(
                        self.risk_card,
                        self.format_number(
                            self.latest_risk
                        )
                    )

                    self.update_risk_card_style()

                elif field == "confidence":

                    self.latest_confidence = float(
                        match.group(1)
                    )

                    self.set_card_value(
                        self.confidence_card,
                        (
                            f"{self.format_number(self.latest_confidence)}%"
                        )
                    )

                elif field == "avg":

                    self.latest_avg_diff = float(
                        match.group(1)
                    )

                    self.set_card_value(
                        self.average_card,
                        self.format_number(
                            self.latest_avg_diff
                        )
                    )

                elif field == "max":

                    self.latest_max_diff = float(
                        match.group(1)
                    )

                    self.set_card_value(
                        self.maximum_card,
                        self.format_number(
                            self.latest_max_diff
                        )
                    )

                elif field == "layers":

                    self.latest_high_layers = int(
                        match.group(1)
                    )

                    self.latest_total_layers = int(
                        match.group(2)
                    )

                    self.set_card_value(
                        self.high_layers_card,
                        (
                            f"{self.latest_high_layers} / "
                            f"{self.latest_total_layers}"
                        )
                    )

                    self.set_card_value(
                        self.total_layers_card,
                        str(
                            self.latest_total_layers
                        )
                    )

                elif field == "verdict":

                    self.latest_verdict = (
                        match.group(1).strip()
                    )

                    self.set_card_value(
                        self.verdict_card,
                        self.latest_verdict
                    )

                    self.update_verdict_card_style()

            except (
                ValueError,
                TypeError
            ):
                continue

    # ======================================================
    # HEATMAP LOG PARSER
    # ======================================================

    def parse_heatmap_data(
        self,
        text
    ):

        match = re.search(
            r"^\s*"
            r"(Layer[_\s-]*\d+)"
            r"\s*\|\s*"
            r"([-+]?\d*\.?\d+)"
            r"\s*\|\s*"
            r"(green|yellow|orange|red)"
            r"\s*$",
            text,
            flags=re.IGNORECASE
        )

        if not match:
            return

        layer = (
            match.group(1)
            .replace(" ", "_")
        )

        activity = float(
            match.group(2)
        )

        color = match.group(3).lower()

        self.add_heatmap_row(
            layer,
            activity,
            color
        )

    # ======================================================
    # HEATMAP
    # ======================================================

    def add_heatmap_row(
        self,
        layer,
        activity,
        color
    ):

        row = -1

        for current_row in range(
            self.heatmap.rowCount()
        ):

            item = self.heatmap.item(
                current_row,
                0
            )

            if (
                item
                and item.text() == layer
            ):

                row = current_row
                break

        if row < 0:

            row = (
                self.heatmap.rowCount()
            )

            self.heatmap.insertRow(
                row
            )

        items = [
            QTableWidgetItem(
                layer
            ),
            QTableWidgetItem(
                f"{activity:.4f}"
            ),
            QTableWidgetItem(
                self.activity_label(
                    activity
                )
            ),
        ]

        items[1].setTextAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        items[2].setTextAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        brush = QBrush(
            self.color_for_activity(
                color
            )
        )

        for item in items:

            item.setBackground(
                brush
            )

            item.setForeground(
                QBrush(
                    QColor("#111827")
                )
            )

            font = item.font()
            font.setBold(True)
            item.setFont(font)

        for column, item in enumerate(
            items
        ):

            self.heatmap.setItem(
                row,
                column,
                item
            )

        self.heatmap_info.setText(
            f"{self.heatmap.rowCount()} "
            f"layers captured"
        )

    def refresh_heatmap_styles(self):

        for row in range(
            self.heatmap.rowCount()
        ):

            item = self.heatmap.item(
                row,
                1
            )

            if not item:
                continue

            try:

                activity = float(
                    item.text()
                )

            except ValueError:
                continue

            brush = QBrush(
                self.color_for_activity(
                    self.activity_color(
                        activity
                    )
                )
            )

            for column in (1, 2):

                cell = self.heatmap.item(
                    row,
                    column
                )

                if cell:

                    cell.setBackground(
                        brush
                    )

                    cell.setForeground(
                        QBrush(
                            QColor("#111827")
                        )
                    )

    def clear_heatmap(self):

        self.heatmap.setRowCount(0)

        self.heatmap_info.setText(
            "Waiting for analysis..."
        )

    @staticmethod
    def activity_color(
        activity
    ):

        if activity < 0.25:
            return "green"

        if activity < 0.50:
            return "yellow"

        if activity < 0.75:
            return "orange"

        return "red"

    @staticmethod
    def activity_label(
        activity
    ):

        if activity < 0.25:
            return "LOW"

        if activity < 0.50:
            return "MODERATE"

        if activity < 0.75:
            return "HIGH"

        return "CRITICAL"

    @staticmethod
    def color_for_activity(
        color
    ):

        colors = {
            "green": QColor("#22C55E"),
            "yellow": QColor("#EAB308"),
            "orange": QColor("#F97316"),
            "red": QColor("#EF4444"),
        }

        return colors.get(
            color.lower(),
            QColor("#94A3B8")
        )

    # ======================================================
    # RESULT CARDS
    # ======================================================

    def reset_result_cards(self):

        self.latest_risk = None
        self.latest_verdict = "Analyzing"
        self.latest_confidence = None
        self.latest_avg_diff = None
        self.latest_max_diff = None
        self.latest_high_layers = None
        self.latest_total_layers = None

        values = [
            (self.risk_card, "--"),
            (self.verdict_card, "Analyzing"),
            (self.confidence_card, "--"),
            (self.high_layers_card, "--"),
            (self.average_card, "--"),
            (self.maximum_card, "--"),
            (self.total_layers_card, "--"),
        ]

        for card, value in values:

            self.set_card_value(
                card,
                value
            )

        self.update_risk_card_style()
        self.update_verdict_card_style()

    def update_risk_card_style(self):

        if self.latest_risk is None:

            color = "#38BDF8"

        elif self.latest_risk >= 75:

            color = "#EF4444"

        elif self.latest_risk >= 50:

            color = "#F97316"

        elif self.latest_risk >= 25:

            color = "#EAB308"

        else:

            color = "#22C55E"

        self.risk_card.value_label.setStyleSheet(
            f"""
            color: {color};
            font-size: 22px;
            font-weight: bold;
            """
        )

    def update_verdict_card_style(self):

        verdict = (
            self.latest_verdict
            or ""
        ).lower()

        if "high" in verdict:

            color = "#EF4444"

        elif "suspicious" in verdict:

            color = "#F97316"

        elif "safe" in verdict:

            color = "#22C55E"

        else:

            color = "#38BDF8"

        self.verdict_card.value_label.setStyleSheet(
            f"""
            color: {color};
            font-size: 18px;
            font-weight: bold;
            """
        )

    def status_card_value(
        self,
        value
    ):

        self.set_card_value(
            self.status_card,
            value
        )

    # ======================================================
    # ANALYSIS THREAD FINISHED
    # ======================================================

    def analysis_thread_finished(self):

        # This method is called only after QThread has
        # actually stopped. This prevents the
        # "QThread: Destroyed while thread is still running"
        # error.

        self.analysis_running = False

        self.set_progress(100)

        self.progress_label.setText(
            "Analysis completed"
        )

        self.status_card_value(
            "Completed"
        )

        self.console.append(
            "\n[SUCCESS] NeuroFence Analysis Completed."
        )

        self.console.append(
            "[SUCCESS] JSON Report Saved."
        )

        self.console.append(
            "[SUCCESS] PDF Report Generated.\n"
        )

        self.run_button.setEnabled(
            self.model_loaded
        )

        self.load_button.setEnabled(
            True
        )

        self.report_button.setEnabled(
            True
        )

        # Only now release the Python references.
        self.thread = None
        self.worker = None

    # ======================================================
    # REPORT
    # ======================================================

    def report_action(self):

        base = os.path.dirname(
            os.path.abspath(__file__)
        )

        paths = [
            os.path.join(
                os.getcwd(),
                "Security_Report.pdf"
            ),
            os.path.join(
                base,
                "Security_Report.pdf"
            ),
            os.path.abspath(
                os.path.join(
                    base,
                    "..",
                    "Security_Report.pdf"
                )
            ),
        ]

        pdf = next(
            (
                os.path.abspath(path)
                for path in paths
                if os.path.exists(
                    os.path.abspath(path)
                )
            ),
            None
        )

        if not pdf:

            self.console.append(
                "\n[INFO] Please run analysis first."
            )

            return

        self.console.append(
            "\n[SUCCESS] Opening Security_Report.pdf..."
        )

        try:

            if sys.platform.startswith(
                "win"
            ):

                os.startfile(pdf)

            elif sys.platform == "darwin":

                subprocess.Popen(
                    ["open", pdf]
                )

            else:

                subprocess.Popen(
                    ["xdg-open", pdf]
                )

        except Exception:

            webbrowser.open(
                "file://" + pdf
            )

    # ======================================================
    # PROGRESS
    # ======================================================

    def set_progress(
        self,
        value
    ):

        value = max(
            0,
            min(
                100,
                int(value)
            )
        )

        self.progress_bar.setValue(
            value
        )

        self.progress_value.setText(
            f"{value}%"
        )

    # ======================================================
    # FORMATTING
    # ======================================================

    @staticmethod
    def format_number(
        value
    ):

        if value is None:
            return "--"

        if abs(value) >= 100:
            return f"{value:.1f}"

        return f"{value:.2f}"

    # ======================================================
    # CLOSE EVENT
    # ======================================================

    def closeEvent(
        self,
        event
    ):

        if (
            self.analysis_running
            or self.loading_model
        ):

            reply = QMessageBox.question(
                self,
                "Operation Running",
                (
                    "A NeuroFence operation is still running.\n\n"
                    "Do you really want to close the application?"
                ),
                (
                    QMessageBox.StandardButton.Yes
                    | QMessageBox.StandardButton.No
                ),
                QMessageBox.StandardButton.No,
            )

            if (
                reply
                == QMessageBox.StandardButton.No
            ):

                event.ignore()
                return

        event.accept()


# ==========================================================
# APPLICATION ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = NeuroFenceApp()

    window.show()

    sys.exit(
        app.exec()
    )