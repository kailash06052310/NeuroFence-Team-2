import torch

from model_loader import ModelLoader
from fuzzer import PromptFuzzer
from activation_tracker import ActivationTracker


def main():

    # Load model
    loader = ModelLoader()
    model, tokenizer = loader.load_model()

    print("\n==============================")
    print(" NeuroFence")
    print("==============================")

    print(f"\nModel Loaded : {loader.model_name}")

    # Initialize Activation Tracker
    tracker = ActivationTracker()

    # Register hooks
    tracker.register_hooks(model)

    # Initialize Prompt Fuzzer
    fuzzer = PromptFuzzer()

    # Select first normal prompt
    prompt = fuzzer.get_normal_prompts()[0]

    print(f"\nTesting Prompt:\n{prompt}")

    # Tokenize prompt
    inputs = tokenizer(prompt, return_tensors="pt")

    # Run inference
    with torch.no_grad():
        outputs = model(**inputs)

    print("\n✓ Model executed successfully.")
    print("Logits Shape:", outputs.logits.shape)

    # Display captured activations
    print("\nCaptured Activations")
    print("----------------------")

    activations = tracker.get_all_activations()

    if len(activations) == 0:
        print("No activations captured.")

    else:
        for layer_name, activation in activations.items():

            # Some HuggingFace models return tuple outputs
            if isinstance(activation, tuple):
                activation = activation[0]

            if hasattr(activation, "shape"):
                print(f"{layer_name} -> {activation.shape}")
            else:
                print(f"{layer_name} -> {type(activation)}")

    # Remove hooks
    tracker.remove_hooks()


if __name__ == "__main__":
    main()