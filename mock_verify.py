import unittest
from alogram_payrisk.testing import MockRiskClient

class TestMockRiskClient(unittest.TestCase):
    def test_mock_behavior(self):
        # Use lowercase as required by the Python Enum/Validator
        mock = MockRiskClient(default_decision="approve")
        
        # Test Default
        resp = mock.check_risk({"test": "data"})
        self.assertEqual(resp.decision, "approve")
        
        # Test Queued
        mock.queue_decision("decline", 0.95, "high_risk")
        resp2 = mock.check_risk({"test": "data"})
        self.assertEqual(resp2.decision, "decline")
        self.assertAlmostEqual(resp2.fraud_score.score, 0.95)
        
        # Test Call Count
        self.assertEqual(mock.call_count, 2)

if __name__ == "__main__":
    unittest.main()
