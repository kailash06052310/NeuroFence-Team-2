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
        self.hooks = []

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

    def register_hooks(self, model):
        """
        Register forward hooks on all transformer blocks.
        """
    
        # Remove old hooks
        self.remove_hooks()

        # Clear previous activations
        self.clear_activations()

        for index, block in enumerate(model.transformer.h):

            layer_name = f"Layer_{index}"

            handle = block.register_forward_hook(
                self.hook_fn(layer_name)
            )

            self.hooks.append(handle)

        print(f"Registered {len(self.hooks)} hooks successfully.")

    def remove_hooks(self):
        """
        Remove all registered hooks.
        """

        for hook in self.hooks:
            hook.remove()

        self.hooks.clear()