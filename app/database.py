from pymongo import MongoClient
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", os.getenv("MONGO_URI", "mongodb://localhost:27017/"))

class MongoDB:
    def __init__(self):
        try:
            self.client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=2000)
            self.db_name = os.getenv("DATABASE_NAME", "onelab")
            self.db = self.client[self.db_name]
            self.reports_collection = self.db["reports"]
        except Exception as e:
            print(f"Warning: Could not connect to MongoDB: {e}")
            self.reports_collection = None

    def save_report(self, report_data, tx_path=None, set_path=None):
        if self.reports_collection is not None:
            try:
                # Create a copy so we don't inject ObjectId into the returned result
                mongo_doc = report_data.copy()
                
                if tx_path and os.path.exists(tx_path):
                    mongo_doc["transactions_data"] = pd.read_csv(tx_path).to_dict(orient="records")
                    
                if set_path and os.path.exists(set_path):
                    mongo_doc["settlements_data"] = pd.read_csv(set_path).to_dict(orient="records")

                self.reports_collection.insert_one(mongo_doc)
            except Exception as e:
                print(f"Failed to save to MongoDB: {e}")

db_client = MongoDB()
