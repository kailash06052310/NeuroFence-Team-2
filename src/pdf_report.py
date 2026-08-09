"""
NeuroFence Project

Module: PDF Report Generator

Purpose:
Generate a professional PDF security report
from the JSON report.
"""

import json
import os

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet


class PDFReportGenerator:

    def __init__(
        self,
        json_file=None,
        pdf_file=None
    ):

        # Project root directory
        project_root = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )

        # Reports directory
        reports_dir = os.path.join(
            project_root,
            "reports"
        )

        # Create reports directory if it does not exist
        os.makedirs(
            reports_dir,
            exist_ok=True
        )

        # Default report paths
        if json_file is None:
            json_file = os.path.join(
                reports_dir,
                "report.json"
            )

        if pdf_file is None:
            pdf_file = os.path.join(
                reports_dir,
                "Security_Report.pdf"
            )

        self.json_file = json_file
        self.pdf_file = pdf_file

    def generate(self):

        # Check JSON file
        if not os.path.exists(self.json_file):

            raise FileNotFoundError(
                f"JSON report not found: {self.json_file}"
            )

        # Read JSON report
        with open(
            self.json_file,
            "r",
            encoding="utf-8"
        ) as file:

            results = json.load(file)

        styles = getSampleStyleSheet()

        document = SimpleDocTemplate(
            self.pdf_file
        )

        story = []

        # -----------------------------------------
        # TITLE
        # -----------------------------------------

        story.append(
            Paragraph(
                "<b>NeuroFence Security Analysis Report</b>",
                styles["Title"]
            )
        )

        story.append(
            Spacer(1, 20)
        )

        # -----------------------------------------
        # Counters
        # -----------------------------------------

        high = 0
        suspicious = 0
        safe = 0

        total_risk = 0
        total_confidence = 0
        highest_risk = 0

        # -----------------------------------------
        # Individual Results
        # -----------------------------------------

        for index, result in enumerate(
            results,
            start=1
        ):

            risk_score = result.get(
                "risk_score",
                0
            )

            confidence = result.get(
                "confidence_score",
                0
            )

            verdict = result.get(
                "verdict",
                "Unknown"
            )

            total_risk += risk_score
            total_confidence += confidence

            highest_risk = max(
                highest_risk,
                risk_score
            )

            # Count verdicts
            if verdict == "High Risk":

                high += 1

            elif verdict == "Suspicious":

                suspicious += 1

            else:

                safe += 1

            # -------------------------------------
            # Analysis Heading
            # -------------------------------------

            story.append(
                Paragraph(
                    f"<b>Analysis #{index}</b>",
                    styles["Heading1"]
                )
            )

            # Prompt
            story.append(
                Paragraph(
                    f"<b>Prompt:</b> "
                    f"{result.get('prompt', '-')}",
                    styles["Normal"]
                )
            )

            story.append(
                Spacer(1, 5)
            )

            # Timestamp
            story.append(
                Paragraph(
                    f"<b>Timestamp:</b> "
                    f"{result.get('timestamp', '-')}",
                    styles["Normal"]
                )
            )

            # Risk
            story.append(
                Paragraph(
                    f"<b>Risk Score:</b> "
                    f"{risk_score}",
                    styles["Normal"]
                )
            )

            # Confidence
            story.append(
                Paragraph(
                    f"<b>Confidence Score:</b> "
                    f"{confidence}%",
                    styles["Normal"]
                )
            )

            # Verdict
            story.append(
                Paragraph(
                    f"<b>Verdict:</b> "
                    f"{verdict}",
                    styles["Normal"]
                )
            )

            # Average Difference
            story.append(
                Paragraph(
                    f"<b>Average Difference:</b> "
                    f"{result.get('average_difference', '-')}",
                    styles["Normal"]
                )
            )

            # Maximum Difference
            story.append(
                Paragraph(
                    f"<b>Maximum Difference:</b> "
                    f"{result.get('maximum_difference', '-')}",
                    styles["Normal"]
                )
            )

            # High Risk Layers
            story.append(
                Paragraph(
                    f"<b>High Risk Layers:</b> "
                    f"{result.get('high_risk_layers', '-')} / "
                    f"{result.get('total_layers', '-')}",
                    styles["Normal"]
                )
            )

            # High Risk Percentage
            story.append(
                Paragraph(
                    f"<b>High Risk Percentage:</b> "
                    f"{result.get('high_risk_percentage', '-')}%",
                    styles["Normal"]
                )
            )

            # Reason
            story.append(
                Paragraph(
                    f"<b>Reason:</b> "
                    f"{result.get('reason', 'Not Available')}",
                    styles["Normal"]
                )
            )

            story.append(
                Spacer(1, 10)
            )

            # -------------------------------------
            # Layer Differences
            # -------------------------------------

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

                try:

                    value = round(
                        float(value),
                        4
                    )

                except (TypeError, ValueError):

                    pass

                story.append(
                    Paragraph(
                        f"{layer} : {value}",
                        styles["Normal"]
                    )
                )

            story.append(
                Spacer(1, 20)
            )

        # -----------------------------------------
        # FINAL SUMMARY
        # -----------------------------------------

        story.append(
            Paragraph(
                "<b>Final Summary</b>",
                styles["Heading1"]
            )
        )

        total_tests = len(results)

        if total_tests:

            average_risk = (
                total_risk /
                total_tests
            )

            average_confidence = (
                total_confidence /
                total_tests
            )

        else:

            average_risk = 0
            average_confidence = 0

        story.append(
            Paragraph(
                f"<b>Total Prompts Tested:</b> "
                f"{total_tests}",
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

        # -----------------------------------------
        # BUILD PDF
        # -----------------------------------------

        document.build(story)

        print(
            f"\n✓ PDF report saved as:"
            f"\n{self.pdf_file}"
        )

        return self.pdf_file