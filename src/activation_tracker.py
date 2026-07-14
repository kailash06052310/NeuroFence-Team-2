"""
NeuroFence Project

Module: Activation Tracker

Author: Rohan

Purpose:
Monitor hidden layer activations of the LLM.
"""

class ActivationTracker:

    def __init__(self):
        """Initialize the activation storage."""
        self.activations = []

    def save_activation(self, layer_name, activation):
        """Save activation values."""
        self.activations.append({
            "layer": layer_name,
            "activation": activation
        })

    def get_activations(self):
        """Return all stored activations."""
        return self.activations