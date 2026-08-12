"""
NeuroFence Project

Module: Neuron Visualizer

Author: Kailash

Purpose:
Generate neuron activation heatmap data and statistics
from hidden layer activations captured by ActivationTracker.

This module is independent of the GUI.
The generated data can be used by main.py and the PyQt6 GUI.
"""

import torch


class NeuronVisualizer:

    def __init__(self):

        # Raw activity score for each layer
        self.raw_scores = {}

        # Normalized activity score for each layer
        self.normalized_scores = {}

        # Heatmap-ready data
        self.heatmap = {}

        # Summary statistics
        self.statistics = {}

        # Activity color categories
        self.color_map = {
            "low": "green",
            "medium": "yellow",
            "high": "orange",
            "critical": "red"
        }

    # --------------------------------------------------
    # Calculate Activity
    # --------------------------------------------------

    def calculate_activity(self, activation):

        if activation is None:
            return 0.0

        # Some transformer modules may return a tuple.
        # Use the first tensor element when necessary.
        if isinstance(activation, (tuple, list)):

            if not activation:
                return 0.0

            activation = activation[0]

        if not isinstance(activation, torch.Tensor):

            activation = torch.tensor(
                activation
            )

        if activation.numel() == 0:
            return 0.0

        return float(
            torch.mean(
                torch.abs(
                    activation
                )
            ).item()
        )

    # --------------------------------------------------
    # Extract Layer Scores
    # --------------------------------------------------

    def extract_layer_scores(self, activations):

        self.raw_scores.clear()

        if not activations:
            return self.raw_scores

        for layer_name, activation in activations.items():

            score = self.calculate_activity(
                activation
            )

            self.raw_scores[layer_name] = score

        return self.raw_scores

    # --------------------------------------------------
    # Normalize Scores
    # --------------------------------------------------

    def normalize_scores(self):

        self.normalized_scores.clear()

        if not self.raw_scores:
            return self.normalized_scores

        maximum = max(
            self.raw_scores.values()
        )

        if maximum == 0:
            maximum = 1.0

        for layer_name, value in self.raw_scores.items():

            normalized = round(
                value / maximum,
                4
            )

            self.normalized_scores[
                layer_name
            ] = normalized

        return self.normalized_scores

    # --------------------------------------------------
    # Get Activity Color
    # --------------------------------------------------

    def get_color(self, value):

        if value < 0.25:
            return self.color_map["low"]

        if value < 0.50:
            return self.color_map["medium"]

        if value < 0.75:
            return self.color_map["high"]

        return self.color_map["critical"]

    # --------------------------------------------------
    # Generate Heatmap
    # --------------------------------------------------

    def generate_heatmap(self, activations):

        self.extract_layer_scores(
            activations
        )

        self.normalize_scores()

        self.heatmap.clear()

        for layer_name in self.raw_scores:

            raw_activity = round(
                self.raw_scores[layer_name],
                6
            )

            normalized_activity = (
                self.normalized_scores[layer_name]
            )

            self.heatmap[layer_name] = {

                "raw_activity":
                    raw_activity,

                "normalized_activity":
                    normalized_activity,

                "color":
                    self.get_color(
                        normalized_activity
                    )
            }

        return self.heatmap

    # --------------------------------------------------
    # Generate Statistics
    # --------------------------------------------------

    def generate_statistics(self):

        self.statistics.clear()

        if not self.normalized_scores:
            return self.statistics

        values = list(
            self.normalized_scores.values()
        )

        layers = list(
            self.normalized_scores.keys()
        )

        highest_layer = max(
            self.normalized_scores,
            key=self.normalized_scores.get
        )

        lowest_layer = min(
            self.normalized_scores,
            key=self.normalized_scores.get
        )

        average_activity = (
            sum(values) / len(values)
        )

        maximum_activity = max(values)
        minimum_activity = min(values)

        high_risk_layers = [
            layer
            for layer, value
            in self.normalized_scores.items()
            if value >= 0.75
        ]

        suspicious_layers = [
            layer
            for layer, value
            in self.normalized_scores.items()
            if 0.50 <= value < 0.75
        ]

        safe_layers = [
            layer
            for layer, value
            in self.normalized_scores.items()
            if value < 0.50
        ]

        self.statistics = {

            "total_layers":
                len(layers),

            "highest_layer":
                highest_layer,

            "highest_activity":
                round(
                    self.normalized_scores[
                        highest_layer
                    ],
                    4
                ),

            "lowest_layer":
                lowest_layer,

            "lowest_activity":
                round(
                    self.normalized_scores[
                        lowest_layer
                    ],
                    4
                ),

            "average_activity":
                round(
                    average_activity,
                    4
                ),

            "maximum_activity":
                round(
                    maximum_activity,
                    4
                ),

            "minimum_activity":
                round(
                    minimum_activity,
                    4
                ),

            "high_risk_layers":
                len(high_risk_layers),

            "suspicious_layers":
                len(suspicious_layers),

            "safe_layers":
                len(safe_layers),

            "high_risk_layer_names":
                high_risk_layers,

            "suspicious_layer_names":
                suspicious_layers,

            "safe_layer_names":
                safe_layers
        }

        return self.statistics

    # --------------------------------------------------
    # COMPLETE ANALYSIS
    # --------------------------------------------------

    def analyze(self, activations):

        heatmap = self.generate_heatmap(
            activations
        )

        statistics = self.generate_statistics()

        return {

            "heatmap":
                heatmap,

            "statistics":
                statistics,

            "table_data":
                self.get_table_data(),

            "summary":
                self.generate_summary()
        }

    # --------------------------------------------------
    # Heatmap Table Data
    # --------------------------------------------------

    def get_table_data(self):

        table = []

        if not self.heatmap:
            return table

        for layer_name, data in self.heatmap.items():

            table.append({

                "layer":
                    layer_name,

                "raw_activity":
                    data["raw_activity"],

                "normalized_activity":
                    data["normalized_activity"],

                "color":
                    data["color"]
            })

        return table

    # --------------------------------------------------
    # Backward-Compatible Table Rows
    # --------------------------------------------------

    def get_table_rows(self):

        rows = []

        for layer_name, data in self.heatmap.items():

            rows.append([
                layer_name,
                data["normalized_activity"],
                data["color"]
            ])

        return rows

    # --------------------------------------------------
    # High Risk Layers
    # --------------------------------------------------

    def get_high_risk_layers(self):

        return [

            layer

            for layer, value
            in self.normalized_scores.items()

            if value >= 0.75
        ]

    # --------------------------------------------------
    # Layer Ranking
    # --------------------------------------------------

    def get_layer_ranking(self):

        return sorted(

            self.normalized_scores.items(),

            key=lambda item: item[1],

            reverse=True
        )

    # --------------------------------------------------
    # Generate Summary
    # --------------------------------------------------

    def generate_summary(self):

        if not self.statistics:

            self.generate_statistics()

        if not self.statistics:
            return {}

        return {

            "total_layers":
                self.statistics[
                    "total_layers"
                ],

            "average_activity":
                self.statistics[
                    "average_activity"
                ],

            "highest_layer":
                self.statistics[
                    "highest_layer"
                ],

            "highest_activity":
                self.statistics[
                    "highest_activity"
                ],

            "high_risk_layers":
                self.statistics[
                    "high_risk_layers"
                ]
        }

    # --------------------------------------------------
    # Export Heatmap
    # --------------------------------------------------

    def export_heatmap(self):

        return self.heatmap

    # --------------------------------------------------
    # Export Statistics
    # --------------------------------------------------

    def export_statistics(self):

        return self.statistics