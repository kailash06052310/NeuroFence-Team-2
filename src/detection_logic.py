"""
NeuroFence Project

Module: Detection Logic

Author: Kailash

Purpose:
Calculate a weighted risk score based on layer activation
differences and classify the model as Safe, Suspicious,
or High Risk.

Enhanced Features:
- Configurable thresholds
- Confidence score
- Average difference
- Maximum difference
- High-risk layer count
- Total layers
- Human-readable reason
"""

class DetectionLogic:

    def __init__(
        self,
        high_risk_layer_threshold=2.0,
        safe_score_threshold=30,
        suspicious_score_threshold=60,
        average_weight=0.40,
        maximum_weight=0.40,
        layer_weight=0.20
    ):
        """
        Initialize configurable detection settings.
        Default values preserve previous behaviour.
        """

        self.high_risk_layer_threshold = high_risk_layer_threshold

        self.safe_score_threshold = safe_score_threshold
        self.suspicious_score_threshold = suspicious_score_threshold

        self.average_weight = average_weight
        self.maximum_weight = maximum_weight
        self.layer_weight = layer_weight

    # --------------------------------------------------
    # Calculate Risk Score
    # --------------------------------------------------

    def calculate_risk_score(self, comparison):

        if not comparison:
            return 0

        differences = list(comparison.values())

        average_difference = sum(differences) / len(differences)
        maximum_difference = max(differences)

        high_risk_layers = sum(
            1
            for value in differences
            if value >= self.high_risk_layer_threshold
        )

        total_layers = len(differences)

        average_score = min(
            (average_difference / 3.0) * 100,
            100
        )

        maximum_score = min(
            (maximum_difference / 3.0) * 100,
            100
        )

        high_layer_score = (
            high_risk_layers / total_layers
        ) * 100

        risk_score = (
            average_score * self.average_weight +
            maximum_score * self.maximum_weight +
            high_layer_score * self.layer_weight
        )

        return round(risk_score, 2)

    # --------------------------------------------------
    # Verdict
    # --------------------------------------------------

    def get_verdict(self, risk_score):

        if risk_score < self.safe_score_threshold:
            return "Safe"

        elif risk_score < self.suspicious_score_threshold:
            return "Suspicious"

        return "High Risk"

    # --------------------------------------------------
    # Confidence Score
    # --------------------------------------------------

    def calculate_confidence(
        self,
        risk_score,
        high_risk_layers,
        total_layers
    ):

        if total_layers == 0:
            return 0.0

        layer_ratio = high_risk_layers / total_layers

        confidence = (
            (risk_score * 0.7) +
            (layer_ratio * 100 * 0.3)
        )

        return round(min(confidence, 100), 2)

    # --------------------------------------------------
    # Reason Generator
    # --------------------------------------------------

    def generate_reason(
        self,
        verdict,
        average_difference,
        maximum_difference,
        high_risk_layers,
        total_layers
    ):

        if verdict == "Safe":
            return (
                "Layer activation differences remained within "
                "acceptable limits. No significant abnormal "
                "behaviour was detected."
            )

        if verdict == "Suspicious":
            return (
                f"Moderate activation deviations detected. "
                f"{high_risk_layers} out of {total_layers} layers "
                f"exceeded the configured threshold "
                f"({self.high_risk_layer_threshold})."
            )

        return (
            f"High activation anomalies detected. Average "
            f"difference ({average_difference:.4f}) and maximum "
            f"difference ({maximum_difference:.4f}) indicate "
            f"potential model poisoning/backdoor behaviour. "
            f"{high_risk_layers} out of {total_layers} layers "
            f"were classified as high risk."
        )

    # --------------------------------------------------
    # Complete Detection
    # --------------------------------------------------

    def detect(self, comparison):

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
                    "high_risk_layer_threshold":
                        self.high_risk_layer_threshold,
                    "safe_score_threshold":
                        self.safe_score_threshold,
                    "suspicious_score_threshold":
                        self.suspicious_score_threshold
                }
            }

        differences = list(comparison.values())

        average_difference = (
            sum(differences) / len(differences)
        )

        maximum_difference = max(differences)

        high_risk_layers = sum(
            1
            for value in differences
            if value >= self.high_risk_layer_threshold
        )

        total_layers = len(differences)

        high_risk_percentage = (
            high_risk_layers / total_layers
        ) * 100

        risk_score = self.calculate_risk_score(
            comparison
        )

        verdict = self.get_verdict(
            risk_score
        )

        confidence_score = self.calculate_confidence(
            risk_score,
            high_risk_layers,
            total_layers
        )

        reason = self.generate_reason(
            verdict,
            average_difference,
            maximum_difference,
            high_risk_layers,
            total_layers
        )

        return {

            # Existing fields (Backward Compatible)
            "risk_score": risk_score,
            "verdict": verdict,

            # New Metrics
            "confidence_score": confidence_score,
            "average_difference": round(
                average_difference,
                4
            ),
            "maximum_difference": round(
                maximum_difference,
                4
            ),
            "high_risk_layers": high_risk_layers,
            "total_layers": total_layers,
            "high_risk_percentage": round(
                high_risk_percentage,
                2
            ),
            "reason": reason,

            # Configuration used
            "thresholds": {
                "high_risk_layer_threshold":
                    self.high_risk_layer_threshold,
                "safe_score_threshold":
                    self.safe_score_threshold,
                "suspicious_score_threshold":
                    self.suspicious_score_threshold
            }
        }