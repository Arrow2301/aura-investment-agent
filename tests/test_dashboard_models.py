import unittest
from dashboard.view_models import outcome_summary


class DashboardModelsTests(unittest.TestCase):
    def test_forward_return_summary_ignores_unobserved_outcomes(self):
        rows = [
            {'action': 'WATCH', 'return_5d_pct': 5.0},
            {'action': 'WATCH', 'return_5d_pct': None},
            {'action': 'WATCH', 'return_5d_pct': -1.0},
            {'action': 'AVOID', 'return_5d_pct': None},
        ]
        summary = outcome_summary(rows, 5)
        self.assertEqual(summary.iloc[0]['Action'], 'WATCH')
        self.assertEqual(summary.iloc[0]['Observations'], 2)
        self.assertEqual(summary.iloc[0]['Mean %'], 2.0)
        self.assertTrue(outcome_summary(rows, 20).empty)
