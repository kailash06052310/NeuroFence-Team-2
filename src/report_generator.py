"""
NeuroFence Project

Module: Report Generator

Purpose:
Generate a JSON security report containing
prompt, layer differences, risk score, verdict,
and additional detection metrics.
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
        verdict,
        confidence_score=None,
        average_difference=None,
        maximum_difference=None,
        high_risk_layers=None,
        total_layers=None,
        high_risk_percentage=None,
        reason=None,
        thresholds=None
    ):

        result = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "prompt": prompt,
            "risk_score": risk_score,
            "verdict": verdict,

            "confidence_score": confidence_score,
            "average_difference": average_difference,
            "maximum_difference": maximum_difference,
            "high_risk_layers": high_risk_layers,
            "total_layers": total_layers,
            "high_risk_percentage": high_risk_percentage,
            "reason": reason,
            "thresholds": thresholds,

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

        print(
            f"\n✓ JSON report saved as '{self.filename}'"
        )