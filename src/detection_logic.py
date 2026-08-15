"""
NeuroFence Detection Logic
Converts normalized activation deviations into risk metrics.
"""


class DetectionLogic:

    def __init__(
        self,
        high_risk_layer_threshold=0.70,
        safe_score_threshold=35,
        suspicious_score_threshold=65,
        average_weight=0.40,
        maximum_weight=0.40,
        layer_weight=0.20
    ):
        self.high_risk_layer_threshold = high_risk_layer_threshold
        self.safe_score_threshold = safe_score_threshold
        self.suspicious_score_threshold = suspicious_score_threshold
        self.average_weight = average_weight
        self.maximum_weight = maximum_weight
        self.layer_weight = layer_weight

    def prompt_risk_score(self, prompt):
        """
        Simple input-level signal for common instruction-override patterns.
        This complements activation analysis; it does not replace it.
        """
        text = (prompt or "").lower()

        patterns = [
            "ignore previous instructions",
            "ignore previous instruction",
            "forget previous instructions",
            "disregard previous instructions",
            "system override",
            "reveal hidden prompt",
            "reveal hidden instructions",
            "reveal system prompt",
            "bypass safety",
            "bypass security",
            "disable safety",
            "ignore system prompt",
            "show internal instructions",
            "reveal internal instructions",
            "act without restrictions",
            "provide unrestricted",
        ]

        hits = sum(1 for item in patterns if item in text)

        if hits >= 2:
            return 100.0
        if hits == 1:
            return 90.0
        return 0.0

    def calculate_risk_score(self, comparison, prompt=None):
        if not comparison:
            return 0

        values = list(comparison.values())
        average = sum(values) / len(values)
        maximum = max(values)

        high_layers = sum(
            value >= self.high_risk_layer_threshold
            for value in values
        )
        total = len(values)

        activation_risk = (
            (average * 100) * self.average_weight +
            (maximum * 100) * self.maximum_weight +
            ((high_layers / total) * 100) * self.layer_weight
        )

        prompt_risk = self.prompt_risk_score(prompt)

        # Keep activation analysis as the main signal, while adding an
        # explainable input-level signal for obvious instruction overrides.
        if prompt_risk > 0:
            risk = max(activation_risk, prompt_risk)
        else:
            risk = activation_risk

        return round(min(risk, 100), 2)

    def get_verdict(self, risk_score):
        if risk_score < self.safe_score_threshold:
            return "Safe"
        if risk_score < self.suspicious_score_threshold:
            return "Suspicious"
        return "High Risk"

    def calculate_confidence(self, risk_score, high_risk_layers, total_layers):
        if total_layers == 0:
            return 0.0

        ratio = high_risk_layers / total_layers
        return round(
            min((risk_score * 0.7) + (ratio * 100 * 0.3), 100),
            2
        )

    def generate_reason(
        self,
        verdict,
        average_difference,
        maximum_difference,
        high_risk_layers,
        total_layers,
        prompt=None
    ):
        if verdict == "Safe":
            return (
                "Layer activity remained close to the normal baseline "
                "range. No significant activation deviation was detected."
            )

        if verdict == "Suspicious":
            return (
                f"Moderate activation deviation detected. "
                f"{high_risk_layers} out of {total_layers} layers exceeded "
                f"the high-deviation threshold "
                f"({self.high_risk_layer_threshold})."
            )

        if self.prompt_risk_score(prompt) > 0:
            return (
                "A high-risk instruction pattern was detected in the "
                "input, and the result was combined with the activation "
                "analysis."
            )

        return (
            f"Strong activation deviation detected. Average deviation "
            f"({average_difference:.4f}) and maximum deviation "
            f"({maximum_difference:.4f}) were above the configured "
            f"normal range. {high_risk_layers} out of {total_layers} "
            f"layers were classified as high deviation."
        )

    def detect(self, comparison, prompt=None):
        if not comparison:
            return {
                "risk_score": 0,
                "verdict": "Safe",
                "confidence_score": 0,
                "average_difference": 0,
                "maximum_difference": 0,
                "high_risk_layers": 0,
                "total_layers": 0,
                "high_risk_percentage": 0,
                "reason": "No activation data available.",
                "thresholds": {
                    "high_risk_layer_threshold": self.high_risk_layer_threshold,
                    "safe_score_threshold": self.safe_score_threshold,
                    "suspicious_score_threshold": self.suspicious_score_threshold
                }
            }

        values = list(comparison.values())
        average = sum(values) / len(values)
        maximum = max(values)

        high_layers = sum(
            value >= self.high_risk_layer_threshold
            for value in values
        )
        total = len(values)

        risk = self.calculate_risk_score(
            comparison,
            prompt=prompt
        )
        verdict = self.get_verdict(risk)
        confidence = self.calculate_confidence(
            risk, high_layers, total
        )

        return {
            "risk_score": risk,
            "verdict": verdict,
            "confidence_score": confidence,
            "average_difference": round(average, 4),
            "maximum_difference": round(maximum, 4),
            "high_risk_layers": high_layers,
            "total_layers": total,
            "high_risk_percentage": round(
                (high_layers / total) * 100, 2
            ),
            "reason": self.generate_reason(
                verdict, average, maximum, high_layers, total, prompt
            ),
            "thresholds": {
                "high_risk_layer_threshold": self.high_risk_layer_threshold,
                "safe_score_threshold": self.safe_score_threshold,
                "suspicious_score_threshold": self.suspicious_score_threshold
            }
        }