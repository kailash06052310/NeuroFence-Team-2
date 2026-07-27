"""
NeuroFence Project

Module: Report Generator

Author: Kailash

Purpose:
Generate a JSON security report containing
prompt, layer differences, risk score and verdict.
"""

import json
from datetime import datetime


class ReportGenerator:

    def __init__(self, filename="report.json"):
        self.filename = filename
        self.results = []

    def add_result(
        self,
        prompt,
        comparison,
        risk_score,
        verdict
    ):

        result = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "prompt": prompt,
            "risk_score": risk_score,
            "verdict": verdict,
            "layer_differences": comparison
        }

        self.results.append(result)

    def save_report(self):

        with open(self.filename, "w", encoding="utf-8") as file:

            json.dump(
                self.results,
                file,
                indent=4
            )

        print(f"\n✓ JSON report saved as '{self.filename}'")