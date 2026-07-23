"""
NeuroFence Project

Module: Detection Logic

Author: Kailash

Purpose:
Calculate risk score and detect suspicious LLM behavior
based on activation differences.
"""


class DetectionLogic:

    def __init__(self):
        pass

    def calculate_risk_score(self, comparison):

        total_difference = 0
        layer_count = 0

        for layer, value in comparison.items():
            total_difference += value
            layer_count += 1

        if layer_count == 0:
            return 0

        average_difference = total_difference / layer_count
        risk_score = min(average_difference * 100, 100)

        return round(risk_score, 2)

    def get_verdict(self, risk_score):

        if risk_score < 30:
            return "Safe"
        elif risk_score < 70:
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