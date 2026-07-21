import torch

from model_loader import ModelLoader
from fuzzer import PromptFuzzer
from activation_tracker import ActivationTracker
from analyzer import Analyzer


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

    # Initialize Analyzer
    analyzer = Analyzer()

    # -----------------------------
    # STEP 1 : Create Baseline
    # -----------------------------

    baseline_prompt = fuzzer.get_normal_prompts()[0]

    print("\nCreating Baseline...")
    print(f"Prompt: {baseline_prompt}")

    tracker.clear_activations()

    inputs = tokenizer(baseline_prompt, return_tensors="pt")

    with torch.no_grad():
        model(**inputs)

    baseline_activations = tracker.get_all_activations()

    analyzer.create_baseline(baseline_activations)

    print("✓ Baseline Created Successfully.")

    # -----------------------------
    # STEP 2 : Test Another Prompt
    # -----------------------------

    test_prompt = fuzzer.get_adversarial_prompts()[0]

    print(f"\nTesting Prompt:\n{test_prompt}")

    tracker.clear_activations()

    inputs = tokenizer(test_prompt, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)

    print("\n✓ Model executed successfully.")
    print("Logits Shape:", outputs.logits.shape)

    current_activations = tracker.get_all_activations()

    # -----------------------------
    # STEP 3 : Compare Activations
    # -----------------------------

    comparison = analyzer.compare_with_baseline(
        current_activations
    )

    report = analyzer.generate_report(comparison)

    print("\n========== Analysis Report ==========")

    for layer, result in report.items():

        print(
            f"{layer} | "
            f"Difference: {result['difference']} | "
            f"Risk: {result['risk']}"
        )

    print("=====================================")

    # Remove hooks
    tracker.remove_hooks()


if __name__ == "__main__":
    main()