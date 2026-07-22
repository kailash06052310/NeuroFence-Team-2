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

    print("\n========== Creating Baselines ==========")

    normal_prompts = fuzzer.get_normal_prompts()[:5]

    baseline_list = []

    for i, prompt in enumerate(normal_prompts, start=1):

        print(f"\nBaseline {i}: {prompt}")

        tracker.clear_activations()

        inputs = tokenizer(prompt, return_tensors="pt")

        with torch.no_grad():
            model(**inputs)

        baseline_activations = tracker.get_all_activations()

        analyzer.create_baseline(baseline_activations)

        baseline_list.append(prompt)

    print("\n✓ 5 Baseline Prompts Processed Successfully.")

    # -----------------------------
    # STEP 2 : Test Another Prompt
    # -----------------------------

    print("\n========== Testing Adversarial Prompts ==========")

    test_prompts = fuzzer.get_adversarial_prompts()[:5]

    for i, test_prompt in enumerate(test_prompts, start=1):

        print(f"\nTest {i}: {test_prompt}")

        tracker.clear_activations()

        inputs = tokenizer(test_prompt, return_tensors="pt")

        with torch.no_grad():
            outputs = model(**inputs)

        current_activations = tracker.get_all_activations()

        comparison = analyzer.compare_with_baseline(current_activations)

        report = analyzer.generate_report(comparison)

        print("Analysis Report:")

        for layer, result in report.items():

            print(
                f"{layer} | "
                f"Difference: {result['difference']} | "
                f"Risk: {result['risk']}"
            )

        print("------------------------------------")
    # Remove hooks
    tracker.remove_hooks()


if __name__ == "__main__":
    main()