"""
NeuroFence Project

Module: Activation Tracker

Author: Rohan

Purpose:
Monitor hidden layer activations of the LLM.
"""

class ActivationTracker:

    def __init__(self):
        """Initialize activation storage."""
        self.activations = {}

    def save_activation(self, layer_name, activation):
        """Store activation for a layer."""
        self.activations[layer_name] = activation

    def get_activation(self, layer_name):
        """Return activation of a specific layer."""
        return self.activations.get(layer_name)

    def get_all_activations(self):
        """Return all stored activations."""
        return self.activations
    
    def clear_activations(self):
        """Remove all stored activations."""
        self.activations.clear()