# NeuroFence Forensic Desktop UI Application

import sys
import os

# --------------------------------------------------
# Path Setup
# --------------------------------------------------

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)


# --------------------------------------------------
# PyQt6 Imports
# --------------------------------------------------

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QTextEdit
)

from PyQt6.QtCore import Qt


# --------------------------------------------------
# NeuroFence Imports
# --------------------------------------------------

from analyzer import Analyzer
from pdf_report import PDFReportGenerator


# --------------------------------------------------
# Main Application
# --------------------------------------------------

class NeuroFenceApp(QMainWindow):

    def __init__(self):

        super().__init__()

        # Window settings
        self.setWindowTitle(
            "NeuroFence - LLM Forensic & Security Suite v1.0"
        )

        self.setGeometry(
            100,
            100,
            850,
            580
        )

        # Application state
        self.is_dark_mode = True
        self.analyzer = None
        self.latest_analysis_results = None

        # --------------------------------------------------
        # Central Widget
        # --------------------------------------------------

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()

        # --------------------------------------------------
        # Header
        # --------------------------------------------------

        header_layout = QHBoxLayout()

        self.title_label = QLabel(
            "🚀 NeuroFence Forensic Desktop Dashboard"
        )

        self.title_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft |
            Qt.AlignmentFlag.AlignVCenter
        )

        self.btn_theme = QPushButton(
            "☀️ Light Mode"
        )

        self.btn_theme.setFixedWidth(130)

        self.btn_theme.clicked.connect(
            self.toggle_theme
        )

        header_layout.addWidget(
            self.title_label
        )

        header_layout.addStretch()

        header_layout.addWidget(
            self.btn_theme
        )

        main_layout.addLayout(
            header_layout
        )

        # --------------------------------------------------
        # Control Buttons
        # --------------------------------------------------

        btn_layout = QHBoxLayout()

        self.btn_load = QPushButton(
            "📁 Load Model"
        )

        self.btn_analyze = QPushButton(
            "🔍 Run Forensic Analysis"
        )

        self.btn_report = QPushButton(
            "📄 Generate PDF Report"
        )

        btn_layout.addWidget(
            self.btn_load
        )

        btn_layout.addWidget(
            self.btn_analyze
        )

        btn_layout.addWidget(
            self.btn_report
        )

        main_layout.addLayout(
            btn_layout
        )

        # --------------------------------------------------
        # Result / Log Area
        # --------------------------------------------------

        self.result_area = QTextEdit()

        self.result_area.setReadOnly(
            True
        )

        self.result_area.setPlaceholderText(
            "Execution logs and analysis results will appear here..."
        )

        main_layout.addWidget(
            self.result_area
        )

        # --------------------------------------------------
        # Button Connections
        # --------------------------------------------------

        self.btn_load.clicked.connect(
            self.load_model_action
        )

        self.btn_analyze.clicked.connect(
            self.run_analysis_action
        )

        self.btn_report.clicked.connect(
            self.generate_report_action
        )

        central_widget.setLayout(
            main_layout
        )

        # Initial theme
        self.apply_dark_theme()


    # ==================================================
    # Theme
    # ==================================================

    def toggle_theme(self):

        if self.is_dark_mode:

            self.apply_light_theme()

            self.btn_theme.setText(
                "🌙 Dark Mode"
            )

            self.is_dark_mode = False

        else:

            self.apply_dark_theme()

            self.btn_theme.setText(
                "☀️ Light Mode"
            )

            self.is_dark_mode = True


    def apply_dark_theme(self):

        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #0F172A;
            }

            QLabel {
                color: #38BDF8;
                font-size: 20px;
                font-weight: bold;
            }

            QPushButton {
                background-color: #1E293B;
                color: #38BDF8;
                border: 1px solid #334155;
                border-radius: 6px;
                font-size: 13px;
                padding: 8px 12px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #334155;
                color: #7DD3FC;
            }

            QTextEdit {
                background-color: #020617;
                color: #38BDF8;
                border: 1px solid #1E293B;
                border-radius: 6px;
                font-family: 'Consolas', monospace;
                font-size: 13px;
                padding: 10px;
            }
            """
        )


    def apply_light_theme(self):

        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #F8FAFC;
            }

            QLabel {
                color: #0F172A;
                font-size: 20px;
                font-weight: bold;
            }

            QPushButton {
                background-color: #FFFFFF;
                color: #0284C7;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                font-size: 13px;
                padding: 8px 12px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #E2E8F0;
                color: #0369A1;
            }

            QTextEdit {
                background-color: #FFFFFF;
                color: #0F172A;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                font-family: 'Consolas', monospace;
                font-size: 13px;
                padding: 10px;
            }
            """
        )


    # ==================================================
    # Load / Initialize Analyzer
    # ==================================================

    def load_model_action(self):

        self.result_area.append(
            "\n[STATUS] Initializing NeuroFence Analyzer..."
        )

        try:

            self.analyzer = Analyzer()

            self.result_area.append(
                "[SUCCESS] NeuroFence Analyzer initialized successfully!\n"
            )

        except Exception as e:

            self.result_area.append(
                f"[ERROR] Failed to initialize analyzer: {str(e)}\n"
            )


    # ==================================================
    # Run Forensic Analysis
    # ==================================================

    def run_analysis_action(self):

        self.result_area.append(
            "\n[RUNNING] Starting NeuroFence forensic analysis..."
        )

        try:

            # Import main pipeline
            from main import main

            # Run complete NeuroFence analysis
            main(
                log_callback=lambda message:
                    self.result_area.append(
                        str(message)
                    )
            )

            self.latest_analysis_results = {
                "status": "Completed"
            }

            self.result_area.append(
                "\n[SUCCESS] Forensic analysis completed successfully."
            )

        except Exception as e:

            self.result_area.append(
                f"\n[ERROR] Analysis failed: {str(e)}"
            )


    # ==================================================
    # Generate PDF Report
    # ==================================================

    def generate_report_action(self):

        self.result_area.append(
            "\n[STATUS] Triggering PDF Report Engine..."
        )

        try:

            reporter = PDFReportGenerator()

            reporter.generate()

            self.result_area.append(
                "[SUCCESS] PDF Security Report generated successfully!\n"
            )

        except FileNotFoundError:

            self.result_area.append(
                "[ERROR] report.json not found. "
                "Please run the analysis first.\n"
            )

        except Exception as e:

            self.result_area.append(
                f"[ERROR] Report generation failed: {str(e)}\n"
            )


# ======================================================
# Application Entry Point
# ======================================================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = NeuroFenceApp()

    window.show()

    sys.exit(
        app.exec()
    )