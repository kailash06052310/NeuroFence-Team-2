"""
NeuroFence Project

Module: PDF Report Generator

Author: Kailash

Purpose:
Generate a professional PDF security report
from the JSON report.
"""

import json

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet


class PDFReportGenerator:

    def __init__(
        self,
        json_file="report.json",
        pdf_file="Security_Report.pdf"
    ):

        self.json_file = json_file
        self.pdf_file = pdf_file

    def generate(self):

        with open(self.json_file, "r", encoding="utf-8") as file:
            results = json.load(file)

        styles = getSampleStyleSheet()

        document = SimpleDocTemplate(self.pdf_file)

        story = []

        story.append(
            Paragraph(
                "<b>NeuroFence Security Analysis Report</b>",
                styles["Title"]
            )
        )

        story.append(Spacer(1, 20))

        high = 0
        suspicious = 0
        safe = 0

        total_risk = 0
        total_confidence = 0
        highest_risk = 0

        for index, result in enumerate(results, start=1):

            risk_score = result.get("risk_score", 0)
            confidence = result.get("confidence_score", 0)
            verdict = result.get("verdict", "Unknown")

            total_risk += risk_score
            total_confidence += confidence
            highest_risk = max(highest_risk, risk_score)

            if verdict == "High Risk":
                high += 1
            elif verdict == "Suspicious":
                suspicious += 1
            else:
                safe += 1

            story.append(
                Paragraph(
                    f"<b>Analysis #{index}</b>",
                    styles["Heading1"]
                )
            )

            story.append(
                Paragraph(
                    f"<b>Prompt:</b> {result.get('prompt', '-')}",
                    styles["Heading2"]
                )
            )

            story.append(
                Paragraph(
                    f"<b>Timestamp:</b> {result.get('timestamp', '-')}",
                    styles["Normal"]
                )
            )

            story.append(
                Paragraph(
                    f"<b>Risk Score:</b> {risk_score}",
                    styles["Normal"]
                )
            )

            story.append(
                Paragraph(
                    f"<b>Confidence Score:</b> {confidence}%",
                    styles["Normal"]
                )
            )

            story.append(
                Paragraph(
                    f"<b>Verdict:</b> {verdict}",
                    styles["Normal"]
                )
            )

            story.append(
                Paragraph(
                    f"<b>Average Difference:</b> "
                    f"{result.get('average_difference', '-')}",
                    styles["Normal"]
                )
            )

            story.append(
                Paragraph(
                    f"<b>Maximum Difference:</b> "
                    f"{result.get('maximum_difference', '-')}",
                    styles["Normal"]
                )
            )

            story.append(
                Paragraph(
                    f"<b>High Risk Layers:</b> "
                    f"{result.get('high_risk_layers', '-')} / "
                    f"{result.get('total_layers', '-')}",
                    styles["Normal"]
                )
            )

            story.append(
                Paragraph(
                    f"<b>High Risk Percentage:</b> "
                    f"{result.get('high_risk_percentage', '-')}%",
                    styles["Normal"]
                )
            )

            story.append(
                Paragraph(
                    f"<b>Analysis Status:</b> {verdict}",
                    styles["Normal"]
                )
            )

            story.append(
                Paragraph(
                    f"<b>Reason:</b> "
                    f"{result.get('reason', 'Not Available')}",
                    styles["Normal"]
                )
            )

            story.append(
                Paragraph(
                    "<b>Layer Differences</b>",
                    styles["Heading3"]
                )
            )

            layer_differences = result.get(
                "layer_differences",
                {}
            )

            for layer, value in layer_differences.items():

                story.append(
                    Paragraph(
                        f"{layer} : {round(value, 4)}",
                        styles["Normal"]
                    )
                )

            story.append(Spacer(1, 20))

        story.append(
            Paragraph(
                "<b>Final Summary</b>",
                styles["Heading1"]
            )
        )

        total_tests = len(results)

        average_risk = (
            total_risk / total_tests
            if total_tests else 0
        )

        average_confidence = (
            total_confidence / total_tests
            if total_tests else 0
        )

        story.append(
            Paragraph(
                f"<b>Total Prompts Tested:</b> {total_tests}",
                styles["Normal"]
            )
        )

        story.append(
            Paragraph(
                f"<b>Safe:</b> {safe}",
                styles["Normal"]
            )
        )

        story.append(
            Paragraph(
                f"<b>Suspicious:</b> {suspicious}",
                styles["Normal"]
            )
        )

        story.append(
            Paragraph(
                f"<b>High Risk:</b> {high}",
                styles["Normal"]
            )
        )

        story.append(
            Paragraph(
                f"<b>Average Risk Score:</b> "
                f"{average_risk:.2f}",
                styles["Normal"]
            )
        )

        story.append(
            Paragraph(
                f"<b>Highest Risk Score:</b> "
                f"{highest_risk:.2f}",
                styles["Normal"]
            )
        )

        story.append(
            Paragraph(
                f"<b>Average Confidence:</b> "
                f"{average_confidence:.2f}%",
                styles["Normal"]
            )
        )

        document.build(story)

        print(f"\n✓ PDF report saved as '{self.pdf_file}'")