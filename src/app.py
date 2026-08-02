"""
NeuroFence Desktop UI
Compatible with NeuroFence Backend

Author:
Prithvi UI + Kailash Backend Integration
"""

import sys
import os

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
)

from PyQt6.QtCore import Qt, QObject, QThread, pyqtSignal

from model_loader import ModelLoader
from main import main


# ------------------------------------
# Worker Thread
# ------------------------------------

class AnalysisWorker(QObject):

    finished = pyqtSignal()

    log_signal = pyqtSignal(str)

    def run(self):

        try:
            main(log_callback=self.log_signal.emit)

        except Exception as e:
            self.log_signal.emit(f"\n[ERROR] {e}")

        self.finished.emit()


# ------------------------------------
# Main Window
# ------------------------------------

class NeuroFenceApp(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "NeuroFence - LLM Security Scanner"
        )

        self.setGeometry(
            150,
            80,
            900,
            600
        )

        self.loader = None

        self.model_loaded = False

        self.is_dark = True

        self.thread = None

        self.worker = None

        # --------------------
        # Central Widget
        # --------------------

        central = QWidget()

        self.setCentralWidget(central)

        layout = QVBoxLayout()

        # --------------------
        # Header
        # --------------------

        header = QHBoxLayout()

        self.title = QLabel(
            "🚀 NeuroFence Security Dashboard"
        )

        self.title.setAlignment(
            Qt.AlignmentFlag.AlignLeft
        )

        self.theme_button = QPushButton(
            "☀️ Light Mode"
        )

        self.theme_button.clicked.connect(
            self.toggle_theme
        )

        header.addWidget(self.title)

        header.addStretch()

        header.addWidget(
            self.theme_button
        )

        layout.addLayout(header)

        # --------------------
        # Buttons
        # --------------------

        buttons = QHBoxLayout()

        self.load_button = QPushButton(
            "📁 Load Model"
        )

        self.run_button = QPushButton(
            "🔍 Run Analysis"
        )

        self.report_button = QPushButton(
            "📄 Open Report Status"
        )

        buttons.addWidget(
            self.load_button
        )

        buttons.addWidget(
            self.run_button
        )

        buttons.addWidget(
            self.report_button
        )

        layout.addLayout(buttons)

        # --------------------
        # Output Console
        # --------------------

        self.console = QTextEdit()

        self.console.setReadOnly(True)

        self.console.setPlaceholderText(
            "Execution logs will appear here..."
        )

        layout.addWidget(self.console)

        central.setLayout(layout)

        # --------------------
        # Button Connections
        # --------------------

        self.load_button.clicked.connect(
            self.load_model_action
        )

        self.run_button.clicked.connect(
            self.run_analysis_action
        )

        self.report_button.clicked.connect(
            self.report_action
        )

        self.apply_dark_theme()

    # --------------------------------

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

    # --------------------------------

    def apply_dark_theme(self):

        self.setStyleSheet("""

QMainWindow{
background:#0F172A;
}

QLabel{
color:#38BDF8;
font-size:20px;
font-weight:bold;
}

QPushButton{

background:#1E293B;

color:#38BDF8;

border:1px solid #334155;

border-radius:6px;

padding:8px;

font-weight:bold;

}

QPushButton:hover{

background:#334155;

}

QTextEdit{

background:#020617;

color:#38BDF8;

border:1px solid #334155;

font-family:Consolas;

font-size:13px;

}

""")

    # --------------------------------

    def apply_light_theme(self):

        self.setStyleSheet("""

QMainWindow{
background:white;
}

QLabel{

color:black;

font-size:20px;

font-weight:bold;

}

QPushButton{

background:#EEEEEE;

font-weight:bold;

}

QTextEdit{

background:white;

color:black;

font-family:Consolas;

font-size:13px;

}

""")
    # --------------------------------

    def load_model_action(self):

        self.console.append(
            "\n[STATUS] Loading Hugging Face Model..."
        )

        try:

            self.loader = ModelLoader()

            self.loader.load_model()

            self.model_loaded = True

            self.console.append(
                "[SUCCESS] Model Loaded Successfully!\n"
            )

        except Exception as e:

            self.console.append(
                f"[ERROR] {e}\n"
            )

    # --------------------------------

    def run_analysis_action(self):

        if not self.model_loaded:

            self.console.append(
                "\n[WARNING] Please load the model first!\n"
            )

            return

        self.run_button.setEnabled(False)

        self.console.append(
            "\n[STATUS] Starting NeuroFence Analysis...\n"
        )

        self.thread = QThread()

        self.worker = AnalysisWorker()

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(
            self.worker.run
        )

        self.worker.log_signal.connect(
            self.console.append
        )

        self.worker.finished.connect(
            self.analysis_finished
        )

        self.worker.finished.connect(
            self.thread.quit
        )

        self.worker.finished.connect(
            self.worker.deleteLater
        )

        self.thread.finished.connect(
            self.thread.deleteLater
        )

        self.thread.start()

    # --------------------------------

    def analysis_finished(self):

        self.console.append(
            "\n[SUCCESS] NeuroFence Analysis Completed."
        )

        self.console.append(
            "[SUCCESS] JSON Report Saved."
        )

        self.console.append(
            "[SUCCESS] PDF Report Generated.\n"
        )

        self.run_button.setEnabled(True)

    # --------------------------------

    def report_action(self):

        pdf_path = "Security_Report.pdf"

        if os.path.exists(pdf_path):

            self.console.append(
                "\n[SUCCESS] Opening Security_Report.pdf..."
            )

            os.startfile(pdf_path)

        else:

            self.console.append(
                "\n[INFO] Please run analysis first."
            )


# ------------------------------------
# Run Application
# ------------------------------------

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = NeuroFenceApp()

    window.show()

    sys.exit(app.exec())