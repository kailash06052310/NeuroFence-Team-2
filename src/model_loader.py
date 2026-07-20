"""
NeuroFence Project

Module: Model Loader

Author: Kailash

Purpose:
Load a Hugging Face language model and tokenizer.
"""

from transformers import AutoTokenizer, AutoModelForCausalLM


class ModelLoader:
    def __init__(self, model_name="distilgpt2"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None

    def load_model(self):
        print(f"Loading model: {self.model_name}")

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name)

        print("Model loaded successfully!")

        return self.model, self.tokenizer