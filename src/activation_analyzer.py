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