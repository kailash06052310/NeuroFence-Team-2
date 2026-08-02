"""
NeuroFence Project

Module: Activation Analyzer

Author: Rohan

Purpose:
Analyze hidden layer activations collected by the Activation Tracker.
This module calculates statistical information from activations.
"""

import torch


class ActivationAnalyzer:
    """
    Analyze activations captured from transformer layers.
    """

    def __init__(self):
        """
        Initialize analyzer.
        """
        pass

    def calculate_mean(self, activation):
        """
        Calculate mean activation value.

        Parameters:
            activation (Tensor): Activation tensor.

        Returns:
            float: Mean activation value.
        """

        if activation is None:
            raise ValueError("Activation cannot be None.")

        return torch.mean(activation.float()).item()

    def calculate_max(self, activation):
        """
        Calculate maximum activation value.

        Parameters:
            activation (Tensor): Activation tensor.

        Returns:
            float: Maximum activation value.
        """

        if activation is None:
            raise ValueError("Activation cannot be None.")

        return torch.max(activation.float()).item()

    def calculate_min(self, activation):
        """
        Calculate minimum activation value.

        Parameters:
            activation (Tensor): Activation tensor.

        Returns:
            float: Minimum activation value.
        """

        if activation is None:
            raise ValueError("Activation cannot be None.")

        return torch.min(activation.float()).item()

    def calculate_std(self, activation):
        """
        Calculate standard deviation of activation values.

        Parameters:
            activation (Tensor): Activation tensor.

        Returns:
            float: Standard deviation.
        """

        if activation is None:
            raise ValueError("Activation cannot be None.")

        return torch.std(activation.float()).item()

    def calculate_energy(self, activation):
        """
        Calculate activation energy.

        Energy is defined as the sum of squared activation values.

        Parameters:
            activation (Tensor): Activation tensor.

        Returns:
            float: Activation energy.
        """

        if activation is None:
            raise ValueError("Activation cannot be None.")

        return torch.sum(activation.float() ** 2).item()

    def calculate_activation_statistics(self, activation):
        """
        Calculate all statistical information for a single activation.

        Parameters:
            activation (Tensor): Activation tensor.

        Returns:
            dict: Dictionary containing activation statistics.
        """

        if activation is None:
            raise ValueError("Activation cannot be None.")

        return {
            "mean": self.calculate_mean(activation),
            "max": self.calculate_max(activation),
            "min": self.calculate_min(activation),
            "std": self.calculate_std(activation),
            "energy": self.calculate_energy(activation)
        }

    def compare_activation_statistics(
        self,
        clean_activation,
        suspicious_activation
        ):
            """
            Compare statistics of two activation tensors.

            Parameters:
                clean_activation (Tensor): Baseline activation.
                suspicious_activation (Tensor): Activation to compare.

            Returns:
                dict: Difference between activation statistics.
            """

            clean_stats = self.calculate_activation_statistics(
                clean_activation
            )

            suspicious_stats = self.calculate_activation_statistics(
                suspicious_activation
            )

            comparison = {}

            for key in clean_stats:

                comparison[key] = round(
                    suspicious_stats[key] - clean_stats[key],
                    6
                )

            return comparison

    def detect_anomalous_layers(
        self,
        comparison,
        threshold=10.0
    ):
        """
        Detect anomalous statistics based on a threshold.

        Parameters:
            comparison (dict): Output from compare_activation_statistics().
            threshold (float): Difference threshold.

        Returns:
            dict: Detected anomalous statistics.
        """

        anomalies = {}

        for statistic, difference in comparison.items():

            if abs(difference) >= threshold:

                anomalies[statistic] = {
                    "difference": round(difference, 6),
                    "status": "Anomalous"
                }

        return anomalies

    def generate_activation_summary(
        self,
        comparison,
        anomalies
    ):
        """
        Generate a summary of activation comparison.

        Parameters:
            comparison (dict): Activation comparison results.
            anomalies (dict): Detected anomalies.

        Returns:
            dict: Summary report.
        """

        total_statistics = len(comparison)
        anomalous_statistics = len(anomalies)

        summary = {
            "total_statistics": total_statistics,
            "anomalous_statistics": anomalous_statistics,
            "normal_statistics": (
                total_statistics - anomalous_statistics
            ),
            "anomaly_percentage": round(
                (anomalous_statistics / total_statistics) * 100,
                2
            ) if total_statistics else 0,
            "status": (
                "Suspicious"
                if anomalous_statistics > 0
                else "Normal"
            )
        }

        return summary

if __name__ == "__main__":

    analyzer = ActivationAnalyzer()

    activation1 = torch.tensor([1.0, 2.0, 3.0, 4.0])
    activation2 = torch.tensor([2.0, 3.0, 4.0, 5.0])

    stats = analyzer.calculate_activation_statistics(activation1)
    print("Statistics:")
    print(stats)

    comparison = analyzer.compare_activation_statistics(
        activation1,
        activation2
    )
    print("\nComparison:")
    print(comparison)

    anomalies = analyzer.detect_anomalous_layers(
        comparison,
        threshold=1.0
    )
    print("\nAnomalies:")
    print(anomalies)

    summary = analyzer.generate_activation_summary(
        comparison,
        anomalies
    )
    print("\nSummary:")
    print(summary)