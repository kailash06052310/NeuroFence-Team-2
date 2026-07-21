"""
NeuroFence Project

Module: Analyzer

Author: Kailash

Purpose:
Analyze neuron activations and compare them with a baseline.
"""

import torch


class Analyzer:

    def __init__(self):
        """
        Initialize baseline storage.
        """
        self.baseline = {}

    def create_baseline(self, activations):
        """
        Store baseline activations.

        Parameters:
            activations (dict): Dictionary received from
                                ActivationTracker.
        """

        self.baseline.clear()

        for layer_name, activation in activations.items():

            # Some models return tuple outputs
            if isinstance(activation, tuple):
                activation = activation[0]

            # Store a copy so future changes don't affect baseline
            self.baseline[layer_name] = activation.clone()

        print(f"✓ Baseline created for {len(self.baseline)} layers.")

    def has_baseline(self):
        """
        Check whether a baseline exists.

        Returns:
            bool
        """
        return len(self.baseline) > 0

    def get_baseline(self):
        """
        Return stored baseline activations.

        Returns:
            dict
        """
        return self.baseline
    def calculate_difference(self, baseline_activation, current_activation):
        """
        Calculate the mean absolute difference between
        baseline and current activations.

        Parameters:
            baseline_activation (Tensor)
            current_activation (Tensor)

        Returns:
            float
        """

        if isinstance(baseline_activation, tuple):
            baseline_activation = baseline_activation[0]

        if isinstance(current_activation, tuple):
            current_activation = current_activation[0]

        difference = torch.mean(
            torch.abs(current_activation - baseline_activation)
        )

        return difference.item()

    def compare_with_baseline(self, current_activations):
        """
        Compare current activations with the stored baseline.

        Parameters:
            current_activations (dict)

        Returns:
            dict
        """

        if not self.has_baseline():
            raise ValueError(
                "Baseline has not been created."
            )

        results = {}

        for layer_name in self.baseline:

            if layer_name not in current_activations:
                continue

            diff = self.calculate_difference(
                self.baseline[layer_name],
                current_activations[layer_name]
            )

            results[layer_name] = diff

        return results

    def get_risk_level(self, score):
        """
        Convert difference score into a risk level.

        Parameters:
            score (float)

        Returns:
            str
        """

        if score < 0.05:
            return "Normal"

        elif score < 0.20:
            return "Suspicious"

        else:
            return "High Risk"

    def generate_report(self, comparison_results):
        """
        Generate a readable analysis report.

        Parameters:
            comparison_results (dict)

        Returns:
            dict
        """

        report = {}

        for layer_name, score in comparison_results.items():

            report[layer_name] = {
                "difference": round(score, 6),
                "risk": self.get_risk_level(score)
            }

        return report