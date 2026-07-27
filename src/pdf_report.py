"""
NeuroFence Project

Module: PDF Report Generator

Author: Kailash

Purpose:
Generate a professional PDF security report
from the JSON report.
"""

import json

from reportlab.platypus import SimpleDocTemplate, Paragraph
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
            Paragraph("<b>NeuroFence Security Report</b>", styles["Title"])
        )

        story.append(
            Paragraph("<br/>", styles["Normal"])
        )

        high = 0
        suspicious = 0
        safe = 0

        for result in results:

            story.append(
                Paragraph(
                    f"<b>Prompt:</b> {result['prompt']}",
                    styles["Heading2"]
                )
            )

            story.append(
                Paragraph(
                    f"<b>Timestamp:</b> {result['timestamp']}",
                    styles["Normal"]
                )
            )

            story.append(
                Paragraph(
                    f"<b>Risk Score:</b> {result['risk_score']}",
                    styles["Normal"]
                )
            )

            story.append(
                Paragraph(
                    f"<b>Verdict:</b> {result['verdict']}",
                    styles["Normal"]
                )
            )

            story.append(
                Paragraph(
                    "<b>Layer Differences</b>",
                    styles["Heading3"]
                )
            )

            for layer, value in result["layer_differences"].items():

                story.append(
                    Paragraph(
                        f"{layer} : {round(value, 4)}",
                        styles["Normal"]
                    )
                )

            story.append(
                Paragraph("<br/>", styles["Normal"])
            )

            verdict = result["verdict"]

            if verdict == "High Risk":
                high += 1

            elif verdict == "Suspicious":
                suspicious += 1

            else:
                safe += 1

        story.append(
            Paragraph("<b>Final Summary</b>", styles["Heading1"])
        )

        story.append(
            Paragraph(
                f"Total Prompts Tested : {len(results)}",
                styles["Normal"]
            )
        )

        story.append(
            Paragraph(
                f"High Risk : {high}",
                styles["Normal"]
            )
        )

        story.append(
            Paragraph(
                f"Suspicious : {suspicious}",
                styles["Normal"]
            )
        )

        story.append(
            Paragraph(
                f"Safe : {safe}",
                styles["Normal"]
            )
        )

        document.build(story)

        print(f"\n✓ PDF report saved as '{self.pdf_file}'")