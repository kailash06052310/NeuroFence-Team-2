"""
NeuroFence Project

Module: Activation Tracker

Author: Rohan

Purpose:
Monitor hidden layer activations of the LLM using PyTorch Forward Hooks.
"""


class ActivationTracker:
    """
    Tracks hidden layer activations of a transformer model.
    """

    def __init__(self):
        """
        Initialize activation storage and hook storage.
        """
        self.activations = {}
        self.hooks = []

    def save_activation(self, layer_name, activation):
        """
        Store activation for a layer.

        Parameters:
            layer_name (str): Name of the transformer layer.
            activation: Output tensor from the layer.
        """

        if hasattr(activation, "detach"):
            activation = activation.detach()

        if hasattr(activation, "cpu"):
            activation = activation.cpu()

        self.activations[layer_name] = activation

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

    def hook_fn(self, layer_name):
        """
        Create a forward hook for a transformer layer.

        Parameters:
            layer_name (str): Name of the transformer layer.

        Returns:
            function: Forward hook function.
        """

        def hook(module, input, output):
            # Save activation of current transformer layer
            self.save_activation(layer_name, output)

        return hook

    def register_hooks(self, model):
        """
        Register forward hooks on all transformer blocks.

        Parameters:
            model: Hugging Face transformer model.
        """

        # Remove previous hooks
        self.remove_hooks()

        # Clear previous activations
        self.clear_activations()

        # Safety checks
        if not hasattr(model, "transformer"):
            raise AttributeError(
                "Model does not contain transformer module."
            )

        if not hasattr(model.transformer, "h"):
            raise AttributeError(
                "Transformer blocks not found."
            )

        # Register hooks on every transformer block
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