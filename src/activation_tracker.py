"""
NeuroFence Project

Module: Activation Tracker

Author: Rohan

Purpose:
Monitor hidden layer activations of the LLM using PyTorch Forward Hooks.
"""

import torch


class ActivationTracker:

    def __init__(self):
        """
        Initialize activation storage and hook storage.
        """
        self.activations = {}
        self.hooks = []

    def hook_fn(self, layer_name):
        """
        Create a forward hook for a transformer layer.

        Parameters:
            layer_name (str): Name of the transformer layer.

        Returns:
            function: Forward hook function.
        """

        def hook(module, input, output):
            """
            Automatically called whenever the layer performs
            a forward pass.
            """

            # Save activation on CPU to reduce GPU memory usage
            self.activations[layer_name] = output.detach().cpu()

        return hook

    def register_hooks(self, model):
        """
        Register hooks on every transformer block of DistilGPT2.

        Parameters:
            model: Hugging Face GPT2 model.
        """

        # Remove old hooks if they exist
        self.remove_hooks()

        # Clear previous activations
        self.clear_activations()

        # Safety check
        if not hasattr(model, "transformer"):
            raise AttributeError(
                "Model does not contain a transformer module."
            )

        if not hasattr(model.transformer, "h"):
            raise AttributeError(
                "Transformer blocks not found."
            )

        # Register hook on every GPT2 block
        for index, block in enumerate(model.transformer.h):

            layer_name = f"Layer_{index}"

            handle = block.register_forward_hook(
                self.hook_fn(layer_name)
            )

            self.hooks.append(handle)

        print(f"✓ Registered {len(self.hooks)} activation hooks.")

    def remove_hooks(self):
        """
        Remove all registered forward hooks.
        """

        for hook in self.hooks:
            hook.remove()

        self.hooks.clear()

        print("✓ All hooks removed.")

    def save_activation(self, layer_name, activation):
        """
        Manually store activation for a layer.

        Parameters:
            layer_name (str): Layer name.
            activation (Tensor): Activation tensor.
        """
        self.activations[layer_name] = activation.detach().cpu()

    def get_activation(self, layer_name):
        """
        Return activation of a specific layer.

        Parameters:
            layer_name (str): Layer name.

        Returns:
            Tensor or None
        """
        return self.activations.get(layer_name)

    def get_all_activations(self):
        """
        Return all captured activations.

        Returns:
            dict
        """
        return self.activations

    def clear_activations(self):
        """
        Remove all stored activations.
        """
        self.activations.clear()