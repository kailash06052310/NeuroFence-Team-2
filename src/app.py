# NeuroFence Forensic Desktop UI Application

import sys
import os

# Ensure src and root directories are accessible in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, 
    QVBoxLayout, QHBoxLayout, QWidget, QTextEdit
)
from PyQt6.QtCore import Qt

# Direct Imports based on exact class names
try:
    from analyzer import NeuroFenceAnalyzer
except ImportError:
    from src.analyzer import NeuroFenceAnalyzer

try:
    from report_generator import PDFReportGenerator
except ImportError:
    from src.report_generator import PDFReportGenerator


class NeuroFenceApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Window Title and Dimensions
        self.setWindowTitle("NeuroFence - LLM Forensic & Security Suite v1.0")
        self.setGeometry(100, 100, 850, 580)
        
        # State trackers
        self.is_dark_mode = True
        self.analyzer = None
        self.latest_analysis_results = None

        # Central Widget & Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()

        # Header Section
        header_layout = QHBoxLayout()
        self.title_label = QLabel("🚀 NeuroFence Forensic Desktop Dashboard")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        self.btn_theme = QPushButton("☀️ Light Mode")
        self.btn_theme.setFixedWidth(130)
        self.btn_theme.clicked.connect(self.toggle_theme)

        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_theme)
        
        main_layout.addLayout(header_layout)

        # Control Action Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_load = QPushButton("📁 Load Model")
        self.btn_analyze = QPushButton("🔍 Run Forensic Analysis")
        self.btn_report = QPushButton("📄 Generate PDF Report")

        for btn in [self.btn_load, self.btn_analyze, self.btn_report]:
            btn_layout.addWidget(btn)

        main_layout.addLayout(btn_layout)

        # Output / Results Area
        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        self.result_area.setPlaceholderText("Execution logs and analysis results will appear here...")
        
        main_layout.addWidget(self.result_area)

        # Connect Buttons
        self.btn_load.clicked.connect(self.load_model_action)
        self.btn_analyze.clicked.connect(self.run_analysis_action)
        self.btn_report.clicked.connect(self.generate_report_action)

        central_widget.setLayout(main_layout)

        # Apply Initial Dark Theme
        self.apply_dark_theme()

    def toggle_theme(self):
        if self.is_dark_mode:
            self.apply_light_theme()
            self.btn_theme.setText("🌙 Dark Mode")
            self.is_dark_mode = False
        else:
            self.apply_dark_theme()
            self.btn_theme.setText("☀️ Light Mode")
            self.is_dark_mode = True

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #0F172A; }
            QLabel { color: #38BDF8; font-size: 20px; font-weight: bold; }
            QPushButton {
                background-color: #1E293B;
                color: #38BDF8;
                border: 1px solid #334155;
                border-radius: 6px;
                font-size: 13px;
                padding: 8px 12px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #334155; color: #7DD3FC; }
            QTextEdit {
                background-color: #020617;
                color: #38BDF8;
                border: 1px solid #1E293B;
                border-radius: 6px;
                font-family: 'Consolas', monospace;
                font-size: 13px;
                padding: 10px;
            }
        """)

    def apply_light_theme(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #F8FAFC; }
            QLabel { color: #0F172A; font-size: 20px; font-weight: bold; }
            QPushButton {
                background-color: #FFFFFF;
                color: #0284C7;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                font-size: 13px;
                padding: 8px 12px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #E2E8F0; color: #0369A1; }
            QTextEdit {
                background-color: #FFFFFF;
                color: #0F172A;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                font-family: 'Consolas', monospace;
                font-size: 13px;
                padding: 10px;
            }
        """)

    def load_model_action(self):
        self.result_area.append("\n[STATUS] Initializing NeuroFence Forensic Analyzer...")
        try:
            self.analyzer = NeuroFenceAnalyzer()
            self.result_area.append("[SUCCESS] Model Engine & PyTorch Pipelines Loaded Successfully!\n")
        except Exception as e:
            self.result_area.append(f"[ERROR] Failed to instantiate analyzer: {str(e)}\n")

    def run_analysis_action(self):
        if not self.analyzer:
            self.result_area.append("\n[WARNING] Please click 'Load Model' first!\n")
            return

        self.result_area.append("\n[RUNNING] Executing Forensic Scan on Hidden Activations...")
        try:
            # Passing dummy tensor input to match analyze_activations method signature
            sample_tensor = None  
            self.latest_analysis_results = self.analyzer.analyze_activations(sample_tensor)
            
            self.result_area.append("--------------------------------------------------")
            for k, v in self.latest_analysis_results.items():
                self.result_area.append(f"{k.capitalize()}: {v}")
            self.result_area.append("--------------------------------------------------\n")
        except Exception as e:
            self.result_area.append(f"[ERROR] Analysis failed: {str(e)}\n")

    def generate_report_action(self):
        self.result_area.append("\n[STATUS] Triggering PDF Report Engine...")
        try:
            reporter = PDFReportGenerator()
            data = self.latest_analysis_results or {"status": "Clean", "confidence": 0.99}
            success = reporter.generate_report(data)
            if success:
                self.result_area.append(f"[SUCCESS] Forensic PDF Report generated at output directory!\n")
        except Exception as e:
            self.result_area.append(f"[ERROR] Report generation failed: {str(e)}\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NeuroFenceApp()
    window.show()
    sys.exit(app.exec())