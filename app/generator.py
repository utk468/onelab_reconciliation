import pandas as pd
import numpy as np
import os
import random
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def generate_synthetic_data():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    np.random.seed(42)
    random.seed(42)
    
    # 1. Base Transactions
    num_txns = 100
    base_date = datetime(2023, 1, 15)
    
    transactions = []
    settlements = []
    
    for i in range(1, num_txns + 1):
        txn_id = f"T{i:03d}"
        amount = round(random.uniform(10.0, 500.0), 2)
        # Random date around mid Jan
        txn_date = base_date + timedelta(days=random.randint(0, 10))
        
        transactions.append({
            "txn_id": txn_id,
            "amount": amount,
            "date": txn_date.strftime("%Y-%m-%d"),
            "type": "sale"
        })
        
        # Normal settlement is 1-2 days later
        settlement_date = txn_date + timedelta(days=random.randint(1, 2))
        settlements.append({
            "txn_id": txn_id,
            "settled_amount": amount,
            "settlement_date": settlement_date.strftime("%Y-%m-%d")
        })

    # Add Edge Cases
    
    # a) Delayed settlement (cross-month)
    transactions.append({
        "txn_id": "T101", "amount": 150.00, "date": "2023-01-31", "type": "sale"
    })
    settlements.append({
        "txn_id": "T101", "settled_amount": 150.00, "settlement_date": "2023-02-02"
    })

    # b) Duplicate transaction (appears twice in platform)
    transactions.append({
        "txn_id": "T102", "amount": 75.50, "date": "2023-01-20", "type": "sale"
    })
    transactions.append({
        "txn_id": "T102", "amount": 75.50, "date": "2023-01-20", "type": "sale"
    })
    settlements.append({
        "txn_id": "T102", "settled_amount": 75.50, "settlement_date": "2023-01-21"
    })

    # c) Rounding difference
    transactions.append({
        "txn_id": "T103", "amount": 100.55, "date": "2023-01-22", "type": "sale"
    })
    settlements.append({
        "txn_id": "T103", "settled_amount": 100.56, "settlement_date": "2023-01-23"
    })

    # d) Refund without original transaction
    transactions.append({
        "txn_id": "R001", "amount": -50.00, "date": "2023-01-25", "type": "refund"
    })
    # Missing in settlements entirely (maybe a dispute, maybe not settled yet)

    # e) Missing in platform (Extra settlement)
    settlements.append({
        "txn_id": "T104", "settled_amount": 200.00, "settlement_date": "2023-01-26"
    })
    
    # f) Missing in bank (Not settled)
    transactions.append({
        "txn_id": "T105", "amount": 300.00, "date": "2023-01-28", "type": "sale"
    })
    
    df_tx = pd.DataFrame(transactions)
    df_set = pd.DataFrame(settlements)
    
    tx_path = os.path.join(DATA_DIR, "transactions.csv")
    set_path = os.path.join(DATA_DIR, "settlements.csv")
    
    df_tx.to_csv(tx_path, index=False)
    df_set.to_csv(set_path, index=False)
    
    return tx_path, set_path
