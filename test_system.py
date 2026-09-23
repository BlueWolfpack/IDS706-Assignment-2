"""End-to-end system tests for assignment_2_ntbk.py."""

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import assignment_2_ntbk


class TestAssignmentWorkflow(unittest.TestCase):
    """Verify that the complete analysis workflow runs successfully."""
    # I have no idea what @patch does
    @patch("assignment_2_ntbk.plt.show")
    def test_main_runs_complete_workflow(self, show_mock):
        output = io.StringIO()
        # Japan_Agrofood_co2_emission.csv used to reduce testing runtime
        fixture_path = Path(__file__).with_name(
            "Japan_Agrofood_co2_emission.csv" 
        )

        with redirect_stdout(output):
            assignment_2_ntbk.main(fixture_path)

        printed_output = output.getvalue()
        self.assertIn("Best models by area and predictor:", printed_output)
        self.assertIn("Best models sorted by R2:", printed_output)
        self.assertEqual(show_mock.call_count, 3)


if __name__ == "__main__":
    unittest.main()
