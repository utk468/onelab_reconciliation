import pandas as pd
import os
import unittest
from app.reconciler import reconcile_data

# Create a temporary test dir
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")
if not os.path.exists(TEST_DATA_DIR):
    os.makedirs(TEST_DATA_DIR)

class TestReconciler(unittest.TestCase):
    
    def setUp(self):
        # Create mock data
        self.tx_path = os.path.join(TEST_DATA_DIR, "mock_tx.csv")
        self.set_path = os.path.join(TEST_DATA_DIR, "mock_set.csv")
        
        tx_data = [
            {"txn_id": "T1", "amount": 100.0, "date": "2023-01-01", "type": "sale"},
            {"txn_id": "T2", "amount": 200.0, "date": "2023-01-02", "type": "sale"},
            {"txn_id": "T2", "amount": 200.0, "date": "2023-01-02", "type": "sale"}, # Duplicate
            {"txn_id": "T3", "amount": 300.0, "date": "2023-01-31", "type": "sale"}, # Delayed
            {"txn_id": "R1", "amount": -50.0, "date": "2023-01-10", "type": "refund"}, # Refund Inconsistency
            {"txn_id": "T4", "amount": 400.0, "date": "2023-01-15", "type": "sale"} # Missing settlement
        ]
        
        set_data = [
            {"txn_id": "T1", "settled_amount": 100.0, "settlement_date": "2023-01-02"},
            {"txn_id": "T2", "settled_amount": 200.0, "settlement_date": "2023-01-03"},
            {"txn_id": "T3", "settled_amount": 300.0, "settlement_date": "2023-02-01"}, # Delayed
            {"txn_id": "T5", "settled_amount": 500.0, "settlement_date": "2023-01-20"} # Extra settlement
        ]
        
        pd.DataFrame(tx_data).to_csv(self.tx_path, index=False)
        pd.DataFrame(set_data).to_csv(self.set_path, index=False)

    def tearDown(self):
        if os.path.exists(self.tx_path):
            os.remove(self.tx_path)
        if os.path.exists(self.set_path):
            os.remove(self.set_path)

    def test_reconciliation_logic(self):
        result = reconcile_data(self.tx_path, self.set_path)
        issues = result["issues"]
        
        issue_types = {i["issue_type"]: i for i in issues}
        
        self.assertIn("Duplicate Transaction", issue_types)
        self.assertEqual(issue_types["Duplicate Transaction"]["txn_id"], "T2")
        
        self.assertIn("Delayed Settlement", issue_types)
        self.assertEqual(issue_types["Delayed Settlement"]["txn_id"], "T3")
        
        self.assertIn("Refund Inconsistency", issue_types)
        self.assertEqual(issue_types["Refund Inconsistency"]["txn_id"], "R1")
        
        self.assertIn("Missing Settlement", issue_types)
        self.assertEqual(issue_types["Missing Settlement"]["txn_id"], "T4")
        
        self.assertIn("Extra Settlement", issue_types)
        self.assertEqual(issue_types["Extra Settlement"]["txn_id"], "T5")

if __name__ == '__main__':
    unittest.main()
