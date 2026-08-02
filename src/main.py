import torch

from detection_logic import DetectionLogic
from report_generator import ReportGenerator
from pdf_report import PDFReportGenerator

from model_loader import ModelLoader
from fuzzer import PromptFuzzer
from activation_tracker import ActivationTracker
from analyzer import Analyzer


# --------------------------------------------------
# Logging Helper
# --------------------------------------------------

def log(message, log_callback=None):

    if log_callback:
        log_callback(message)

    else:
        print(message)


# --------------------------------------------------
# Main Pipeline
# --------------------------------------------------

def main(
    model=None,
    tokenizer=None,
    log_callback=None
):

    # ------------------------------------
    # Load Model (Only if not already loaded)
    # ------------------------------------

    if model is None or tokenizer is None:

        loader = ModelLoader()
        model, tokenizer = loader.load_model()

        model_name = loader.model_name

    else:

        model_name = "Loaded from GUI"

    log("\n==============================", log_callback)
    log(" NeuroFence", log_callback)
    log("==============================", log_callback)

    log(f"\nModel Loaded : {model_name}", log_callback)

    # ------------------------------------
    # Initialize Components
    # ------------------------------------

    tracker = ActivationTracker()

    tracker.register_hooks(model)

    fuzzer = PromptFuzzer()

    analyzer = Analyzer()

    detector = DetectionLogic()

    report_generator = ReportGenerator()

    pdf_generator = PDFReportGenerator()

    # ------------------------------------
    # STEP 1 : Create Average Baseline
    # ------------------------------------

    log("\n========== Creating Average Baseline ==========", log_callback)

    normal_prompts = fuzzer.get_normal_prompts()[:5]

    baseline_list = []

    for i, prompt in enumerate(normal_prompts, start=1):

        log(f"\nBaseline {i}: {prompt}", log_callback)

        tracker.clear_activations()

        inputs = tokenizer(
            prompt,
            return_tensors="pt"
        )

        with torch.no_grad():
            model(**inputs)

        baseline_activations = tracker.get_all_activations()

        baseline_list.append(
            baseline_activations
        )

    analyzer.create_average_baseline(
        baseline_list
    )

    log(
        "\n✓ Average Baseline Created Successfully.",
        log_callback
    )
        # ------------------------------------
    # STEP 2 : Test Adversarial Prompts
    # ------------------------------------

    log(
        "\n========== Testing Adversarial Prompts ==========",
        log_callback
    )

    test_prompts = fuzzer.get_adversarial_prompts()[:5]

    for i, test_prompt in enumerate(test_prompts, start=1):

        log(f"\nTest {i}: {test_prompt}", log_callback)

        tracker.clear_activations()

        inputs = tokenizer(
            test_prompt,
            return_tensors="pt"
        )

        with torch.no_grad():
            model(**inputs)

        current_activations = tracker.get_all_activations()

        comparison = analyzer.compare_with_baseline(
            current_activations
        )

        report = analyzer.generate_report(
            comparison
        )

        log("\nAnalysis Report:", log_callback)

        for layer, result in report.items():

            log(
                f"{layer} | "
                f"Difference: {result['difference']} | "
                f"Risk: {result['risk']}",
                log_callback
            )

        # ------------------------------------
        # Detection Result
        # ------------------------------------

        detection_result = detector.detect(
            comparison
        )
        report_generator.add_result(
            prompt=test_prompt,
            comparison=comparison,
            risk_score=detection_result["risk_score"],
            verdict=detection_result["verdict"],

            # New Detection Metrics
            confidence_score=detection_result["confidence_score"],
            average_difference=detection_result["average_difference"],
            maximum_difference=detection_result["maximum_difference"],
            high_risk_layers=detection_result["high_risk_layers"],
            total_layers=detection_result["total_layers"],
            high_risk_percentage=detection_result["high_risk_percentage"],
            reason=detection_result["reason"],
            thresholds=detection_result["thresholds"]
)

        log(
            "\n========== Detection Result ==========",
            log_callback
        )

        log(
            f"Risk Score : {detection_result['risk_score']}",
            log_callback
        )

        log(
            f"Verdict    : {detection_result['verdict']}",
            log_callback
        )
        log(
            f"Confidence : {detection_result['confidence_score']}%",
            log_callback
        )

        log(
            f"Avg Diff   : {detection_result['average_difference']}",
            log_callback
        )

        log(
            f"Max Diff   : {detection_result['maximum_difference']}",
            log_callback
        )

        log(
            f"High Layers: "
            f"{detection_result['high_risk_layers']} / "
            f"{detection_result['total_layers']}",
            log_callback
        )

        log(
            f"Reason     : {detection_result['reason']}",
            log_callback
        )
        log(
            "======================================",
            log_callback
        )

    # ------------------------------------
    # Save Reports
    # ------------------------------------

    report_generator.save_report()

    log(
        "\n✓ JSON Report Saved Successfully.",
        log_callback
    )

    pdf_generator.generate()

    log(
        "✓ PDF Report Generated Successfully.",
        log_callback
    )

    # ------------------------------------
    # Cleanup
    # ------------------------------------

    tracker.remove_hooks()

    log(
        "\n✓ NeuroFence Analysis Completed.",
        log_callback
    )


# ------------------------------------
# Run from CLI
# ------------------------------------

if __name__ == "__main__":

    main()