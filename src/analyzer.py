"""
NeuroFence Analyzer
Normalized activation comparison against a multi-prompt normal baseline.
"""
import torch


class Analyzer:

    def __init__(self):
        self.baseline = {}
        self.baseline_mean = {}
        self.baseline_std = {}

    def _tensor(self, activation):
        if isinstance(activation, tuple):
            activation = activation[0]
        return activation

    def _activity(self, activation):
        activation = self._tensor(activation)
        return float(torch.mean(torch.abs(activation)).item())

    def create_baseline(self, activations):
        self.baseline.clear()
        self.baseline_mean.clear()
        self.baseline_std.clear()

        for name, activation in activations.items():
            activation = self._tensor(activation)
            self.baseline[name] = activation.clone()
            self.baseline_mean[name] = self._activity(activation)
            self.baseline_std[name] = 0.0

        print(f"✓ Baseline created for {len(self.baseline)} layers.")

    def create_average_baseline(self, baseline_list):
        self.baseline.clear()
        self.baseline_mean.clear()
        self.baseline_std.clear()

        if not baseline_list:
            return

        for name in baseline_list[0].keys():
            tensors = []
            values = []

            for data in baseline_list:
                if name not in data:
                    continue
                activation = self._tensor(data[name])
                tensors.append(activation)
                values.append(self._activity(activation))

            if not tensors:
                continue

            min_length = min(x.shape[1] for x in tensors)
            trimmed = [x[:, :min_length, :] for x in tensors]

            self.baseline[name] = torch.mean(
                torch.stack(trimmed), dim=0
            ).clone()

            value_tensor = torch.tensor(values, dtype=torch.float32)
            self.baseline_mean[name] = float(
                torch.mean(value_tensor).item()
            )
            self.baseline_std[name] = float(
                torch.std(value_tensor, unbiased=False).item()
            )

        print(
            f"✓ Average baseline created using "
            f"{len(baseline_list)} prompts."
        )

    def has_baseline(self):
        return len(self.baseline) > 0

    def get_baseline(self):
        return self.baseline

    def calculate_difference(self, baseline_activation, current_activation):
        baseline_activation = self._tensor(baseline_activation)
        current_activation = self._tensor(current_activation)

        min_length = min(
            baseline_activation.shape[1],
            current_activation.shape[1]
        )

        baseline_activation = baseline_activation[:, :min_length, :]
        current_activation = current_activation[:, :min_length, :]

        return torch.mean(
            torch.abs(current_activation - baseline_activation)
        ).item()

    def compare_with_baseline(self, current_activations):
        if not self.has_baseline():
            raise ValueError("Baseline has not been created.")

        results = {}

        for name in self.baseline:
            if name not in current_activations:
                continue

            current = self._activity(current_activations[name])
            mean = self.baseline_mean.get(
                name, self._activity(self.baseline[name])
            )
            std = self.baseline_std.get(name, 0.0)

            relative = abs(current - mean) / max(abs(mean), 1e-6)

            if std > 1e-6:
                z = abs(current - mean) / std
                score = min(
                    (relative * 0.5) +
                    (min(z, 6.0) / 6.0 * 0.5),
                    1.0
                )
            else:
                score = min(relative, 1.0)

            results[name] = float(score)

        return results

    def get_risk_level(self, score):
        if score < 0.20:
            return "Normal"
        if score < 0.50:
            return "Suspicious"
        return "High Risk"

    def generate_report(self, comparison_results):
        return {
            name: {
                "difference": round(score, 6),
                "risk": self.get_risk_level(score)
            }
            for name, score in comparison_results.items()
        }