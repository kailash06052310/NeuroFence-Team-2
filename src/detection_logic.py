"""
NeuroFence Project

Module: Detection Logic

Author: Kailash

Purpose:
Calculate a weighted risk score based on layer activation
differences and classify the model as Safe, Suspicious,
or High Risk.
"""


class DetectionLogic:

    def __init__(self):
        pass

    def calculate_risk_score(self, comparison):

        if not comparison:
            return 0

        differences = list(comparison.values())

        # Average Difference
        average_difference = sum(differences) / len(differences)

        # Maximum Difference
        maximum_difference = max(differences)

        # Count High-Risk Layers
        high_risk_layers = 0

        for value in differences:
            if value >= 2.0:
                high_risk_layers += 1

        total_layers = len(differences)

        # -----------------------
        # Normalize Values
        # -----------------------

        average_score = min((average_difference / 3.0) * 100, 100)

        maximum_score = min((maximum_difference / 3.0) * 100, 100)

        high_layer_score = (high_risk_layers / total_layers) * 100

        # -----------------------
        # Weighted Final Score
        # -----------------------

        risk_score = (
            average_score * 0.40 +
            maximum_score * 0.40 +
            high_layer_score * 0.20
        )

        return round(risk_score, 2)

    def get_verdict(self, risk_score):

        if risk_score < 30:
            return "Safe"

        elif risk_score < 60:
            return "Suspicious"

        else:
            return "High Risk"

    def detect(self, comparison):

        risk_score = self.calculate_risk_score(comparison)

        verdict = self.get_verdict(risk_score)

        return {
            "risk_score": risk_score,
            "verdict": verdict
        }