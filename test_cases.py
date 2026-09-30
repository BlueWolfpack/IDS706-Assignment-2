"""Unit tests for the reusable Agrofood analysis functions. Written by AI"""

import unittest
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import fxns_for_ACE as fxn


class TestAnalysisFunctions(unittest.TestCase):
    def test_load_data(self):
        fixture_path = Path(__file__).with_name("test.csv")

        result = fxn.load_data(fixture_path)

        self.assertEqual(list(result.columns), ["Letters", "Integers", "Floats"])
        self.assertEqual(len(result), 5)

    def test_preprocess_data_coerces_non_area_columns_without_mutating_input(self):
        """edge case where one entry is not a number.
        Asserts that value is stored as na"""
        source = pd.DataFrame(
            {
                "Area": ["A", "B"],
                "Year": ["2000", "not a year"],
                "total_emission": ["1.5", "2.5"],
            }
        )

        result = fxn.preprocess_data(source)

        self.assertEqual(result["Area"].tolist(), ["A", "B"])
        self.assertEqual(result["Year"].iloc[0], 2000)
        self.assertTrue(pd.isna(result["Year"].iloc[1]))
        self.assertEqual(result["total_emission"].tolist(), [1.5, 2.5])
        self.assertEqual(source["Year"].tolist(), ["2000", "not a year"])

    def test_new_df_keeps_requested_columns_and_adds_empty_column(self):
        """Test for new_df that checks that specified columns are kept/added"""
        source = pd.DataFrame({"keep": [1, 2], "drop": [3, 4]})

        result = fxn.new_df(source, ["keep"], "new")

        self.assertEqual(list(result.columns), ["keep", "new"])
        self.assertTrue(result["new"].isna().all())
        self.assertNotIn("new", source.columns)

    def test_add_columns_sums_values_without_mutating_destination(self):
        source = pd.DataFrame({"first": [1, -2], "second": [3.5, 4.0]})
        destination = pd.DataFrame({"label": ["a", "b"]})

        result = fxn.add_columns(source, destination, "first", "second", "sum")

        self.assertEqual(result["sum"].tolist(), [4.5, 2.0])
        self.assertNotIn("sum", destination.columns)

    def test_create_fire_features_sums_fire_columns(self):
        """Tests that create_fire_features is able to subset the appropriate columns"""
        source = pd.DataFrame(
            {
                "Area": ["A", "B"],
                "Year": [2000, 2001],
                "total_emission": [10.0, 20.0],
                "Forestland": [100, 200],
                "Forest fires": [1.5, 0.0],
                "Fires in humid tropical forests": [2.5, 3.0],
                "unused": [99, 99],
            }
        )

        result = fxn.create_fire_features(source)

        self.assertEqual(
            list(result.columns),
            ["Area", "Year", "total_emission", "Forestland", "total_fires"],
        )
        self.assertEqual(result["total_fires"].tolist(), [4.0, 3.0])
        self.assertNotIn("unused", result.columns)

    def test_create_population_features_calculates_population_and_ratio(self):
        source = pd.DataFrame(
            {
                "Area": ["A", "B"],
                "Year": [2000, 2001],
                "total_emission": [10.0, 20.0],
                "Total Population - Male": [40, 0],
                "Total Population - Female": [60, 0],
                "Urban population": [30, 0],
                "Rural population": [10, 0],
            }
        )

        result = fxn.create_population_features(source)

        self.assertEqual(result["total_population"].tolist(), [100, 0])
        self.assertEqual(result["urban_to_rural"].iloc[0], 3.0)
        self.assertTrue(np.isnan(result["urban_to_rural"].iloc[1]))

    def test_train_and_evaluate_models_returns_four_metrics_per_predictor(self):
        signal = np.arange(12, dtype=float)
        source = pd.DataFrame(
            {
                "Area": ["A"] * len(signal),
                "Year": np.arange(2000, 2000 + len(signal)),
                "total_emission": signal**2 + signal,
                "signal": signal,
                "constant": np.ones(len(signal)),
            }
        )

        result = fxn.train_and_evaluate_models(source)

        self.assertEqual(len(result), 4)
        self.assertEqual(set(result["predictor"]), {"signal"})
        self.assertEqual(
            set(result["model"]),
            {"linear", "polynomial_degree_2", "polynomial_degree_3", "random_forest"},
        )
        self.assertTrue(np.isfinite(result[["MAE", "RMSE", "R2"]].to_numpy()).all())

    def test_select_best_models_chooses_lowest_rmse_per_group(self):
        results = pd.DataFrame(
            {
                "Area": ["A", "A", "A", "B"],
                "predictor": ["x", "x", "y", "x"],
                "model": ["linear", "random_forest", "linear", "linear"],
                "RMSE": [2.0, 1.0, 3.0, 4.0],
            }
        )

        selected = fxn.select_best_models(results)

        self.assertEqual(len(selected), 3)
        self.assertEqual(
            selected.loc[
                (selected["Area"] == "A") & (selected["predictor"] == "x"), "model"
            ].item(),
            "random_forest",
        )

    def test_plot_fire_emissions_sets_labels_and_plots_selected_area(self):
        fire_data = pd.DataFrame(
            {
                "Area": ["A", "A", "B"],
                "Year": [2000, 2001, 2000],
                "total_fires": [1.0, 2.0, 99.0],
                "total_emission": [10.0, 20.0, 99.0],
            }
        )

        axis = fxn.plot_fire_emissions(fire_data, "A")
        self.addCleanup(plt.close, axis.figure)

        self.assertEqual(axis.get_xlabel(), "Year")
        self.assertEqual(axis.get_ylabel(), "Total Fires")
        self.assertEqual(axis.right_ax.get_ylabel(), "Total Emission")
        self.assertEqual(len(axis.lines[0].get_xdata()), 2)

    def test_plot_population_ratio_filters_data_and_sets_labels(self):
        population_data = pd.DataFrame(
            {"urban_to_rural": [1.0, 2.0, 250.0], "total_emission": [10.0, 20.0, 30.0]}
        )

        figure, axis = fxn.plot_population_ratio(population_data, max_ratio=200)
        self.addCleanup(plt.close, figure)

        self.assertEqual(axis.get_xlabel(), "Urban-to-rural population ratio < 200")
        self.assertEqual(axis.get_ylabel(), "Total emissions")
        self.assertEqual(
            axis.get_title(), "Density of Urban-to-Rural Ratio vs. Total Emissions"
        )
        self.assertEqual(len(axis.collections), 1)


if __name__ == "__main__":
    unittest.main()
