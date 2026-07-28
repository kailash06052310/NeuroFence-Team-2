import torch
from detection_logic import DetectionLogic
from report_generator import ReportGenerator
from pdf_report import PDFReportGenerator

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

    # Initialize Detection Logic
    detector = DetectionLogic()
    report_generator = ReportGenerator()
    pdf_generator = PDFReportGenerator()

    # -----------------------------
    # STEP 1 : Create Average Baseline
    # -----------------------------

    print("\n========== Creating Average Baseline ==========")

    normal_prompts = fuzzer.get_normal_prompts()[:5]

    baseline_list = []

    for i, prompt in enumerate(normal_prompts, start=1):

        print(f"\nBaseline {i}: {prompt}")

        tracker.clear_activations()

        inputs = tokenizer(prompt, return_tensors="pt")

        with torch.no_grad():
            model(**inputs)

        baseline_activations = tracker.get_all_activations()

        # Store activations instead of prompt
        baseline_list.append(baseline_activations)

    # Create one average baseline
    analyzer.create_average_baseline(baseline_list)

    print("\n✓ Average Baseline Created Successfully.")

    # -----------------------------
    # STEP 2 : Test Adversarial Prompts
    # -----------------------------

    print("\n========== Testing Adversarial Prompts ==========")

    test_prompts = fuzzer.get_adversarial_prompts()[:5]

    for i, test_prompt in enumerate(test_prompts, start=1):

        print(f"\nTest {i}: {test_prompt}")

        tracker.clear_activations()

        inputs = tokenizer(test_prompt, return_tensors="pt")

        with torch.no_grad():
            model(**inputs)

        current_activations = tracker.get_all_activations()

        comparison = analyzer.compare_with_baseline(current_activations)

        report = analyzer.generate_report(comparison)

        print("\nAnalysis Report:")

        for layer, result in report.items():

            print(
                f"{layer} | "
                f"Difference: {result['difference']} | "
                f"Risk: {result['risk']}"
            )

        # -----------------------------
        # STEP 3 : Detection Result
        # -----------------------------

        detection_result = detector.detect(comparison)
        report_generator.add_result(
            prompt=test_prompt,
            comparison=comparison,
            risk_score=detection_result["risk_score"],
            verdict=detection_result["verdict"]
        )

        print("\n========== Detection Result ==========")
        print(f"Risk Score : {detection_result['risk_score']}")
        print(f"Verdict    : {detection_result['verdict']}")
        print("======================================")
    report_generator.save_report()
    pdf_generator.generate()
    # Remove hooks
    tracker.remove_hooks()


if __name__ == "__main__":
    main()