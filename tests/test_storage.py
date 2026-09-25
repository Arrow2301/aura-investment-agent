import unittest
from unittest.mock import MagicMock, patch

from database.supabase_client import save_signal


class StorageTests(unittest.TestCase):
    @patch("database.supabase_client.get_client")
    def test_daily_signal_is_upserted_for_repeatable_runs(self, get_client):
        client = MagicMock()
        get_client.return_value = client
        result = {"symbol": "TEST.NS", "technical": {"score": 60, "signals": []},
                  "fundamental": {"score": 60}, "quality": {"score": 60},
                  "risk": {"score": 50, "eligible": False},
                  "aura": {"aura_score": 58, "action": "AVOID", "confidence": 58}, "explanation": "test"}
        save_signal(result)
        _, kwargs = client.table.return_value.upsert.call_args
        self.assertEqual(kwargs["on_conflict"], "symbol,analysis_date")
        self.assertIn("analysis_date", client.table.return_value.upsert.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
